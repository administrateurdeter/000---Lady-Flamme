"""
Script de lancement du bot Discord en tant que sous-processus,
avec relance automatique en cas de crash.
"""

import subprocess
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from subprocess import Popen


def setup_logging() -> None:
    """Configure le logging pour le lanceur lui-même."""
    file_handler: RotatingFileHandler = RotatingFileHandler(
        filename="launcher.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    stream_handler: logging.StreamHandler = logging.StreamHandler()
    fmt: str = "%(asctime)s – %(levelname)s – %(name)s – %(message)s"
    logging.basicConfig(
        level=logging.INFO, handlers=[file_handler, stream_handler], format=fmt
    )


def main_launcher() -> None:
    """
    Boucle principale qui lance main.py dans un processus séparé
    et le redémarre en cas de crash.
    """
    setup_logging()
    logger: logging.Logger = logging.getLogger("launcher")
    python_executable: str = sys.executable

    while True:
        try:
            logger.info("Lancement du processus du bot (main.py)...")
            process: "Popen" = subprocess.Popen([python_executable, "main.py"])
            return_code: int = process.wait()
            logger.info(
                f"Le processus du bot s'est arrêté. Code de sortie: {return_code}. Arrêt du launcher."
            )
            break

        except KeyboardInterrupt:
            logger.info("Arrêt manuel du launcher détecté. Fermeture du bot…")
            if "process" in locals() and process.poll() is None:
                process.terminate()
            logger.info("Au revoir !")
            break

        except Exception as e:
            logger.error("Erreur fatale dans le launcher.", exc_info=e)
            break


if __name__ == "__main__":
    main_launcher()
