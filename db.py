"""
Gestion de la base de données Lady-Flamme (Oracle 19c ADB + SQLAlchemy).

- Modèle User (items stocké en CLOB JSON-stringifié)
- Fonctions CRUD + cache leaderboard
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import (
    CLOB,
    DateTime,
    Integer,
    String,
    create_engine,
    select,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)

from config import BotConfig

# --- 1. Configuration via variables d'environnement ---
if not all([BotConfig.DB_PASSWORD, BotConfig.DB_TNS_NAME, os.getenv("TNS_ADMIN")]):
    raise RuntimeError("DB_PASSWORD, DB_TNS_NAME et TNS_ADMIN doivent être définies.")

TNS_ADMIN = os.environ["TNS_ADMIN"]

# --- 2. Moteur SQLAlchemy ---
engine = create_engine(
    "oracle+oracledb://",
    connect_args={
        "user": BotConfig.DB_USER,
        "password": BotConfig.DB_PASSWORD,
        "dsn": BotConfig.DB_TNS_NAME,
        "config_dir": TNS_ADMIN,
        "wallet_location": TNS_ADMIN,
        "wallet_password": BotConfig.WALLET_PASSWORD,
    },
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


# --- 3. Helpers (JSON <-> CLOB) ---
def _items_to_db(value: list | None) -> str:
    return json.dumps(value or [])


def _items_from_db(value: str | None) -> list:
    return json.loads(value or "[]")


# --- 4. Déclarations de modèles ---
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nick: Mapped[str | None] = mapped_column(String(100), nullable=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=0)
    coins: Mapped[int] = mapped_column(Integer, default=0)
    items: Mapped[str] = mapped_column(CLOB, default="[]")
    last_daily: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# --- 6. Sessions helpers ---
def get_session() -> Session:
    return SessionLocal()


# --- 7. Cache leaderboard ---
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
            "items": _items_from_db(u.items),
            "avatar": f"https://cdn.discordapp.com/avatars/{u.user_id}/{u.user_id}.png",
        }
        for u in users
    ]
    _last_cache_time = datetime.utcnow()


def get_leaderboard_from_cache() -> List[Dict[str, Any]]:
    if not _leaderboard_cache:
        rebuild_leaderboard_cache()
    return _leaderboard_cache


# --- 8. CRUD + achat atomique ---
def fetch_user(user_id: int) -> Dict[str, Any]:
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            user = User(user_id=user_id)
            session.add(user)
            session.commit()
            session.refresh(user)
    return {
        "user_id": user.user_id,
        "nick": user.nick,
        "xp": user.xp,
        "level": user.level,
        "coins": user.coins,
        "items": _items_from_db(user.items),
        "last_daily": user.last_daily,
    }


def save_user(data: Dict[str, Any]) -> None:
    with get_session() as session:
        user = session.get(User, data["user_id"])
        if user:
            for key in ("nick", "xp", "level", "coins", "last_daily"):
                if key in data:
                    setattr(user, key, data[key])
            if "items" in data:
                user.items = _items_to_db(data["items"])
            session.commit()


def atomic_purchase(user_id: int, item_name: str, price: int) -> tuple[bool, str]:
    with get_session() as session:
        user = session.get(User, user_id, with_for_update=True)
        if not user:
            return False, "Utilisateur non trouvé."
        if user.coins < price:
            return False, f"Solde insuffisant : {user.coins} Ignis."

        items = _items_from_db(user.items)
        items.append(item_name)
        user.items = _items_to_db(items)
        user.coins -= price
        session.commit()
        return True, "Achat réussi !"
