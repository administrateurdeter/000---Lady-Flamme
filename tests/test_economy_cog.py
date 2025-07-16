"""Tests unitaires pour le cog de l'économie (EconomyCog)."""

import pytest
from discord.ext import commands

from cogs.economy_cog import EconomyCog


@pytest.fixture
def bot() -> commands.Bot:
    """Crée une instance de bot factice pour les tests."""
    return commands.Bot(command_prefix="!")


@pytest.mark.asyncio
async def test_economy_cog_load(bot: commands.Bot):
    """Vérifie que le cog EconomyCog se charge correctly dans le bot.

    Args:
        bot: L'instance du bot de test.
    """
    # --- Préparation (Arrange) ---
    cog = EconomyCog(bot)

    # --- Action (Act) ---
    await bot.add_cog(cog)

    # --- Vérification (Assert) ---
    assert bot.get_cog("EconomyCog") is cog
