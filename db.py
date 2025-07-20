"""Module de gestion de la base de données avec SQLAlchemy.

Ce module définit le modèle de données `User` et fournit des fonctions
d'accès atomiques et sécurisées pour interagir avec la base de données.
Il inclut également un système de cache pour le leaderboard.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import (
    DateTime,
    Integer,
    JSON,
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

from config import BotConfig  # Configuration centralisée

# ---------------------------------------------------------
# 1. Vérification des variables d'environnement critiques
# ---------------------------------------------------------
if not all(
    [
        BotConfig.DB_PASSWORD,
        BotConfig.DB_TNS_NAME,
        BotConfig.WALLET_LOCATION,
    ]
):
    raise ValueError(
        "Les variables d'environnement DB_PASSWORD, DB_TNS_NAME, et "
        "WALLET_LOCATION doivent être définies."
    )

# ---------------------------------------------------------
# 2. Création du moteur SQLAlchemy (Thin mode + Wallet)
# ---------------------------------------------------------
TNS_DIR = os.environ["TNS_ADMIN"]  # dossier wallet déjà exporté

engine = create_engine(
    "oracle+oracledb://",  # Thin driver
    connect_args={
        "user": os.getenv("DB_USER", "ADMIN"),
        "password": os.getenv("DB_PASSWORD"),
        "dsn": os.getenv("DB_TNS_NAME"),
        "config_dir": TNS_DIR,  # indispensable
        "wallet_location": TNS_DIR,  # indispensable
        "wallet_password": os.getenv("WALLET_PASSWORD"),  # indispensable
    },
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


# ---------------------------------------------------------
# 3. Modèles SQLAlchemy
# ---------------------------------------------------------
class Base(DeclarativeBase):
    """Classe de base pour les modèles SQLAlchemy (compatible mypy)."""


class User(Base):
    """Modèle de données représentant un utilisateur Discord."""

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nick: Mapped[str | None] = mapped_column(String, nullable=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=0)
    coins: Mapped[int] = mapped_column(Integer, default=0)
    items: Mapped[list] = mapped_column(JSON, default=lambda: [])
    last_daily: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# ---------------------------------------------------------
# 4. Création des tables (au démarrage)
# ---------------------------------------------------------
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logging.error("Erreur de connexion à la base de données: %s", e)


# ---------------------------------------------------------
# 5. Helpers session
# ---------------------------------------------------------
def get_session() -> Session:
    """Retourne une nouvelle session SQLAlchemy."""
    return SessionLocal()


# ---------------------------------------------------------
# 6. Cache leaderboard
# ---------------------------------------------------------
_leaderboard_cache: List[Dict[str, Any]] = []
_last_cache_time: datetime = datetime.min


def rebuild_leaderboard_cache() -> None:
    """Reconstruit le cache du leaderboard depuis la base."""
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
            "avatar": (
                f"https://cdn.discordapp.com/avatars/{u.user_id}/{u.user_id}.png"
            ),
        }
        for u in users
    ]
    _last_cache_time = datetime.utcnow()


def get_leaderboard_from_cache() -> List[Dict[str, Any]]:
    """Retourne le leaderboard depuis le cache (reconstruit si vide)."""
    if not _leaderboard_cache:
        rebuild_leaderboard_cache()
    return _leaderboard_cache


# ---------------------------------------------------------
# 7. Fonctions CRUD utilisateur
# ---------------------------------------------------------
def fetch_user(user_id: int) -> Dict[str, Any]:
    """Récupère un utilisateur ; le crée s'il n'existe pas."""
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            user = User(user_id=user_id, xp=0, level=0, coins=0, items=[])
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
        "last_daily": user.last_daily,
    }


def save_user(data: Dict[str, Any]) -> None:
    """Sauvegarde les champs présents dans `data`."""
    with get_session() as session:
        user = session.get(User, data["user_id"])
        if user:
            for key in ("nick", "xp", "level", "coins", "items", "last_daily"):
                if key in data:
                    setattr(user, key, data[key])
            session.commit()


# ---------------------------------------------------------
# 8. Transaction atomique d'achat
# ---------------------------------------------------------
def atomic_purchase(user_id: int, item_name: str, price: int) -> tuple[bool, str]:
    """Effectue un achat en garantissant l'intégrité des données."""
    with get_session() as session:
        user = session.get(User, user_id, with_for_update=True)
        if not user:
            return False, "Utilisateur non trouvé."

        if user.coins < price:
            return False, f"Solde insuffisant. Vous avez {user.coins} Ignis."

        current_items = list(user.items) if user.items is not None else []
        current_items.append(item_name)
        user.items = current_items
        user.coins -= price

        session.commit()
        return True, "Achat réussi !"
