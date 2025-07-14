"""
Cog pour les commandes utilisateur de base (leaderboard, rank, sac).
"""

import time
import math
import logging

import discord
from discord import app_commands
from discord.ext import commands

from config import BotConfig, VisualConfig
from db import rebuild_leaderboard_cache, get_leaderboard_from_cache, fetch_user
from utils import xp_cum, total_xp_to_level, make_progress_bar

logger = logging.getLogger(__name__)


class CommandsCog(commands.Cog):
    """Regroupe les commandes slash accessibles aux utilisateurs."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._lb_last_rebuild: float = 0.0
        # Durée de vie du cache du leaderboard en secondes pour éviter les reconstructions trop fréquentes.
        self._lb_ttl: float = 30.0

    def reset_leaderboard_cache_timer(self) -> None:
        """Réinitialise le minuteur du cache, forçant une reconstruction à la prochaine commande."""
        self._lb_last_rebuild = 0.0
        logger.info("[CommandsCog] Leaderboard cache timer has been reset.")

    @app_commands.command(
        name="leaderboard", description="Affiche le top 10 des meilleurs niveaux et XP."
    )
    @app_commands.guilds(discord.Object(id=BotConfig.GUILD_ID))
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        """Affiche le top 10 du classement général."""
        now = time.time()
        if now - self._lb_last_rebuild > self._lb_ttl:
            rebuild_leaderboard_cache()
            self._lb_last_rebuild = now
            logger.info("[CommandsCog] Central leaderboard cache rebuilt on demand.")

        lb_data = get_leaderboard_from_cache()

        embed = discord.Embed(
            title=f"{VisualConfig.EMOJIS['trophy']} Leaderboard XP",
            description=f"Consultez le [classement complet sur le site web]({BotConfig.WEB_URL}) !",
            colour=VisualConfig.COLORS["info"],
        )
        for idx, user in enumerate(lb_data[:10], start=1):
            embed.add_field(
                name=f"{idx}. {user['nick'] or user['user_id']}",
                value=f"Level {user['level']} – {user['xp']} XP",
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="rank", description="Affiche ton niveau, ton XP et ta progression."
    )
    @app_commands.guilds(discord.Object(id=BotConfig.GUILD_ID))
    @app_commands.describe(
        user="L’utilisateur dont tu veux voir le rang (par défaut : toi)."
    )
    async def rank(
        self, interaction: discord.Interaction, user: discord.Member | None = None
    ) -> None:
        """Affiche les statistiques détaillées d'un utilisateur."""
        target = user or interaction.user
        data = fetch_user(target.id)
        lvl, xp = data["level"], data["xp"]

        # Calcul de la progression dans le palier actuel
        if lvl < len(xp_cum):
            xmin = xp_cum[lvl - 1] if lvl > 0 else 0
            xmax = xp_cum[lvl]
            cur = xp - xmin
        else:  # Niveau max atteint
            xmin, xmax = xp_cum[-2], xp_cum[-1]
            cur = xp - xmin

        needed = xmax - xmin
        bar = make_progress_bar(cur, needed)

        embed = discord.Embed(
            title=f"📊 Rang de {target.display_name}",
            colour=VisualConfig.COLORS["info"],
        )
        embed.add_field(name="Niveau", value=str(lvl), inline=True)
        embed.add_field(name="XP totale", value=str(xp), inline=True)
        embed.add_field(
            name=f"Progression vers {lvl+1}",
            value=f"{cur}/{needed} XP\n{bar}",
            inline=False,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="sac", description="Affiche tes Ignis et les objets de ton inventaire."
    )
    @app_commands.guilds(discord.Object(id=BotConfig.GUILD_ID))
    async def sac(self, interaction: discord.Interaction) -> None:
        """Affiche l'argent et l'inventaire de l'utilisateur."""
        data = fetch_user(interaction.user.id)
        money = data["money"]
        items = data.get("inventory", {}).get("items", [])
        text = f"🔥 **Ignis :** {money} IG\n"
        text += "🎒 **Objets :** " + (", ".join(items) if items else "— Aucun objet —")

        embed = discord.Embed(
            title="🎒 Ton sac", description=text, colour=VisualConfig.COLORS["info"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_app_command_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        """Gestionnaire d'erreurs global pour les commandes de ce cog."""
        logger.error(
            f"Erreur commande {interaction.command.name} → {error}", exc_info=True
        )
        try:
            embed = discord.Embed(
                title=f"{VisualConfig.EMOJIS['warning']} Erreur",
                description="Une erreur est survenue, réessaie dans un instant.",
                colour=VisualConfig.COLORS["error"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CommandsCog(bot))
