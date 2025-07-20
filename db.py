"""Gestion de la base de données Lady‑Flamme (Oracle ADB + SQLAlchemy).

– Modèle `User`
– Helpers cache/leaderboard
– Fonctions CRUD + achat atomique
Compatible ADB 19c : la colonne `items` est stockée en CLOB (JSON sérialisé).
"""

from __future__ import annotations

import json
import logging
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

# ---------------------------------------------------------------------------
# Vérif variables env
# ---------------------------------------------------------------------------
if not all([BotConfig.DB_PASSWORD, BotConfig.DB_TNS_NAME, BotConfig.WALLET_LOCATION]):
    raise ValueError(
        "DB_PASSWORD, DB_TNS_NAME et WALLET_LOCATION doivent être définies."
    )

# ---------------------------------------------------------------------------
# Moteur SQLAlchemy (Thin + Wallet)
# ---------------------------------------------------------------------------
TNS_DIR = os.environ["TNS_ADMIN"]  # dossier wallet exporté

engine = create_engine(
    "oracle+oracledb://",
    connect_args={
        "user": os.getenv("DB_USER", "ADMIN"),
        "password": os.getenv("DB_PASSWORD"),
        "dsn": os.getenv("DB_TNS_NAME"),
        "config_dir": TNS_DIR,
        "wallet_location": TNS_DIR,
        "wallet_password": os.getenv("WALLET_PASSWORD"),
    },
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# ---------------------------------------------------------------------------
# Helpers sérialisation items
# ---------------------------------------------------------------------------


def _items_to_db(value: list | None) -> str:
    return json.dumps(value or [])


def _items_from_db(value: str | None) -> list:
    return json.loads(value or "[]")


# ---------------------------------------------------------------------------
# Modèle
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    """Classe de base pour les modèles SQLAlchemy (compatible mypy)."""

    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nick: Mapped[str | None] = mapped_column(String, nullable=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=0)
    coins: Mapped[int] = mapped_column(Integer, default=0)
    items: Mapped[str] = mapped_column(
        CLOB,
        nullable=True,
        default="[]",
    )  # JSON sérialisé
    last_daily: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# ---------------------------------------------------------------------------
# Création table (si absente)
# ---------------------------------------------------------------------------
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logging.error("Erreur DB : %s", e)


# ---------------------------------------------------------------------------
# Session helper
# ---------------------------------------------------------------------------
def get_session() -> Session:
    return SessionLocal()


# ---------------------------------------------------------------------------
# Leaderboard cache
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# CRUD & achat atomique
# ---------------------------------------------------------------------------
def fetch_user(user_id: int) -> Dict[str, Any]:
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            user = User(
                user_id=user_id,
                xp=0,
                level=0,
                coins=0,
                items="[]",
            )
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
            for key in ("nick", "xp", "level", "coins", "items", "last_daily"):
                if key in data:
                    if key == "items":
                        setattr(user, key, _items_to_db(data[key]))
                    else:
                        setattr(user, key, data[key])
            session.commit()


def atomic_purchase(user_id: int, item_name: str, price: int) -> tuple[bool, str]:
    with get_session() as session:
        user = session.get(User, user_id, with_for_update=True)
        if not user:
            return False, "Utilisateur non trouvé."

        if user.coins < price:
            return False, f"Solde insuffisant. Vous avez {user.coins} Ignis."

        items = _items_from_db(user.items)
        items.append(item_name)
        user.items = _items_to_db(items)
        user.coins -= price
        session.commit()
        return True, "Achat réussi !"
