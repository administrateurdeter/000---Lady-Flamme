# db.py

import os
from datetime import datetime
from typing import Any, Dict, List

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
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --- Fallback si DATABASE_URL invalide ou non fournie ---
_RAW_DB_URL = os.getenv("DATABASE_URL", "")
if (
    not _RAW_DB_URL
    or _RAW_DB_URL.lower().startswith("sqlite:///")
    or "://" not in _RAW_DB_URL
):
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
    if not _leaderboard_cache:
        rebuild_leaderboard_cache()
    return _leaderboard_cache


def fetch_user(user_id: int) -> Dict[str, Any]:
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
    with get_session() as session:
        user = session.get(User, data["user_id"])
        if user:
            for key in ("nick", "xp", "level", "coins", "items"):
                if key in data:
                    setattr(user, key, data[key])
            session.commit()


def atomic_purchase(user_id: int, item_name: str, price: int) -> tuple[bool, str]:
    """
    Effectue un achat dans une transaction atomique pour éviter les race conditions.
    Retourne un tuple (succès, message).
    """
    with get_session() as session:
        # Verrouille la ligne de l'utilisateur pour la durée de la transaction.
        user = session.get(User, user_id, with_for_update=True)

        if not user:
            return False, "Utilisateur non trouvé."

        if user.coins < price:
            return False, f"Solde insuffisant. Vous avez {user.coins} Ignis."

        user.coins -= price
        current_items = list(user.items) if user.items is not None else []
        current_items.append(item_name)
        user.items = current_items

        session.commit()
        return True, "Achat réussi !"


def reset_all_daily_counts() -> None:
    with get_session() as session:
        stmt = select(User)
        for user in session.execute(stmt).scalars().all():
            user.last_daily = None
        session.commit()
