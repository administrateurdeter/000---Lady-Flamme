"""Tests unitaires pour le cog des commandes utilisateur (CommandsCog)."""

import pytest
from discord.ext import commands

from cogs.commands_cog import CommandsCog


@pytest.fixture
def bot() -> commands.Bot:
    """Crée une instance de bot factice pour les tests."""
    return commands.Bot(command_prefix="!")


@pytest.mark.asyncio
async def test_commands_cog_load(bot: commands.Bot):
    """Vérifie que le cog CommandsCog se charge correctement dans le bot.

    Args:
        bot: L'instance du bot de test.
    """
    # --- Préparation (Arrange) ---
    cog = CommandsCog(bot)

    # --- Action (Act) ---
    await bot.add_cog(cog)

    # --- Vérification (Assert) ---
    assert bot.get_cog("CommandsCog") is cog
