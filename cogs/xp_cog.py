import logging
import random
from datetime import datetime, time as dt_time
import discord
from discord.ext import commands, tasks
from db import fetch_user, save_user
from utils import total_xp_to_level, calculer_bonus_de_palier
from config import XPConfig, StyleConfig

logger = logging.getLogger(__name__)


class XPCog(commands.Cog):
    """Gère la logique de gain d'XP, niveaux et récompenses."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._cache: dict[int, dict] = {}
        self._dirty: set[int] = set()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Démarre les tasks quand le bot est prêt."""
        if not self._flush_loop.is_running():
            self._flush_loop.start()
        if not self._daily_reset.is_running():
            self._daily_reset.start()
        logger.info(
            "[XPCog] Tasks _flush_loop et _daily_reset démarrées après on_ready."
        )

    @tasks.loop(seconds=60)
    async def _flush_loop(self) -> None:
        """Tâche de fond pour sauvegarder périodiquement les données modifiées."""
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
        await self.bot.wait_until_ready()

    @tasks.loop(time=dt_time(hour=0, minute=0, second=5))
    async def _daily_reset(self) -> None:
        """Reset quotidien des compteurs journaliers."""
        self._cache.clear()
        self._dirty.clear()
        logger.info("[XPCog] Cache local vidé pour le reset quotidien.")

    @_daily_reset.before_loop
    async def _before_daily(self) -> None:
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        if msg.author.bot or msg.guild is None:
            return

        has_media = bool(msg.attachments or msg.stickers or msg.embeds)
        content = msg.content.strip()
        if not has_media and len(content) < XPConfig.MIN_LEN:
            return

        uid = msg.author.id
        now = datetime.utcnow()

        if uid not in self._cache:
            self._cache[uid] = fetch_user(uid)
        user = self._cache[uid]

        # Mise à jour du pseudo si nécessaire
        if user.get("nick") != msg.author.display_name:
            user["nick"] = msg.author.display_name
            self._dirty.add(uid)

        last_ts = user.get("last_ts", datetime.min)
        if (now - last_ts).total_seconds() < XPConfig.COOLDOWN:
            return

        today = now.date()
        last_daily_date = user.get("last_daily")
        if last_daily_date != today:
            user["messages_today"] = 0
            user["daily_xp_gain"] = 0
            user["last_daily"] = today

        user["messages_today"] = user.get("messages_today", 0) + 1
        daily_msg_count = user["messages_today"]
        daily_xp_gain = user.get("daily_xp_gain", 0)

        if daily_msg_count <= XPConfig.MONEY_PER_MESSAGE_LIMIT:
            user["coins"] = user.get("coins", 0) + XPConfig.MONEY_PER_MESSAGE_AMOUNT

        xp_gain = 0
        if daily_xp_gain < XPConfig.XP_DAILY_CAP:
            xp_gain = round(
                XPConfig.XP_FORMULA_BASE
                / (1 + XPConfig.XP_FORMULA_DECAY * daily_msg_count)
            )
            xp_gain = min(xp_gain, XPConfig.XP_DAILY_CAP - daily_xp_gain)

        if xp_gain > 0:
            user["xp"] = user.get("xp", 0) + xp_gain
            user["daily_xp_gain"] = user.get("daily_xp_gain", 0) + xp_gain

            old_level = user.get("level", 0)
            new_level = total_xp_to_level(user["xp"])

            if new_level > old_level:
                user["level"] = new_level
                msg_text = random.choice(StyleConfig.LEVEL_UP_MESSAGES)
                bonus_msg = ""

                for lvl_check in range(old_level + 1, new_level + 1):
                    bonus = calculer_bonus_de_palier(lvl_check)
                    if bonus > 0:
                        user["coins"] = user.get("coins", 0) + bonus
                        bonus_msg += (
                            f"\n💰 **PALIER {lvl_check} ATTEINT !** +{bonus:,} Ignis"
                        )

                embed = discord.Embed(
                    title=f"{msg.author.display_name} → Niveau {new_level}",
                    description=f"{msg_text}{StyleConfig.EMOJI_KERMIT}{bonus_msg}",
                    colour=0xFE6A33,
                )
                embed.set_thumbnail(url=msg.author.display_avatar.url)
                await msg.channel.send(embed=embed)

                if isinstance(msg.author, discord.Member):
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
                                f"Permissions manquantes pour ajouter le rôle {StyleConfig.ROLE_CITIZEN} à {msg.author.name}"
                            )

        user["last_ts"] = now
        self._dirty.add(uid)

    def cog_unload(self) -> None:
        """Arrêt propre, flush final des données."""
        logger.info("[XPCog] Unload: flush final des données en attente.")

        dirty_users_to_save = list(self._dirty)
        for uid in dirty_users_to_save:
            if uid in self._cache:
                save_user(self._cache[uid])

        self._flush_loop.cancel()
        self._daily_reset.cancel()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(XPCog(bot))
