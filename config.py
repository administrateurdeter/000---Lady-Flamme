"""
Fichier de configuration centralisé.

Ce module charge les variables d'environnement et définit les constantes
de l'application. Pour une meilleure organisation à grande échelle, les
constantes sont regroupées dans des classes dédiées.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class BotConfig:
    """Paramètres essentiels pour la connexion du bot et à la base de données."""

    BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
    GUILD_ID: int = int(os.getenv("GUILD_ID", "0"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    WEB_URL: str = os.getenv("WEB_URL", "http://127.0.0.1:3000/leaderboard")


class XPConfig:
    """Toutes les constantes liées au gain d'expérience et d'or."""

    MIN_LEN: int = 5  # Longueur minimale d'un message pour être éligible à l'XP.
    COOLDOWN: int = 30  # Temps en secondes entre deux messages rapportant de l'XP.

    # Constantes pour la formule de gain d'XP
    XP_FORMULA_BASE: int = 200
    XP_FORMULA_DECAY: float = 0.1
    XP_DAILY_CAP: int = 4000

    # Constantes pour le gain d'or par message ("salaire" quotidien)
    MONEY_PER_MESSAGE_AMOUNT: int = 5
    MONEY_PER_MESSAGE_LIMIT: int = 5


class StyleConfig:
    """Constantes liées aux messages, rôles et emojis pour une identité visuelle cohérente."""

    ROLE_CITIZEN: str = "Citoyen"
    EMOJI_KERMIT: str = "🎉"
    LEVEL_UP_MESSAGES: list[str] = [
        "te voilà plus flamboyant·e que jamais, l’aventure ne fait que commencer !",
        "la chaleur de ta détermination illumine désormais un nouveau niveau.",
        "ta légende s’écrit doucement dans les nuages. Continuons à monter ensemble !",
        "tu franchis les cieux avec élégance, j’admire ta progression !",
        "tu portes désormais haut les couleurs de notre expédition.",
        "ta passion brûle d’un éclat nouveau, je suis fière de toi !",
        "un vent favorable te propulse toujours plus haut. Poursuis ta route !",
        "mon ballon s’élève grâce à ta flamme intérieure : continue ainsi !",
        "ton niveau monte, tout comme la chaleur que tu dégages autour de toi.",
        "la grandeur de ton esprit vient d’atteindre un nouveau palier.",
        "la montgolfière s’élève encore, portée par tes efforts remarquables.",
        "notre voyage commun prend de l’altitude grâce à toi !",
        "tu as franchi un cap : je sens déjà ton enthousiasme croître.",
        "chaque nouveau niveau te rapproche davantage des étoiles.",
        "ton feu intérieur grandit, et avec lui, l’émerveillement de Lady Flamme.",
        "tu nourris les flammes de notre aventure, merci d’être là !",
        "ta persévérance éclaire notre chemin vers l’infini.",
        "ta route est lumineuse, continue à gravir ces niveaux avec passion.",
        "tu montes, tu t’élèves, tu brilles : que c’est beau de te voir évoluer !",
        "voici une nouvelle étape atteinte avec grâce et style !",
        "tes efforts dessinent peu à peu ta légende dans les cieux.",
        "un palier supplémentaire à ta quête : profite du paysage !",
        "ta progression est une danse élégante qui enchante notre aventure.",
        "tu viens d'ajouter un chapitre fascinant à ton histoire.",
        "ta volonté est admirable : continue à gravir les échelons célestes.",
        "tu es désormais plus haut, plus fort, plus rayonnant·e.",
        "avec chaque niveau, c’est tout notre univers qui gagne en beauté.",
        "ce nouveau palier est une promesse d’encore plus belles découvertes.",
        "tu montes brillamment en altitude, et Lady Flamme sourit fièrement à tes côtés.",
    ]


class EconomyConfig:
    """Définit les objets disponibles à l'achat dans la boutique du bot."""

    ITEMS: dict[str, dict[str, object]] = {
        "paypal": {
            "name": "Action Meta",
            "price": 59997,
            "description": "Vous recevrez 5 € sur PayPal. (Usage unique)",
        },
        "xp_bonus": {
            "name": "Puce GPU",
            "price": 1440,
            "description": "Supprime la limite d'XP pendant 1 h. Cumulable ×5.",
        },
        "xp_block": {
            "name": "Malware",
            "price": 348,
            "description": "Bloque la prise d'XP du prochain minuit au suivant. (Non cumulable)",
        },
        "spy": {
            "name": "Lunettes Meta",
            "price": 20,
            "description": "Permet de voir le sac (objets + argent) d'un autre utilisateur.",
        },
        "timemute": {
            "name": "Attaque DDOS",
            "price": 999,
            "description": "Mute un utilisateur ≥ lvl 10 pendant 10 min. Usage limité à 1/jour par cible.",
        },
    }


class VisualConfig:
    """Codes couleur et émojis pour les embeds & logs."""

    COLORS: dict[str, int] = {
        "error": 0xE74C3C,
        "warning": 0xF1C40F,
        "success": 0x2ECC71,
        "info": 0x3498DB,
    }
    EMOJIS: dict[str, str] = {
        "error": "❌",
        "warning": "⚠️",
        "reload": "♻️",
        "closed": "🔒",
        "web": "🌐",
        "trophy": "🏆",
    }
