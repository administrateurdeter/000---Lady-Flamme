"""
Cog pour le serveur web Flask qui expose le leaderboard.
"""

import os
import math
import logging
from flask import Flask, render_template, request
from threading import Thread
from discord.ext import commands
from werkzeug.serving import make_server
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

from config import VisualConfig
from db import get_leaderboard_from_cache
from utils import xp_cum

logger = logging.getLogger(__name__)

# --- Résolution du dossier templates en absolu ---
HERE = os.path.dirname(__file__)
TEMPLATES = os.path.abspath(os.path.join(HERE, "..", "templates"))

# Création de l'app Flask en pointant sur templates abs.
app = Flask(__name__, template_folder=TEMPLATES)
app.jinja_env.autoescape = True

# Injection de VisualConfig et de enumerate dans l'environnement Jinja
app.jinja_env.globals.update(VisualConfig=VisualConfig, enumerate=enumerate)

# --- Prometheus metrics ---
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests")

@app.before_request
def _before_request():
    REQUEST_COUNT.inc()

@app.route("/")
def home():
    """Page d'accueil simple pour vérifier que le serveur web est en ligne."""
    return "Bot is alive and web server is running!", 200

@app.route("/healthz")
def healthz():
    """Endpoint santé pour le monitoring."""
    return "OK", 200

@app.route("/metrics")
def metrics():
    """Exposition des métriques Prometheus."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@app.route("/logs")
def logs():
    """Affiche les 5000 derniers caractères du fichier de log. Utile pour le débogage."""
    log_path = os.environ.get("LOG_PATH", "bot.log")
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            data = f.read()[-5000:]
        return f"<pre>{data}</pre>", 200
    except Exception as e:
        logger.exception("Erreur en lisant les logs", exc_info=e)
        return f"Erreur en lisant les logs : {e}", 500

def xp_bounds(level: int):
    """Calcule l'XP min et max pour un niveau donné."""
    if level < 1:
        return 0, xp_cum[0] if xp_cum else 0
    if level >= len(xp_cum):
        return xp_cum[-2], xp_cum[-1]
    return xp_cum[level - 1], xp_cum[level]

@app.route("/leaderboard")
def leaderboard():
    """Affiche la page web du leaderboard complet."""
    page = max(int(request.args.get("page", 1)), 1)
    per_page = int(request.args.get("per_page", 50))
    if per_page not in (50, 100, 200):
        per_page = 50

    cached = get_leaderboard_from_cache()
    members = []
    for d in cached:
        xp = d.get("xp", 0)
        lvl = d.get("level", 0)
        name = d.get("nick") or f"Utilisateur {d.get('user_id')}"
        avatar = d.get("avatar") or "https://cdn.discordapp.com/embed/avatars/0.png"
        xmin, xmax = xp_bounds(lvl)
        pct = int((xp - xmin) / (xmax - xmin) * 100) if xmax > xmin else 100
        members.append({
            "uid": d["user_id"],
            "name": name,
            "avatar": avatar,
            "level": lvl,
            "xp": xp,
            "percent": pct,
        })

    total = len(members)
    pages = math.ceil(total / per_page) if total else 1
    if page > pages:
        page = pages
    start = (page - 1) * per_page
    entries = members[start : start + per_page]

    return render_template(
        "leaderboard.html",
        entries=entries,
        page=page,
        per_page=per_page,
        start=start,
        pages=pages
    ), 200

class WebCog(commands.Cog):
    """Lance le serveur web Flask dans un thread et gère son arrêt propre."""

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        port = int(os.environ.get("PORT", 3000))
        self._server = make_server("0.0.0.0", port, app)
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        logger.info(f"{VisualConfig.EMOJIS['web']} Serveur web démarré en arrière-plan sur 0.0.0.0:{port}")

    def cog_unload(self) -> None:
        """Arrêt propre du serveur web."""
        logger.info(f"{VisualConfig.EMOJIS['web']} WebCog déchargé – arrêt du serveur Flask…")
        self._server.shutdown()
        self._thread.join(timeout=5)
        logger.info(f"{VisualConfig.EMOJIS['web']} Serveur Flask arrêté.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WebCog(bot))
