"""Cog gérant la logique de gain d'XP, niveaux et récompenses.

Ce module contient le listener on_message qui est le cœur du système de
progression. Il utilise le modèle "Spline Unifiée" pour une expérience
équilibrée et sophistiquée.
"""

import logging
import random
from datetime import datetime

import discord
from discord.ext import commands, tasks

from config import XPConfig, StyleConfig
from db import fetch_user, save_user
from utils import XP_CUM_TABLE, calculer_bonus_de_palier, MAX_LEVEL


logger = logging.getLogger(__name__)


class XPCog(commands.Cog):
    """Gère la logique de gain d'XP avec le système Spline Unifiée."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialise le cog XP."""
        self.bot = bot
        self._cache: dict[int, dict] = {}
        self._dirty: set[int] = set()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Démarre les tâches de fond lorsque le bot est prêt."""
        if not self._flush_loop.is_running():
            self._flush_loop.start()
        logger.info("[XPCog] Cog XP prêt avec le système Spline Unifiée.")

    @tasks.loop(seconds=60)
    async def _flush_loop(self) -> None:
        """Sauvegarde périodiquement les données modifiées en base de données."""
        if not self._dirty:
            return

        dirty_users_to_save = list(self._dirty)
        logger.info(f"[XPCog] Flush de {len(dirty_users_to_save)} utilisateurs en BDD")

        for uid in dirty_users_to_save:
            if uid in self._cache:
                save_user(self._cache[uid])
                self._dirty.discard(uid)

    @_flush_loop.before_loop
    async def _before_flush(self) -> None:
        """Attend que le bot soit prêt avant de démarrer la boucle de sauvegarde."""
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        """Traite chaque message pour attribuer de l'XP et des récompenses."""
        # --- Étape 1: Vérifications initiales ---
        if msg.author.bot or msg.guild is None:
            return

        has_media = bool(msg.attachments or msg.stickers or msg.embeds)
        content = msg.content.strip()
        if not has_media and len(content) < XPConfig.MIN_LEN:
            return

        uid = msg.author.id
        now = datetime.utcnow()

        # --- Étape 2: Gestion du cache et du cooldown ---
        if uid not in self._cache:
            self._cache[uid] = fetch_user(uid)
        user = self._cache[uid]

        if (
            (now - user.get("last_ts", datetime.min)).total_seconds()
            < XPConfig.COOLDOWN
        ):
            return

        if user.get("nick") != msg.author.display_name:
            user["nick"] = msg.author.display_name
            self._dirty.add(uid)

        # --- Étape 3: Logique de gain d'XP et d'or ---
        today = now.date()
        last_daily_date = user.get("last_daily")
        # Assurer la compatibilité si last_daily est un datetime
        if isinstance(last_daily_date, datetime):
            last_daily_date = last_daily_date.date()

        if last_daily_date != today:
            user["messages_today"] = 0
            user["last_daily"] = today

        user["messages_today"] = user.get("messages_today", 0) + 1
        daily_msg_count = user["messages_today"]

        # Calcul du gain d'XP avec la formule Spline Unifiée
        xp_gain = round(200 / (1 + XPConfig.PHI * daily_msg_count))

        # Calcul du gain d'or (logique économique conservée)
        if daily_msg_count <= XPConfig.MONEY_PER_MESSAGE_LIMIT:
            user["coins"] = user.get("coins", 0) + XPConfig.MONEY_PER_MESSAGE_AMOUNT

        if xp_gain > 0:
            user["xp"] = user.get("xp", 0) + xp_gain

            # --- Étape 4: Logique de Level-Up (robuste avec boucle while) ---
            old_level = user.get("level", 0)
            new_level = old_level

            while new_level < MAX_LEVEL and user["xp"] >= XP_CUM_TABLE[new_level + 1]:
                new_level += 1

                bonus = calculer_bonus_de_palier(new_level)
                if bonus > 0:
                    user["coins"] += bonus
                    bonus_msg = (
                        f"\n💰 **PALIER {new_level} ATTEINT !** +{bonus:,} Ignis"
                    )
                else:
                    bonus_msg = ""

                msg_text = random.choice(StyleConfig.LEVEL_UP_MESSAGES)
                embed = discord.Embed(
                    title=f"{msg.author.display_name} → Niveau {new_level}",
                    description=f"{msg_text}{StyleConfig.EMOJI_KERMIT}{bonus_msg}",
                    colour=0xFE6A33,
                )
                embed.set_thumbnail(url=msg.author.display_avatar.url)
                await msg.channel.send(embed=embed)

            if new_level > old_level:
                user["level"] = new_level
                if old_level == 0 and isinstance(msg.author, discord.Member):
                    role = discord.utils.get(
                        msg.guild.roles, name=StyleConfig.ROLE_CITIZEN
                    )
                    if role and role not in msg.author.roles:
                        try:
                            await msg.author.add_roles(
                                role, reason="Atteinte du premier niveau"
                            )
                        except discord.Forbidden:
                            logger.warning(
                                f"Permissions manquantes pour ajouter le rôle "
                                f"{StyleConfig.ROLE_CITIZEN} à {msg.author.name}"
                            )

        # --- Étape 5: Finalisation ---
        user["last_ts"] = now
        self._dirty.add(uid)

    def cog_unload(self) -> None:
        """Arrête proprement les tâches de fond lors du déchargement du cog."""
        logger.info("[XPCog] Unload: flush final des données en attente.")

        dirty_users_to_save = list(self._dirty)
        for uid in dirty_users_to_save:
            if uid in self._cache:
                save_user(self._cache[uid])

        self._flush_loop.cancel()


async def setup(bot: commands.Bot) -> None:
    """Fonction d'entrée pour charger le cog."""
    await bot.add_cog(XPCog(bot))