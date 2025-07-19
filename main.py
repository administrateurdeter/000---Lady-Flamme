"""Point d'entrée principal du bot Discord.

Ce script configure le logging, les intents Discord, charge tous les cogs
et démarre le bot.
"""

import asyncio
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, List

import discord
from discord.ext import commands

from config import BotConfig


def setup_logging() -> None:
    """Configure le logging rotatif pour les logs du bot."""
    file_handler = RotatingFileHandler(
        filename="bot.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8"
    )
    stream_handler = logging.StreamHandler()
    fmt = "%(asctime)s – %(levelname)s – %(name)s – %(message)s"
    logging.basicConfig(
        level=logging.INFO, handlers=[file_handler, stream_handler], format=fmt
    )


async def main() -> None:
    """Initialise et démarre le bot."""
    setup_logging()
    logger = logging.getLogger("main")

    # --- NOUVELLE VALIDATION DES VARIABLES D'ENVIRONNEMENT POUR ORACLE ---
    required_vars = [
        "DISCORD_BOT_TOKEN",
        "GUILD_ID",
        "DB_PASSWORD",
        "DB_TNS_NAME",
        "WALLET_LOCATION",
    ]
    missing_vars = [v for v in required_vars if not os.getenv(v)]
    if missing_vars:
        logger.critical(
            f"Variables d'environnement manquantes : {', '.join(missing_vars)}"
        )
        sys.exit(1)

    # --- CORRECTION MYPY: Validation explicite pour le type de GUILD_ID ---
    guild_id_str = os.getenv("GUILD_ID")
    if not guild_id_str or not guild_id_str.isdigit():
        logger.critical(
            "La variable d'environnement GUILD_ID doit être un entier valide."
        )
        sys.exit(1)

    # À ce stade, mypy sait que guild_id_str est une chaîne de chiffres.
    guild_id = int(guild_id_str)

    # --- Configuration des Intents Discord ---
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready() -> None:
        """Événement déclenché lorsque le bot est connecté et prêt."""
        if not bot.user:
            logger.critical("bot.user est None après la connexion. Arrêt.")
            return

        logger.info(f"Connecté comme {bot.user.name} (ID: {bot.user.id})")
        try:
            synced: List[Any] = await bot.tree.sync(guild=discord.Object(id=guild_id))
            logger.info(f"{len(synced)} slash commands synchronisées pour la guilde.")
        except Exception as e:
            logger.error("Erreur de synchronisation des slash commands", exc_info=e)

    # --- Chargement dynamique des cogs ---
    for filename in os.listdir("cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            extension = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(extension)
                logger.info(f"Cog chargé : {extension}")
            except Exception as e:
                logger.error(f"Échec du chargement de {extension}", exc_info=e)

    await bot.start(BotConfig.BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
