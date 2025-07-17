"""Cog pour les commandes utilisateur de base (leaderboard, rank, sac)."""

import logging
import time
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from config import BotConfig, VisualConfig
from db import fetch_user, get_leaderboard_from_cache, rebuild_leaderboard_cache
from utils import MAX_LEVEL, XP_CUM_TABLE, make_progress_bar


logger = logging.getLogger(__name__)


class CommandsCog(commands.Cog):
    """Regroupe les commandes slash accessibles aux utilisateurs."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialise le cog des commandes.

        Args:
            bot: L'instance du bot Discord.
        """
        self.bot = bot
        self._lb_last_rebuild: float = 0.0
        self._lb_ttl: float = 30.0  # Durée de vie du cache du leaderboard

    def reset_leaderboard_cache_timer(self) -> None:
        """Réinitialise le minuteur du cache, forçant une reconstruction."""
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

        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "Erreur : impossible de récupérer les informations du serveur.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"{VisualConfig.EMOJIS['trophy']} Leaderboard XP",
            description=f"Consultez le [classement complet sur le site web]({BotConfig.WEB_URL}) !",
            colour=VisualConfig.THEME_COLOR,  # <-- MODIFICATION: Utilisation de la couleur du thème
        )

        for idx, user_data in enumerate(lb_data[:10], start=1):
            member = guild.get_member(user_data["user_id"])

            if member:
                display_name = member.display_name
            else:
                display_name = (
                    user_data.get("nick")
                    or f"Utilisateur parti ({user_data['user_id']})"
                )

            embed.add_field(
                name=f"{idx}. {display_name}",
                value=f"Level {user_data['level']} – {user_data['xp']:,} XP",
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
        self, interaction: discord.Interaction, user: Optional[discord.Member] = None
    ) -> None:
        """Affiche les statistiques détaillées d'un utilisateur."""
        target = user or interaction.user
        data = fetch_user(target.id)
        lvl, xp = data.get("level", 0), data.get("xp", 0)

        if lvl < MAX_LEVEL:
            xmin = XP_CUM_TABLE[lvl]
            xmax = XP_CUM_TABLE[lvl + 1]
            cur = xp - xmin
            needed = xmax - xmin
        else:
            cur = 1
            needed = 1

        bar = make_progress_bar(cur, needed)

        # --- MODIFICATION: Arrondir les valeurs d'XP pour l'affichage ---
        display_cur = int(cur)
        display_needed = int(needed)

        embed = discord.Embed(
            title=f"📊 Rang de {target.display_name}",
            colour=VisualConfig.THEME_COLOR,  # <-- MODIFICATION: Utilisation de la couleur du thème
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Niveau", value=str(lvl), inline=True)
        embed.add_field(name="XP totale", value=f"{xp:,}", inline=True)
        embed.add_field(
            name=f"Progression vers {lvl+1}",
            value=f"{display_cur:,}/{display_needed:,} XP\n{bar}", # <-- MODIFICATION: Utilisation des valeurs arrondies
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
        money = data.get("coins", 0)
        items = data.get("items", [])

        text = f"🔥 **Ignis :** {money:,} IG\n\n"
        text += "🎒 **Objets :** " + (", ".join(items) if items else "— Aucun objet —")

        embed = discord.Embed(
            title=f"🎒 Sac de {interaction.user.display_name}",
            description=text,
            colour=VisualConfig.THEME_COLOR, # <-- MODIFICATION: Cohérence de la couleur
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
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
    """Fonction d'entrée pour charger le cog."""
    await bot.add_cog(CommandsCog(bot))