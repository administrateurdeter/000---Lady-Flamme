"""
Script de maintenance pour restaurer l'XP des utilisateurs après une
réinitialisation de la base de données de développement.
"""
import os
import sys
import logging

# --- Configuration du chemin pour importer les modules du projet ---
# Cette astuce permet au script de trouver les modules 'db' et 'utils'
# qui sont dans le dossier parent.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from db import fetch_user, save_user
from utils import total_xp_to_level

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==============================================================================
# ▼▼▼ MODIFIEZ CETTE LISTE AVEC VOS DONNÉES ▼▼▼
# ==============================================================================
# Remplacez les ID et XP par ceux de vos utilisateurs.
# J'ai pré-rempli avec les données de votre image.
USER_DATA = [
    {'id': 746363602172379156, 'xp': 752, 'name': 'Jack'},
    {'id': 1051572942766612542, 'xp': 640, 'name': 'BlackMamba'},
    {'id': 639884625908465674, 'xp': 607, 'name': 'Reptilien'},
    {'id': 395012813078396928, 'xp': 487, 'name': 'Lowen'},
    {'id': 476066925504626700, 'xp': 487, 'name': 'Sombre Déchet'},
    {'id': 1344320348912357448, 'xp': 233, 'name': 'Plok'},
    {'id': 605451770868662274, 'xp': 133, 'name': 'Bellatrix'},
    {'id': 1240299425038073931, 'xp': 133, 'name': 'Loona'},
    {'id': 1392729630557081713, 'xp': 133, 'name': 'Ganbaro'},
    # Ajoutez d'autres utilisateurs si nécessaire...
    # {'id': AUTRE_ID, 'xp': AUTRE_XP, 'name': 'AUTRE_NOM'},
]
# ==============================================================================

def main():
    """Fonction principale du script de restauration."""
    logging.info(f"Début de la restauration pour {len(USER_DATA)} utilisateurs.")

    for user_info in USER_DATA:
        user_id = user_info['id']
        target_xp = user_info['xp']
        user_name = user_info.get('name', 'N/A')

        try:
            # 1. Récupère l'utilisateur (le crée s'il n'existe pas)
            user_data = fetch_user(user_id)

            # 2. Met à jour son XP et son niveau
            user_data['xp'] = target_xp
            user_data['level'] = total_xp_to_level(target_xp) # Recalcule le niveau !
            user_data['nick'] = user_name # Met à jour le pseudo

            # 3. Sauvegarde les changements
            save_user(user_data)

            logging.info(f"✅ Succès pour {user_name} (ID: {user_id}): XP mis à {target_xp}, Niveau mis à {user_data['level']}.")

        except Exception as e:
            logging.error(f"❌ Échec pour {user_name} (ID: {user_id}): {e}")

    logging.info("Restauration terminée !")

if __name__ == "__main__":
    main()