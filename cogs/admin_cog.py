"""
Cog pour les commandes d'administration réservées au propriétaire du bot.
"""

import logging
import discord
from discord.ext import commands
from db import rebuild_leaderboard_cache, save_user
from cogs.commands_cog import CommandsCog
from cogs.xp_cog import XPCog

logger = logging.getLogger(__name__)


class AdminCog(commands.Cog):
    """Commandes administratives en préfixe `!` pour la gestion du bot."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="reload_all")
    @commands.is_owner()
    async def reload_all(self, ctx: commands.Context) -> None:
        """Recharge tous les cogs dynamiquement sans redémarrer le bot."""
        failures = []
        for ext in list(self.bot.extensions):
            try:
                await self.bot.reload_extension(ext)
                embed = discord.Embed(
                    title="🔄 Reload Cog",
                    description=f"{ext} rechargé",
                    colour=0xFE6A33,
                )
                await ctx.send(embed=embed)
            except Exception as e:
                failures.append(f"{ext} ({e})")
        if failures:
            embed = discord.Embed(
                title="⚠️ Échecs", description="\n".join(failures), colour=0xFE6A33
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="✅ Reload terminé",
                description="Tous les cogs ont été rechargés avec succès!",
                colour=0xFE6A33,
            )
            await ctx.send(embed=embed)

    @commands.command(name="reset_cache")
    @commands.is_owner()
    async def reset_cache(self, ctx: commands.Context) -> None:
        """
        Réinitialise les caches (XP et leaderboard) de manière sécurisée.
        Sauvegarde d'abord les données XP en attente pour éviter toute perte.
        """
        # 1. Sauvegarder les données du cache XP avant de le vider.
        xp_cog: XPCog | None = self.bot.get_cog("XPCog")
        if xp_cog:
            logger.info(
                f"[AdminCog] Forcing flush of {len(xp_cog._dirty)} users before reset."
            )
            for uid in list(xp_cog._dirty):
                if uid in xp_cog._cache:
                    save_user(uid, xp_cog._cache[uid])
            xp_cog._dirty.clear()
            xp_cog._cache.clear()
            logger.info("[AdminCog] XP cache flushed and cleared.")

        # 2. Reconstruire le cache du leaderboard.
        rebuild_leaderboard_cache()
        cmd_cog: CommandsCog | None = self.bot.get_cog("CommandsCog")
        if cmd_cog:
            # Notifie le cog de commandes de réinitialiser son propre minuteur.
            cmd_cog.reset_leaderboard_cache_timer()
            logger.info(
                "[AdminCog] Leaderboard cache rebuilt and CommandsCog timer reset."
            )

        embed = discord.Embed(
            title="♻️ Cache réinitialisé",
            description="Caches (XP & leaderboard) réinitialisés en toute sécurité !",
            colour=0xFE6A33,
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCog(bot))
