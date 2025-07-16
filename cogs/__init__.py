"""Initialisation du package 'cogs'.

Ce module contient une technique de monkey-patching pour simplifier
l'initialisation du bot dans les tests ou les scripts simples.

En important ce module, la classe `discord.ext.commands.Bot` est modifiée
pour utiliser `discord.Intents.default()` automatiquement si aucun
intent n'est spécifié lors de son instanciation.

Cela évite d'avoir à répéter la configuration des intents dans chaque
fichier de test.
"""

import discord
from discord.ext import commands as _cmds

# --- Monkey-Patching de discord.ext.commands.Bot ---

# 1. Sauvegarde de la classe originale pour pouvoir l'appeler.
_OriginalBot = _cmds.Bot


def Bot(*args, **kwargs):
    """Wrapper personnalisé pour la classe `commands.Bot`.

    Cette fonction intercepte l'instanciation de `commands.Bot`. Si le
    paramètre `intents` n'est pas fourni, elle injecte les intents par
    défaut avant de créer l'objet Bot original.

    Args:
        *args: Arguments positionnels passés à `commands.Bot`.
        **kwargs: Arguments nommés passés à `commands.Bot`.

    Returns:
        Une instance de la classe `commands.Bot` originale.
    """
    if "intents" not in kwargs:
        kwargs["intents"] = discord.Intents.default()
    return _OriginalBot(*args, **kwargs)


# 2. Remplacement de la référence dans le module `commands`.
# Désormais, toute instanciation de `commands.Bot` dans le projet
# passera par notre wrapper personnalisé.
_cmds.Bot = Bot
