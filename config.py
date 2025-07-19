"""Fichier de configuration centralisé.

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
    """Constantes liées au gain d'expérience et d'or."""

    MIN_LEN: int = 5  # Longueur minimale d'un message pour être éligible à l'XP.
    COOLDOWN: int = (
        60  # Cooldown de 60 secondes entre deux messages rapportant de l'XP.
    )

    # --- Constantes du modèle "Spline Unifiée" ---
    MAX_LEVEL: int = 100
    PHI: float = 0.5
    CIBLE_MESSAGES_PER_DAY: int = 10
    KNOT_LEVELS: list[int] = [1, 15, 60, 100]
    OPTIMAL_KNOT_VALUES: list[float] = [0.2, 1.8, 18, 85]

    # Constantes pour le gain d'or par message ("salaire" quotidien)
    MONEY_PER_MESSAGE_AMOUNT: int = 5
    MONEY_PER_MESSAGE_LIMIT: int = 5


class StyleConfig:
    """Constantes liées aux messages, rôles et emojis."""

    EMOJI_LEVEL_UP: str = "🎉"

    LEVEL_UP_MESSAGES: list[str] = [
        "te voilà plus flamboyant·e que jamais, " "l’aventure ne fait que commencer !",
        "la chaleur de ta détermination illumine désormais un nouveau niveau.",
        "ta légende s’écrit doucement dans les nuages. Continuons à monter !",
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
        "tu montes brillamment en altitude, et Lady Flamme sourit à tes côtés.",
    ]


class EconomyConfig:
    """Définit les objets disponibles à l'achat dans la boutique du bot."""

    ITEMS: dict[str, dict[str, object]] = {
        "temp_nick_self": {
            "name": "Changement de Pseudo (Personnel, 2h)",
            "price": 50,
            "description": "Changez votre propre pseudo sur le serveur pour 2 heures.",
        },
        "temp_nick_other": {
            "name": "Changement de Pseudo (Ciblé, 2h)",
            "price": 200,
            "description": "Changez le pseudo d'un autre membre pour 2 heures.",
        },
        "temp_color_self": {
            "name": "Couleur de Pseudo (24h)",
            "price": 150,
            "description": (
                "Obtenez une couleur de pseudo personnalisée pendant 24 heures."
            ),
        },
        "perm_nick": {
            "name": "Permission: Changer son Pseudo (Permanent)",
            "price": 5000,
            "description": "Achetez le droit de changer votre pseudo à volonté.",
        },
        "perm_emoji": {
            "name": "Permission: Emojis Externes (Permanent)",
            "price": 7500,
            "description": "Achetez le droit d'utiliser des emojis externes.",
        },
        "perm_sticker": {
            "name": "Permission: Autocollants Externes (Permanent)",
            "price": 7500,
            "description": "Achetez le droit d'utiliser des autocollants externes.",
        },
    }


class VisualConfig:
    """Codes couleur et émojis pour les embeds & logs."""

    THEME_COLOR: int = 0xFE6A33
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


class SecurityConfig:
    """Configuration liée à la sécurité et à la modération des pseudos."""

    FORBIDDEN_NICKNAME_WORDS_RAW: tuple[str, ...] = (
        "attarde",
        "attardee",
        "attardes",
        "bamboula",
        "bicot",
        "bougnoule",
        "broute gazon",
        "broute_gazon",
        "broute-gazon",
        "broutegazon",
        "chinetoque",
        "crouille",
        "debile mental",
        "debile_mental",
        "debile-mental",
        "debilemental",
        "dep",
        "dp",
        "encule",
        "enculee",
        "encules",
        "face de citron",
        "face_de_citron",
        "face-de-citron",
        "facedecitron",
        "feuj",
        "fiotte",
        "gay",
        "gays",
        "goudou",
        "gouine",
        "grosse gouine",
        "grosse_gouine",
        "grosse-gouine",
        "grossegouine",
        "macaque",
        "mongolien",
        "negre",
        "negree",
        "negres",
        "negro",
        "negroide",
        "niakoue",
        "noiraud",
        "payday",
        "pd",
        "pds",
        "pedale",
        "pure souche",
        "pure_souche",
        "pure-souche",
        "puresouche",
        "pute",
        "race inferieure",
        "race pure",
        "race superieure",
        "race_inferieure",
        "race_pure",
        "race_superieure",
        "race-inferieure",
        "race-pure",
        "race-superieure",
        "raceinferieure",
        "racepure",
        "racesuperieure",
        "sale arabe",
        "sale blanc",
        "sale chretien",
        "sale juif",
        "sale musulman",
        "sale noir",
        "sale pede",
        "sale_arabe",
        "sale_blanc",
        "sale_chretien",
        "sale_juif",
        "sale_musulman",
        "sale_noir",
        "sale_pede",
        "sale-arabe",
        "sale-blanc",
        "sale-chretien",
        "sale-juif",
        "sale-musulman",
        "sale-noir",
        "sale-pede",
        "salearabe",
        "saleblanc",
        "salechretien",
        "salejuif",
        "salemusulman",
        "salenoir",
        "salepede",
        "salope",
        "sous homme",
        "sous race",
        "sous_homme",
        "sous_race",
        "sous-homme",
        "sous-race",
        "soushomme",
        "sousrace",
        "tantouse",
        "tapette",
        "tarlouze",
        "trainee",
        "transpd",
        "trisomique mental",
        "trisomique_mental",
        "trisomique-mental",
        "trisomiquemental",
        "youpin",
        "youpine",
    )
