"""Tests unitaires pour le cog de gestion de l'XP (XPCog)."""

import pytest
from discord.ext import commands

from cogs.xp_cog import XPCog


@pytest.fixture
def bot() -> commands.Bot:
    """Crée une instance de bot factice pour les tests."""
    return commands.Bot(command_prefix="!")


@pytest.mark.asyncio
async def test_xp_cog_load(bot: commands.Bot):
    """Vérifie que le cog XPCog se charge correctement dans le bot.

    Args:
        bot: L'instance du bot de test.
    """
    # --- Préparation (Arrange) ---
    cog = XPCog(bot)

    # --- Action (Act) ---
    await bot.add_cog(cog)

    # --- Vérification (Assert) ---
    assert bot.get_cog("XPCog") is cog
