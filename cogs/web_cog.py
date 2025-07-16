"""Cog pour le serveur web Flask."""

import html
import logging
import math
import os
from threading import Thread

from discord.ext import commands
from flask import Flask, render_template, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from werkzeug.serving import make_server

from config import VisualConfig
from db import get_leaderboard_from_cache
from utils import XP_CUM_TABLE


logger = logging.getLogger(__name__)

HERE = os.path.dirname(__file__)
TEMPLATES = os.path.abspath(os.path.join(HERE, "..", "templates"))

app = Flask(__name__, template_folder=TEMPLATES)
app.jinja_env.autoescape = True
app.jinja_env.globals.update(VisualConfig=VisualConfig, enumerate=enumerate)

LOGS_SECRET_KEY = os.environ.get("LOGS_SECRET_KEY")
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests")


@app.before_request
def _before_request():
    """Incrémente le compteur de requêtes avant chaque requête."""
    REQUEST_COUNT.inc()


@app.route("/")
def home():
    """Endpoint principal pour vérifier que le serveur est en ligne."""
    return "Bot is alive and web server is running!", 200


@app.route("/healthz")
def healthz():
    """Endpoint de santé pour les systèmes de monitoring."""
    return "OK", 200


@app.route("/metrics")
def metrics():
    """Endpoint pour exposer les métriques au format Prometheus."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route("/logs")
def logs():
    """Endpoint sécurisé pour afficher les derniers logs du bot."""
    if not LOGS_SECRET_KEY or request.args.get("key") != LOGS_SECRET_KEY:
        return "Accès non autorisé", 403

    log_path = os.environ.get("LOG_PATH", "bot.log")
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            data = f.read()[-5000:]
        return f"<pre>{data}</pre>", 200
    except Exception as e:
        logger.exception("Erreur en lisant les logs", exc_info=e)
        return f"Erreur en lisant les logs : {e}", 500


def xp_bounds(level: int) -> tuple[int, int]:
    """Calcule les bornes d'XP pour un niveau donné."""
    if level < 1:
        return 0, int(XP_CUM_TABLE[1]) if len(XP_CUM_TABLE) > 1 else 0
    if level >= len(XP_CUM_TABLE) - 1:
        return int(XP_CUM_TABLE[-2]), int(XP_CUM_TABLE[-1])
    return int(XP_CUM_TABLE[level]), int(XP_CUM_TABLE[level + 1])


@app.route("/leaderboard")
def leaderboard():
    """Affiche la page web du leaderboard complet et paginé."""
    page = max(int(request.args.get("page", 1)), 1)
    per_page = int(request.args.get("per_page", 50))
    if per_page not in (50, 100, 200):
        per_page = 50

    cached = get_leaderboard_from_cache()
    members = []
    for d in cached:
        xp = d.get("xp", 0)
        lvl = d.get("level", 0)

        name = html.escape(d.get("nick") or f"Utilisateur {d.get('user_id')}")
        avatar = d.get("avatar") or "https://cdn.discordapp.com/embed/avatars/0.png"

        xmin, xmax = xp_bounds(lvl)
        pct = int((xp - xmin) / (xmax - xmin) * 100) if xmax > xmin else 100

        members.append(
            {
                "uid": d["user_id"],
                "name": name,
                "avatar": avatar,
                "level": lvl,
                "xp": xp,
                "percent": pct,
            }
        )

    total = len(members)
    pages = math.ceil(total / per_page) if total else 1
    if page > pages:
        page = pages
    start = (page - 1) * per_page
    entries = members[start : start + per_page]

    return (
        render_template(
            "leaderboard.html",
            entries=entries,
            page=page,
            per_page=per_page,
            start=start,
            pages=pages,
        ),
        200,
    )


class WebCog(commands.Cog):
    """Cog qui gère le cycle de vie du serveur web Flask."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialise le cog et démarre le serveur web dans un thread séparé."""
        super().__init__()
        self.bot = bot
        port = int(os.environ.get("PORT", 3000))
        self._server = make_server("0.0.0.0", port, app)
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        logger.info(
            f"{VisualConfig.EMOJIS['web']} Serveur web démarré sur 0.0.0.0:{port}"
        )

    def cog_unload(self) -> None:
        """Arrête proprement le serveur Flask lors du déchargement du cog."""
        logger.info(f"{VisualConfig.EMOJIS['web']} Arrêt du serveur Flask…")
        self._server.shutdown()
        self._thread.join(timeout=5)
        logger.info(f"{VisualConfig.EMOJIS['web']} Serveur Flask arrêté.")


async def setup(bot: commands.Bot) -> None:
    """Fonction d'entrée pour charger le cog."""
    await bot.add_cog(WebCog(bot))
