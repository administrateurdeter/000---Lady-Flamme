"""Module de gestion de la base de données avec SQLAlchemy.

Ce module définit le modèle de données `User` et fournit des fonctions
d'accès atomiques et sécurisées pour interagir avec la base de données.
Il inclut également un système de cache pour le leaderboard.
"""

import os
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    create_engine,
    select,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# --- Configuration du moteur de base de données ---
_RAW_DB_URL = os.getenv("DATABASE_URL", "")
if (
    not _RAW_DB_URL
    or _RAW_DB_URL.lower().startswith("sqlite:///")
    or "://" not in _RAW_DB_URL
):
    # Fallback vers une base de données en mémoire si l'URL est invalide ou non fournie.
    _DB_URL = "sqlite:///:memory:"
else:
    _DB_URL = _RAW_DB_URL

engine = create_engine(
    _DB_URL,
    connect_args={"check_same_thread": False} if _DB_URL.startswith("sqlite") else {},
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


class User(Base):
    """Modèle de données représentant un utilisateur dans la base."""

    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    nick = Column(String, nullable=True)
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=0, nullable=False)
    coins = Column(Integer, default=0, nullable=False)
    items = Column(JSON, default=lambda: [])
    last_daily = Column(DateTime, default=None, nullable=True)


try:
    # Crée les tables si elles n'existent pas.
    Base.metadata.create_all(bind=engine)
except OperationalError as e:
    # Gère le cas où la base de données n'est pas encore prête.
    logging.error(f"Erreur de connexion à la base de données: {e}")


def get_session() -> Session:
    """Crée et retourne une nouvelle session SQLAlchemy."""
    return SessionLocal()


# --- Fonctions d'accès et de manipulation des données ---

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
    """Récupère un utilisateur par son ID, le crée s'il n'existe pas.

    Args:
        user_id: L'ID Discord de l'utilisateur.

    Returns:
        Un dictionnaire représentant les données de l'utilisateur.
    """
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
        "last_daily": user.last_daily,
    }


def save_user(data: Dict[str, Any]) -> None:
    """Sauvegarde les données d'un dictionnaire utilisateur en base.

    Args:
        data: Le dictionnaire contenant les données de l'utilisateur.
              Doit inclure 'user_id'.
    """
    with get_session() as session:
        user = session.get(User, data["user_id"])
        if user:
            for key in ("nick", "xp", "level", "coins", "items", "last_daily"):
                if key in data:
                    setattr(user, key, data[key])
            session.commit()


def atomic_purchase(user_id: int, item_name: str, price: int) -> tuple[bool, str]:
    """Effectue un achat dans une transaction atomique pour éviter les race conditions.

    Args:
        user_id: L'ID de l'acheteur.
        item_name: Le nom de l'objet acheté.
        price: Le prix de l'objet.

    Returns:
        Un tuple (succès, message).
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
