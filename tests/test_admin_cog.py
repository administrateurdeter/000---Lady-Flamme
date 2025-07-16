"""Tests unitaires pour le cog d'administration (AdminCog)."""

import pytest
from discord.ext import commands

from cogs.admin_cog import AdminCog


@pytest.fixture
def bot() -> commands.Bot:
    """Crée une instance de bot factice pour les tests."""
    return commands.Bot(command_prefix="!")


@pytest.mark.asyncio
async def test_admin_cog_load(bot: commands.Bot):
    """Vérifie que le cog AdminCog se charge correctement dans le bot.

    Args:
        bot: L'instance du bot de test.
    """
    # --- Préparation (Arrange) ---
    cog = AdminCog(bot)

    # --- Action (Act) ---
    await bot.add_cog(cog)

    # --- Vérification (Assert) ---
    assert bot.get_cog("AdminCog") is cog
