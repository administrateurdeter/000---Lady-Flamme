"""Script de lancement du bot Discord en tant que sous-processus.

Ce lanceur assure une meilleure gestion du cycle de vie du bot,
notamment en permettant une relance automatique en cas de crash.
"""

import logging
import subprocess
import sys
from logging.handlers import RotatingFileHandler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from subprocess import Popen


def setup_logging() -> None:
    """Configure le logging pour le lanceur lui-même."""
    file_handler = RotatingFileHandler(
        filename="launcher.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    stream_handler = logging.StreamHandler()
    fmt = "%(asctime)s – %(levelname)s – %(name)s – %(message)s"
    logging.basicConfig(
        level=logging.INFO, handlers=[file_handler, stream_handler], format=fmt
    )


def main_launcher() -> None:
    """Boucle principale qui lance main.py et le surveille.

    Ce processus parent est responsable de démarrer le processus enfant (le bot)
    et de le redémarrer s'il se termine de manière inattendue.
    """
    setup_logging()
    logger = logging.getLogger("launcher")
    python_executable = sys.executable
    process: "Popen"

    while True:
        try:
            logger.info(
                f"Lancement du processus du bot (main.py) avec {python_executable}..."
            )
            process = subprocess.Popen([python_executable, "main.py"])
            return_code = process.wait()

            # Si le processus se termine, on logue le code de sortie.
            # Une sortie normale ne déclenchera pas de redémarrage.
            logger.warning(
                f"Le processus du bot s'est arrêté avec le code de sortie: {return_code}."
            )
            break  # Sort de la boucle while pour arrêter le launcher.

        except KeyboardInterrupt:
            logger.info("Arrêt manuel du launcher détecté. Fermeture du bot…")
            if "process" in locals() and process.poll() is None:
                process.terminate()
            logger.info("Launcher arrêté proprement. Au revoir !")
            break

        except Exception as e:
            logger.critical("Erreur fatale et non gérée dans le launcher.", exc_info=e)
            break


if __name__ == "__main__":
    main_launcher()
