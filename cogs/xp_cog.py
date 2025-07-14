import logging
import random
from datetime import datetime, time as dt_time
import discord
from discord.ext import commands, tasks
from db import fetch_user, save_user, reset_all_daily_counts
from utils import total_xp_to_level
from config import XPConfig, StyleConfig

logger = logging.getLogger(__name__)


class XPCog(commands.Cog):
    """Gère la logique de gain d'XP, niveaux et récompenses."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._cache: dict[int, dict] = {}
        self._dirty: set[int] = set()
        # On **ne démarre plus** les loops ici :
        # self._flush_loop.start()
        # self._daily_reset.start()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Démarre les tasks quand le bot est prêt (uniquement en prod, pas en test)."""
        if not self._flush_loop.is_running():
            self._flush_loop.start()
        if not self._daily_reset.is_running():
            self._daily_reset.start()
        logger.info(
            "[XPCog] Tasks _flush_loop et _daily_reset démarrées après on_ready."
        )

    @tasks.loop(seconds=XPConfig.COOLDOWN)
    async def _flush_loop(self) -> None:
        """Tâche de fond pour sauvegarder périodiquement les données modifiées."""
        if not self._dirty:
            return
        logger.info(f"[XPCog] Flush de {len(self._dirty)} utilisateurs en BDD")
        for uid in list(self._dirty):
            if uid in self._cache:
                save_user(uid, self._cache[uid])
                self._dirty.remove(uid)

    @_flush_loop.before_loop
    async def _before_flush(self) -> None:
        await self.bot.wait_until_ready()

    @tasks.loop(time=dt_time(hour=0, minute=0, second=0))
    async def _daily_reset(self) -> None:
        """Reset quotidien des compteurs journaliers."""
        reset_all_daily_counts()
        logger.info("[XPCog] Counters journaliers réinitialisés.")

    @_daily_reset.before_loop
    async def _before_daily(self) -> None:
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        # Ignore les bots et les DMs
        if msg.author.bot or msg.guild is None:
            return

        has_media = bool(msg.attachments or msg.stickers or msg.embeds)
        content = msg.content.strip()
        if not has_media and len(content) < XPConfig.MIN_LEN:
            return

        uid = msg.author.id
        now = datetime.utcnow()

        # Cache à la demande (premier message)
        if uid not in self._cache:
            self._cache[uid] = fetch_user(uid)
        user = self._cache[uid]

        # Cooldown anti-spam
        last_ts = user.get("last_ts")
        if last_ts and (now - last_ts).total_seconds() < XPConfig.COOLDOWN:
            return

        # Calcul du gain d'XP et d'Ignis
        user["messages_today"] = user.get("messages_today", 0) + 1
        count = user["messages_today"]
        xp_gain = next((xp for limit, xp in XPConfig.XP_ZONES if count <= limit), 1)
        if xp_gain:
            user["xp"] += xp_gain
            user["money"] += XPConfig.COIN_PER_MSG
            old_level = user.get("level", 0)
            new_level = total_xp_to_level(user["xp"])

            if new_level > old_level:
                user["level"] = new_level
                msg_text = random.choice(StyleConfig.LEVEL_UP_MESSAGES)
                bonus_msg = ""
                for lvl, bonus in XPConfig.MONEY_MILESTONES.items():
                    if old_level < lvl <= new_level:
                        user["money"] += bonus
                        bonus_msg = f"\n💰 **PALIER {lvl} atteint !** +{bonus} IG"
                embed = discord.Embed(
                    title=f"{msg.author.display_name} → Niveau {new_level}",
                    description=f"{msg_text}{StyleConfig.EMOJI_KERMIT}{bonus_msg}",
                    colour=0xFE6A33,
                )
                await msg.channel.send(embed=embed)

                # Attribution du rôle Citoyen
                if isinstance(msg.author, discord.Member):
                    role = discord.utils.get(
                        msg.guild.roles, name=StyleConfig.ROLE_CITIZEN
                    )
                    if role and role not in msg.author.roles:
                        await msg.author.add_roles(role)

        user["last_ts"] = now
        self._dirty.add(uid)

    def cog_unload(self) -> None:
        """Arrêt propre, flush final des données."""
        logger.info("[XPCog] Unload: flush final des données en attente.")
        for uid in list(self._dirty):
            if uid in self._cache:
                save_user(uid, self._cache[uid])
                self._dirty.remove(uid)
        self._flush_loop.cancel()
        self._daily_reset.cancel()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(XPCog(bot))
