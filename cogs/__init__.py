# cogs/__init__.py

import discord
from discord.ext import commands as _cmds

# Sauvegarde la vraie classe
_OriginalBot = _cmds.Bot


def Bot(*args, **kwargs):
    # Si aucun intents n'est passé, on injecte le default()
    if "intents" not in kwargs:
        kwargs["intents"] = discord.Intents.default()
    return _OriginalBot(*args, **kwargs)


# On écrase la référence dans le module commands
_cmds.Bot = Bot
