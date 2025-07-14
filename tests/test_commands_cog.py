import pytest
from discord.ext import commands
from cogs.commands_cog import CommandsCog


@pytest.fixture
def bot() -> commands.Bot:
    return commands.Bot(command_prefix="!")


@pytest.mark.asyncio
async def test_commands_cog_load(bot):
    """
    Vérifie que le cog CommandsCog se charge bien dans le bot
    et qu'il est accessible via bot.get_cog.
    """
    cog = CommandsCog(bot)
    await bot.add_cog(cog)
    assert bot.get_cog("CommandsCog") is cog
