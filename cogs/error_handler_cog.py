"""Cog pour la gestion globale des erreurs de commande."""

import logging

import discord
from discord.ext import commands

from config import VisualConfig

logger = logging.getLogger(__name__)


class ErrorHandlerCog(commands.Cog):
    """Gestionnaire d'erreurs global pour les commandes à préfixe."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialise le cog de gestion des erreurs."""
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Listener global qui intercepte les erreurs des commandes à préfixe.

        Args:
            ctx: Le contexte de la commande qui a échoué.
            error: L'exception d'erreur levée.
        """
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title=f"{VisualConfig.EMOJIS['warning']} Argument manquant",
                description=str(error),
                colour=VisualConfig.COLORS["warning"],
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.CommandNotFound):
            # On ignore silencieusement les commandes inconnues pour ne pas polluer.
            return

        # Pour toutes les autres erreurs, on logue et on notifie l'utilisateur.
        logger.exception(
            f"Erreur dans la commande '{ctx.command}': {error}", exc_info=error
        )
        embed = discord.Embed(
            title=f"{VisualConfig.EMOJIS['error']} Erreur interne",
            description=(
                "Oups… une erreur inattendue est survenue. "
                "L’équipe a été notifiée."
            ),
            colour=VisualConfig.COLORS["error"],
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Fonction d'entrée pour charger le cog."""
    await bot.add_cog(ErrorHandlerCog(bot))