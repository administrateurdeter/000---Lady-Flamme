"""Tests unitaires pour le cog du serveur web (WebCog)."""

import pytest
from discord.ext import commands

from cogs.web_cog import WebCog


@pytest.fixture
def bot() -> commands.Bot:
    """Crée une instance de bot factice pour les tests."""
    return commands.Bot(command_prefix="!")


@pytest.mark.asyncio
async def test_web_cog_load(bot: commands.Bot):
    """Vérifie que le cog WebCog se charge correctement dans le bot.

    Args:
        bot: L'instance du bot de test.
    """
    # --- Préparation (Arrange) ---
    cog = WebCog(bot)

    # --- Action (Act) ---
    await bot.add_cog(cog)

    # --- Vérification (Assert) ---
    assert bot.get_cog("WebCog") is cog
