"""
Point d'entrée principal du bot Discord.

Ce script configure le logging, les intents Discord, charge tous les cogs
et démarre le bot.
"""

import asyncio
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import discord
from discord.ext import commands
from config import BotConfig
from typing import List, Any

def setup_logging() -> None:
    """Configure le logging rotatif pour les logs du bot."""
    file_handler: RotatingFileHandler = RotatingFileHandler(
        filename="bot.log",
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8"
    )
    stream_handler: logging.StreamHandler = logging.StreamHandler()
    fmt: str = "%(asctime)s – %(levelname)s – %(name)s – %(message)s"
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler], format=fmt)


async def main() -> None:
    """Initialise et démarre le bot."""
    setup_logging()
    logger: logging.Logger = logging.getLogger("main")

    # Validation des variables d'environnement
    required = ["DISCORD_BOT_TOKEN", "GUILD_ID", "DATABASE_URL"]
    missing = [v for v in required if os.getenv(v) is None]
    if missing:
        logger.critical(f"Variables d'environnement manquantes : {', '.join(missing)}")
        sys.exit(1)

    # Vérification que GUILD_ID est un entier
    try:
        int(os.getenv("GUILD_ID"))  # type: ignore
    except (TypeError, ValueError):
        logger.critical("La variable d'environnement GUILD_ID doit être un entier valide.")
        sys.exit(1)

    intents: discord.Intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot: commands.Bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready() -> None:
        """Événement déclenché lorsque le bot est connecté et prêt."""
        # On s'assure que bot.user n'est pas None avant d'y accéder
        assert bot.user is not None, "Le bot doit être connecté avant d'accéder à bot.user"
        logger.info(f"Connecté comme {bot.user} (ID {bot.user.id})")
        try:
            # On utilise une annotation générique Any pour MyPy
            synced: List[Any] = await bot.tree.sync(
                guild=discord.Object(id=BotConfig.GUILD_ID)
            )
            logger.info(f"Slash commands synchronisées : {len(synced)}")
        except Exception as e:
            logger.error("Erreur de sync des slash commands", exc_info=e)

    # Chargement dynamique des cogs
    for file in os.listdir("cogs"):
        if file.endswith(".py") and file != "__init__.py":
            ext: str = f"cogs.{file[:-3]}"
            try:
                await bot.load_extension(ext)
                logger.info(f"Cog chargé : {ext}")
            except Exception as e:
                logger.error(f"Échec du chargement de {ext}", exc_info=e)

    await bot.start(BotConfig.BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
