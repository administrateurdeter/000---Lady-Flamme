"""Tests unitaires pour le cog de gestion des erreurs (ErrorHandlerCog)."""

import pytest
from discord.ext import commands

from cogs.error_handler_cog import ErrorHandlerCog


@pytest.fixture
def bot() -> commands.Bot:
    """Crée une instance de bot factice pour les tests."""
    return commands.Bot(command_prefix="!")


@pytest.mark.asyncio
async def test_error_handler_cog_load(bot: commands.Bot):
    """Vérifie que le cog ErrorHandlerCog se charge correctement dans le bot.

    Args:
        bot: L'instance du bot de test.
    """
    # --- Préparation (Arrange) ---
    cog = ErrorHandlerCog(bot)

    # --- Action (Act) ---
    await bot.add_cog(cog)

    # --- Vérification (Assert) ---
    assert bot.get_cog("ErrorHandlerCog") is cog
