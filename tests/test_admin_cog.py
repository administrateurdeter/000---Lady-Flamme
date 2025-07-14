import pytest
from discord.ext import commands
from cogs.admin_cog import AdminCog


@pytest.fixture
def bot() -> commands.Bot:
    return commands.Bot(command_prefix="!")


@pytest.mark.asyncio
async def test_admin_cog_load(bot):
    """
    Vérifie que le cog AdminCog se charge bien dans le bot
    et qu'il est accessible via bot.get_cog.
    """
    cog = AdminCog(bot)
    await bot.add_cog(cog)
    assert bot.get_cog("AdminCog") is cog
