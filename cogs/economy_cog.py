"""Cog gérant la boutique via une interface utilisateur persistante."""

import logging
from typing import Any

import discord
from discord.ext import commands

from config import EconomyConfig, VisualConfig
from economy_service import EconomyService, InsufficientFunds
from utils import is_nickname_valid

logger = logging.getLogger(__name__)


# --- MODAL POUR LE CHANGEMENT DE PSEUDO ---
class NicknameModal(discord.ui.Modal):
    """Fenêtre modale pour demander le nouveau pseudo à l'utilisateur."""

    def __init__(self, item_id: str, service: EconomyService):
        super().__init__(title="Changement de Pseudo")
        self.item_id = item_id
        self.item_info = EconomyConfig.ITEMS[item_id]
        self.service = service

        self.new_nick = discord.ui.TextInput(
            label="Nouveau pseudo souhaité",
            placeholder="Entrez votre nouveau pseudo ici...",
            min_length=2,
            max_length=32,
        )
        self.add_item(self.new_nick)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Gère la soumission du formulaire."""
        nickname = self.new_nick.value
        price = self.item_info.get("price", 0)

        if not isinstance(price, int):
            await interaction.response.send_message(
                "Erreur de configuration de l'objet.", ephemeral=True
            )
            return

        if not is_nickname_valid(nickname):
            await interaction.response.send_message(
                "Ce pseudo n'est pas autorisé car il contient des termes interdits.",
                ephemeral=True,
            )
            return

        try:
            self.service.purchase(interaction.user.id, price, self.item_id)
            await interaction.user.edit(nick=nickname)
            await interaction.response.send_message(
                f"Félicitations ! Votre pseudo a été changé en **{nickname}**.",
                ephemeral=True,
            )
        except InsufficientFunds as e:
            await interaction.response.send_message(str(e), ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                "Je n'ai pas la permission de changer votre pseudo. "
                "Contactez un administrateur.",
                ephemeral=True,
            )
        except Exception as e:
            logger.error(f"Erreur lors du changement de pseudo : {e}", exc_info=True)
            await interaction.response.send_message(
                "Une erreur est survenue lors de l'achat.", ephemeral=True
            )


# --- BOUTON D'ACHAT GÉNÉRIQUE ---
class PurchaseButton(discord.ui.Button["ShopView"]):
    """Bouton personnalisé pour un objet de la boutique."""

    def __init__(self, item_id: str, item_data: dict[str, Any]):
        """Initialise le bouton."""
        super().__init__(
            label=f"{item_data.get('price', 0):,} Ignis",
            style=discord.ButtonStyle.secondary,
            custom_id=f"buy_{item_id}",
            emoji="🛒",
        )
        self.item_id = item_id
        self.item_info = item_data

    async def callback(self, interaction: discord.Interaction):
        """Définit l'action lors du clic sur le bouton."""
        await interaction.response.defer(ephemeral=True)

        service: EconomyService = self.view.service
        price = self.item_info.get("price", 0)

        if not isinstance(price, int):
            await interaction.followup.send("Erreur de configuration de l'objet.")
            return

        # Cas spécial pour les objets nécessitant une saisie utilisateur
        if self.item_id == "temp_nick_self":
            modal = NicknameModal(item_id=self.item_id, service=service)
            await interaction.response.send_modal(
                modal
            )  # Correction: on_submit s'en occupe
            return

        # Logique d'achat standard pour les autres objets
        try:
            service.purchase(interaction.user.id, price, self.item_id)
            embed = discord.Embed(
                title="✅ Achat Réussi !",
                description=f"Vous avez acheté : **{self.item_info['name']}**.",
                colour=VisualConfig.COLORS["success"],
            )
            await interaction.followup.send(embed=embed)
        except InsufficientFunds as e:
            embed = discord.Embed(
                title=f"{VisualConfig.EMOJIS['error']} Fonds Insuffisants",
                description=str(e),
                colour=VisualConfig.COLORS["error"],
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Erreur d'achat pour {self.item_id}: {e}", exc_info=True)
            await interaction.followup.send("Oups, une erreur est survenue.")


# --- VUE PERSISTANTE DE LA BOUTIQUE ---
class ShopView(discord.ui.View):
    """Vue contenant les embeds et boutons de tous les objets."""

    def __init__(self):
        """Initialise la vue en ajoutant un bouton pour chaque objet."""
        super().__init__(timeout=None)
        self.service = EconomyService()

        for key, item_data in EconomyConfig.ITEMS.items():
            if isinstance(item_data, dict):
                # Crée un Embed pour chaque objet
                embed = discord.Embed(
                    title=f"{item_data.get('name', 'Objet Inconnu')}",
                    description=item_data.get("description", "Aucune description."),
                    colour=VisualConfig.THEME_COLOR,
                )
                # Ajoute un bouton d'achat spécifique à cet objet
                # Le bouton est ajouté via un `ShopItemContainer`
                container = ShopItemContainer(
                    embed=embed, item_id=key, item_data=item_data
                )
                self.add_item(container.button)


class ShopItemContainer:
    """Helper pour associer un embed et un bouton. Non ajouté à la vue directement."""

    def __init__(self, embed: discord.Embed, item_id: str, item_data: dict):
        self.embed = embed
        self.button = PurchaseButton(item_id=item_id, item_data=item_data)


# --- COG ECONOMIQUE ---
class EconomyCog(commands.Cog):
    """Gère l'interface de la boutique."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialise le cog économique."""
        self.bot = bot
        self.service = EconomyService()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """S'assure que la vue de la boutique est bien enregistrée au démarrage."""
        self.bot.add_view(ShopView())
        logger.info("[EconomyCog] Vue de la boutique persistante enregistrée.")


async def setup(bot: commands.Bot) -> None:
    """Fonction d'entrée pour charger le cog."""
    await bot.add_cog(EconomyCog(bot))
