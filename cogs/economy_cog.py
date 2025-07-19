"""Cog pour la boutique et les commandes économiques."""

import logging

import discord
from discord import app_commands
from discord.ext import commands

from config import BotConfig, EconomyConfig, VisualConfig
from economy_service import EconomyService, InsufficientFunds
from utils import is_nickname_valid  # Importation du nouveau filtre

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
            colour=VisualConfig.THEME_COLOR,
        )
        for key, item_data in EconomyConfig.ITEMS.items():
            if isinstance(item_data, dict):
                price = item_data.get("price", "N/A")
                description = item_data.get("description", "Aucune description.")
                name = item_data.get("name", "Objet inconnu")

                desc_text = (
                    f"Prix : **{price:,}** Ignis\n" f"*Description : {description}*"
                )
                embed.add_field(
                    name=f"**{name}** - `{key}`", value=desc_text, inline=False
                )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="buy", description="Acheter un objet dans la boutique.")
    @app_commands.guilds(discord.Object(id=BotConfig.GUILD_ID))
    @app_commands.describe(
        item_id="L'identifiant de l'objet à acheter (ex: temp_nick_self)."
    )
    async def buy(self, interaction: discord.Interaction, item_id: str) -> None:
        """Gère la logique d'achat d'un objet par un utilisateur."""
        item_key = item_id.lower()

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

        # --- Logique d'achat à implémenter ---
        # Cette section sera développée pour gérer chaque objet.
        # Par exemple, pour un achat de pseudo, il faudrait ouvrir un Modal,
        # récupérer le texte, le valider avec is_nickname_valid,
        # déduire l'argent et appliquer le changement.

        embed = discord.Embed(
            title="✅ Commande Reçue",
            description=(
                f"Vous souhaitez acheter l'objet `{item_key}`. "
                "La logique d'achat est en cours de développement."
            ),
            colour=VisualConfig.COLORS["info"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """Fonction d'entrée pour charger le cog."""
    await bot.add_cog(EconomyCog(bot))
