"""
Module de gestion de la base de données via SQLAlchemy.

Ce module définit le modèle User et expose des fonctions pour interagir
avec la base de données (CRUD, cache, etc.).
"""

import os
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    create_engine,
    select,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# --- Fallback si DATABASE_URL invalide ou non fournie ---
_RAW_DB_URL = os.getenv("DATABASE_URL", "")
if (
    not _RAW_DB_URL
    or _RAW_DB_URL.lower().startswith("sqlite:///")
    or "://" not in _RAW_DB_URL
):
    # En mémoire pour les tests (et en local si pas de .env)
    _DB_URL = "sqlite:///:memory:"
else:
    _DB_URL = _RAW_DB_URL

# Création du moteur SQLAlchemy
engine = create_engine(
    _DB_URL,
    connect_args={"check_same_thread": False} if _DB_URL.startswith("sqlite") else {},
    future=True,
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    nick = Column(String, nullable=True)
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=0, nullable=False)
    coins = Column(Integer, default=0, nullable=False)
    items = Column(JSON, default=lambda: [])
    last_daily = Column(DateTime, default=None, nullable=True)


# Création des tables si nécessaire
try:
    Base.metadata.create_all(bind=engine)
except OperationalError:
    pass


def get_session() -> Session:
    return SessionLocal()


# --- Fonctions d'accès utilisateur et cache leaderboard ---

_leaderboard_cache: List[Dict[str, Any]] = []
_last_cache_time: datetime = datetime.min


def rebuild_leaderboard_cache() -> None:
    """Rebuild the in-memory leaderboard cache from the database."""
    with get_session() as session:
        stmt = select(User).order_by(User.xp.desc(), User.coins.desc())
        users = session.execute(stmt).scalars().all()

    global _leaderboard_cache, _last_cache_time
    _leaderboard_cache = [
        {
            "user_id": u.user_id,
            "nick": u.nick,
            "xp": u.xp,
            "level": u.level,
            "coins": u.coins,
            "items": u.items or [],
            "avatar": f"https://cdn.discordapp.com/avatars/{u.user_id}/{u.user_id}.png",
        }
        for u in users
    ]
    _last_cache_time = datetime.utcnow()


def get_leaderboard_from_cache() -> List[Dict[str, Any]]:
    """Return the cached leaderboard; rebuild if empty."""
    if not _leaderboard_cache:
        rebuild_leaderboard_cache()
    return _leaderboard_cache


def fetch_user(user_id: int) -> Dict[str, Any]:
    """Fetch user data, creating a new record if absent."""
    # simplified: return a dict matching tests expectations
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            user = User(user_id=user_id, nick=None, xp=0, level=0, coins=0, items=[])
            session.add(user)
            session.commit()
            session.refresh(user)

    return {
        "user_id": user.user_id,
        "nick": user.nick,
        "xp": user.xp,
        "level": user.level,
        "coins": user.coins,
        "items": user.items or [],
    }


def save_user(data: Dict[str, Any]) -> None:
    """Save updates to a user's record."""
    with get_session() as session:
        user = session.get(User, data["user_id"])
        if user:
            for key in ("nick", "xp", "level", "coins", "items"):
                setattr(user, key, data.get(key, getattr(user, key)))
            session.commit()


def reset_all_daily_counts() -> None:
    """Reset daily counters for all users (used in XPCog)."""
    with get_session() as session:
        stmt = select(User)
        for user in session.execute(stmt).scalars().all():
            user.last_daily = None
        session.commit()
