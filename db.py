"""Module de gestion de la base de données avec SQLAlchemy.

Ce module définit le modèle de données `User` et fournit des fonctions
d'accès atomiques et sécurisées pour interagir avec la base de données.
Il inclut également un système de cache pour le leaderboard.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import create_engine, DateTime, Integer, JSON, select, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker

from config import BotConfig  # On importe la configuration centralisée

# --- NOUVELLE CONFIGURATION DU MOTEUR POUR ORACLE CLOUD ---
# Vérification que les variables critiques sont définies
if not all([BotConfig.DB_PASSWORD, BotConfig.DB_TNS_NAME, BotConfig.WALLET_LOCATION]):
    raise ValueError(
        "Les variables d'environnement DB_PASSWORD, DB_TNS_NAME, et "
        "WALLET_LOCATION doivent être définies."
    )

# Construction de la chaîne de connexion (DSN) pour Oracle
dsn = f"{BotConfig.DB_USER}/{BotConfig.DB_PASSWORD}@{BotConfig.DB_TNS_NAME}"

# Création du moteur SQLAlchemy pour Oracle
engine = create_engine(
    "oracle+oracledb://",  # <-- CORRECTION APPLIQUÉE ICI
    connect_args={
        "dsn": dsn,
        "config_dir": BotConfig.WALLET_LOCATION,
        "wallet_location": BotConfig.WALLET_LOCATION,
        "wallet_password": BotConfig.WALLET_PASSWORD,
    },
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


# --- Le reste du fichier ne change pas ---
class Base(DeclarativeBase):
    """Classe de base pour les modèles SQLAlchemy, compatible avec mypy."""

    pass


class User(Base):
    """Modèle de données représentant un utilisateur dans la base."""

    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nick: Mapped[str | None] = mapped_column(String, nullable=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=0)
    coins: Mapped[int] = mapped_column(Integer, default=0)
    items: Mapped[list] = mapped_column(JSON, default=lambda: [])
    last_daily: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logging.error(f"Erreur de connexion à la base de données: {e}")


def get_session() -> Session:
    """Crée et retourne une nouvelle session SQLAlchemy."""
    return SessionLocal()


_leaderboard_cache: List[Dict[str, Any]] = []
_last_cache_time: datetime = datetime.min


def rebuild_leaderboard_cache() -> None:
    """Reconstruit le cache du leaderboard à partir de la base de données."""
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
    """Retourne le leaderboard depuis le cache. Le reconstruit si vide."""
    if not _leaderboard_cache:
        rebuild_leaderboard_cache()
    return _leaderboard_cache


def fetch_user(user_id: int) -> Dict[str, Any]:
    """Récupère un utilisateur par son ID, le crée s'il n'existe pas."""
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
    """Sauvegarde les données d'un dictionnaire utilisateur en base."""
    with get_session() as session:
        user = session.get(User, data["user_id"])
        if user:
            for key in ("nick", "xp", "level", "coins", "items", "last_daily"):
                if key in data:
                    setattr(user, key, data[key])
            session.commit()


def atomic_purchase(user_id: int, item_name: str, price: int) -> tuple[bool, str]:
    """Effectue un achat dans une transaction atomique."""
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
