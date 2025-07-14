import pytest
from discord.ext import commands
from cogs.error_handler_cog import ErrorHandlerCog


@pytest.fixture
def bot() -> commands.Bot:
    return commands.Bot(command_prefix="!")


@pytest.mark.asyncio
async def test_error_handler_cog_load(bot):
    """
    Vérifie que le cog ErrorHandlerCog se charge bien dans le bot
    et qu'il est accessible via bot.get_cog.
    """
    cog = ErrorHandlerCog(bot)
    await bot.add_cog(cog)
    assert bot.get_cog("ErrorHandlerCog") is cog
