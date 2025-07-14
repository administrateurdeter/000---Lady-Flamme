"""
Cog pour la boutique et les commandes économiques.
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands
from config import BotConfig, EconomyConfig
from economy_service import EconomyService, InsufficientFunds

logger = logging.getLogger(__name__)


class EconomyCog(commands.Cog):
    """Gère les commandes liées à l'économie, comme l'achat d'objets."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.service = EconomyService()

    @app_commands.command(
        name="buy", description="(MASQUÉ) Acheter un objet dans la boutique."
    )
    @app_commands.guilds(discord.Object(id=BotConfig.GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(item="Clé de l’objet (ex. `paypal`, `spy`, etc.)")
    async def buy(self, interaction: discord.Interaction, item: str) -> None:
        """Commande pour acheter un objet. Temporairement désactivée."""
        # TODO: Implémenter la logique d'achat en utilisant self.service.purchase
        # et en vérifiant que 'item' existe dans EconomyConfig.ITEMS.
        embed = discord.Embed(
            title="❌ Boutique fermée",
            description="La boutique est momentanément fermée.",
            colour=0xFE6A33,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EconomyCog(bot))
