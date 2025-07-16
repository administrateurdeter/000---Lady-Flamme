"""Cog pour la boutique et les commandes économiques."""

import logging

import discord
from discord import app_commands
from discord.ext import commands

from config import BotConfig, EconomyConfig, VisualConfig
from economy_service import EconomyService, InsufficientFunds

logger = logging.getLogger(__name__)


class EconomyCog(commands.Cog):
    """Gère les commandes liées à l'économie, comme l'achat d'objets."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialise le cog économique."""
        self.bot = bot
        self.service = EconomyService()

    @app_commands.command(
        name="shop", description="Affiche les objets disponibles à l'achat."
    )
    @app_commands.guilds(discord.Object(id=BotConfig.GUILD_ID))
    async def shop(self, interaction: discord.Interaction) -> None:
        """Affiche la liste des objets de la boutique."""
        embed = discord.Embed(
            title="🔥 Boutique d'Ignis 🔥",
            description="Utilisez `/buy <id_objet>` pour acheter.",
            colour=0xFE6A33,
        )
        for key, item_data in EconomyConfig.ITEMS.items():
            desc = (
                f"Prix : **{item_data['price']:,}** Ignis\n"
                f"*Description : {item_data['description']}*"
            )
            embed.add_field(
                name=f"**{item_data['name']}** - `{key}`", value=desc, inline=False
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="buy", description="Acheter un objet dans la boutique.")
    @app_commands.guilds(discord.Object(id=BotConfig.GUILD_ID))
    @app_commands.describe(
        item="L'identifiant de l'objet à acheter (ex: spy, xp_block)."
    )
    async def buy(self, interaction: discord.Interaction, item: str) -> None:
        """Gère la logique d'achat d'un objet par un utilisateur."""
        item_key = item.lower()

        if item_key not in EconomyConfig.ITEMS:
            embed = discord.Embed(
                title=f"{VisualConfig.EMOJIS['error']} Objet introuvable",
                description=(
                    f"L'objet `{item_key}` n'existe pas. Utilisez `/shop` "
                    "pour voir les objets disponibles."
                ),
                colour=VisualConfig.COLORS["error"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        item_data = EconomyConfig.ITEMS[item_key]
        price = int(item_data["price"])
        name = str(item_data["name"])
        user_id = interaction.user.id

        try:
            self.service.purchase(user_id=user_id, price=price, item_name=name)

            embed = discord.Embed(
                title=f"{VisualConfig.EMOJIS['success']} Achat réussi !",
                description=f"Vous avez acheté **{name}** pour {price:,} Ignis.",
                colour=VisualConfig.COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except InsufficientFunds as e:
            embed = discord.Embed(
                title=f"{VisualConfig.EMOJIS['warning']} Fonds insuffisants",
                description=str(e),
                colour=VisualConfig.COLORS["warning"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'achat par {user_id}", exc_info=e)
            embed = discord.Embed(
                title=f"{VisualConfig.EMOJIS['error']} Erreur Interne",
                description=(
                    "Une erreur inattendue est survenue. " "L'équipe a été notifiée."
                ),
                colour=VisualConfig.COLORS["error"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """Fonction d'entrée pour charger le cog."""
    await bot.add_cog(EconomyCog(bot))
