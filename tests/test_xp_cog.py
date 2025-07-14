import pytest
from discord.ext import commands
from cogs.xp_cog import XPCog


@pytest.fixture
def bot() -> commands.Bot:
    return commands.Bot(command_prefix="!")


@pytest.mark.asyncio
async def test_xp_cog_load(bot):
    """
    Vérifie que le cog XPCog se charge bien dans le bot
    et qu'il est accessible via bot.get_cog.
    """
    cog = XPCog(bot)
    await bot.add_cog(cog)
    assert bot.get_cog("XPCog") is cog
