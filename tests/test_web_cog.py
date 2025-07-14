import pytest
from discord.ext import commands
from cogs.web_cog import WebCog


@pytest.fixture
def bot() -> commands.Bot:
    return commands.Bot(command_prefix="!")


@pytest.mark.asyncio
async def test_web_cog_load(bot):
    """
    Vérifie que le cog WebCog se charge bien dans le bot
    et qu'il est accessible via bot.get_cog.
    """
    cog = WebCog(bot)
    await bot.add_cog(cog)
    assert bot.get_cog("WebCog") is cog
