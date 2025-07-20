"""
Gestion de la base de données Lady‑Flamme (Oracle 19c ADB + SQLAlchemy).

– Modèle User
– Helpers cache/leaderboard
– Fonctions CRUD + achat atomique

La colonne `items` est stockée en CLOB (JSON sérialisé) : compatible avec
les Autonomous Databases 19c (où le type JSON natif n’est pas disponible).
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Imports                                                                    #
# --------------------------------------------------------------------------- #
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

# --------------------------------------------------------------------------- #
# Vérification des variables d’environnement                                  #
# --------------------------------------------------------------------------- #
if not all([BotConfig.DB_PASSWORD, BotConfig.DB_TNS_NAME, BotConfig.WALLET_LOCATION]):
    raise ValueError(
        "DB_PASSWORD, DB_TNS_NAME et WALLET_LOCATION doivent être définies dans .env"
    )

# --------------------------------------------------------------------------- #
# Moteur SQLAlchemy (mode Thin + Wallet)                                      #
# --------------------------------------------------------------------------- #
TNS_DIR = os.environ["TNS_ADMIN"]  # dossier wallet déjà exporté

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

# --------------------------------------------------------------------------- #
# Helpers (sérialisation / désérialisation des items)                         #
# --------------------------------------------------------------------------- #


def _items_to_db(value: list | None) -> str:
    """Convertit la liste d’objets → chaîne JSON pour stockage."""
    return json.dumps(value or [])


def _items_from_db(value: str | None) -> list:
    """Convertit la chaîne JSON stockée → liste Python."""
    return json.loads(value or "[]")


# --------------------------------------------------------------------------- #
# Modèles                                                                     #
# --------------------------------------------------------------------------- #
class Base(DeclarativeBase):
    """Base SQLAlchemy avec typing friendly (mypy)."""

    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nick: Mapped[str | None] = mapped_column(String(100), nullable=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=0)
    coins: Mapped[int] = mapped_column(Integer, default=0)
    items: Mapped[str] = mapped_column(
        CLOB,
        nullable=True,
        default="[]",  # chaîne JSON vide
    )
    last_daily: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# --------------------------------------------------------------------------- #
# Création de la table si elle n’existe pas                                   #
# --------------------------------------------------------------------------- #
try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:  # pragma: no cover
    logging.error("Erreur DB : %s", exc)


# --------------------------------------------------------------------------- #
# Helpers sessions                                                            #
# --------------------------------------------------------------------------- #
def get_session() -> Session:
    """Renvoie une session SQLAlchemy déjà configurée."""
    return SessionLocal()


# --------------------------------------------------------------------------- #
# Leaderboard cache (en mémoire)                                              #
# --------------------------------------------------------------------------- #
_leaderboard_cache: List[Dict[str, Any]] = []
_last_cache_time: datetime = datetime.min


def rebuild_leaderboard_cache() -> None:
    """Recharge le cache complet depuis la base."""
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


# --------------------------------------------------------------------------- #
# CRUD & achat atomique                                                       #
# --------------------------------------------------------------------------- #
def fetch_user(user_id: int) -> Dict[str, Any]:
    """Récupère un utilisateur (créé si absent)."""
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
    """Met à jour un utilisateur existant avec `data`."""
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
    """Achete un objet de manière transactionnelle."""
    with get_session() as session:
        user = session.get(User, user_id, with_for_update=True)
        if not user:
            return False, "Utilisateur non trouvé."

        if user.coins < price:
            return False, f"Solde insuffisant : {user.coins} Ignis."

        items = _items_from_db(user.items)
        items.append(item_name)
        user.items = _items_to_db(items)
        user.coins -= price
        session.commit()
        return True, "Achat réussi !"
