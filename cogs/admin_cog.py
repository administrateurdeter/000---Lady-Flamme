"""Cog pour les commandes d'administration réservées au propriétaire du bot."""

import logging

import discord
from discord.ext import commands

from cogs.commands_cog import CommandsCog
from cogs.xp_cog import XPCog
from db import User, get_session, rebuild_leaderboard_cache, save_user

# On importe la fonction de recalcul depuis le nouveau module utils
from utils import total_xp_to_level


logger = logging.getLogger(__name__)


class AdminCog(commands.Cog):
    """Commandes administratives en préfixe `!` pour la gestion du bot."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialise le cog d'administration."""
        self.bot = bot

    @commands.command(name="reload_all")
    @commands.is_owner()
    async def reload_all(self, ctx: commands.Context) -> None:
        """Recharge tous les cogs dynamiquement sans redémarrer le bot."""
        failures = []
        for ext in list(self.bot.extensions):
            try:
                await self.bot.reload_extension(ext)
            except Exception as e:
                failures.append(f"{ext} ({e})")

        if failures:
            embed = discord.Embed(
                title="⚠️ Échecs de Rechargement",
                description="\n".join(failures),
                colour=0xFE6A33,
            )
        else:
            embed = discord.Embed(
                title="✅ Rechargement Terminé",
                description="Tous les cogs ont été rechargés avec succès !",
                colour=0xFE6A33,
            )
        await ctx.send(embed=embed)

    @commands.command(name="recalculate_levels")
    @commands.is_owner()
    async def recalculate_all_levels(self, ctx: commands.Context) -> None:
        """[MAINTENANCE] Recalcule le niveau de TOUS les utilisateurs.

        Cette commande doit être utilisée une seule fois après la migration
        vers le système Spline Unifiée pour aligner les niveaux de tous
        les membres sur la nouvelle courbe de progression.
        """
        await ctx.send(
            "Début du recalcul de tous les niveaux... Cette opération peut prendre un moment."
        )

        updated_count = 0
        with get_session() as session:
            all_users = session.query(User).all()

            for user in all_users:
                old_level = user.level
                new_level = total_xp_to_level(user.xp)

                if old_level != new_level:
                    user.level = new_level
                    updated_count += 1

            session.commit()

        # Reconstruit le cache du leaderboard pour refléter les changements
        rebuild_leaderboard_cache()

        await ctx.send(
            f"✅ Recalcul terminé ! {updated_count} utilisateurs ont vu leur niveau mis à jour."
        )


async def setup(bot: commands.Bot) -> None:
    """Fonction d'entrée pour charger le cog."""
    await bot.add_cog(AdminCog(bot))
