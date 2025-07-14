import logging
import discord
from discord.ext import commands
from config import VisualConfig

logger = logging.getLogger(__name__)


class ErrorHandlerCog(commands.Cog):
    """Gestion globale des erreurs de commande."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title=f"{VisualConfig.EMOJIS['warning']} Argument manquant",
                description=str(error),
                colour=VisualConfig.COLORS["warning"],
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.CommandNotFound):
            return  # on ignore les commandes inconnues

        logger.exception(f"Erreur dans {ctx.command}: {error}", exc_info=error)
        embed = discord.Embed(
            title=f"{VisualConfig.EMOJIS['error']} Erreur interne",
            description="Oups… une erreur inattendue est survenue. L’équipe a été notifiée.",
            colour=VisualConfig.COLORS["error"],
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ErrorHandlerCog(bot))
