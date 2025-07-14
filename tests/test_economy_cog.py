import pytest
from discord.ext import commands
from cogs.economy_cog import EconomyCog


@pytest.fixture
def bot() -> commands.Bot:
    return commands.Bot(command_prefix="!")


@pytest.mark.asyncio
async def test_economy_cog_load(bot):
    """
    Vérifie que le cog EconomyCog se charge bien dans le bot
    et qu'il est accessible via bot.get_cog.
    """
    cog = EconomyCog(bot)
    await bot.add_cog(cog)
    assert bot.get_cog("EconomyCog") is cog
