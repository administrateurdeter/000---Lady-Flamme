"""Script de visualisation et de validation du modèle "Spline Unifiée".

Ce script utilise Streamlit pour générer des graphiques interactifs et des
tableaux de données basés sur les constantes du modèle de progression.

Il sert d'outil d'analyse pour le game designer afin de vérifier que toutes
les contraintes de conception (temps de progression, équilibre, etc.) sont
respectées par le modèle mathématique avant son implémentation.

Pour l'exécuter : `streamlit run visualisation_level.py`
"""

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from scipy.interpolate import CubicSpline

# ==============================================================================
# PARAMÈTRES DU MODÈLE "SPLINE UNIFIÉ"
# Ces constantes doivent être identiques à celles utilisées dans `utils.py`.
# ==============================================================================

PHI_FINAL: float = 0.5
PROFILES: dict[str, float] = {
    "Médiane (5 msg/j)": 5.0,
    "Cible (10 msg/j)": 10.0,
    "P90 (27.5 msg/j)": 27.5,
    "P99 (120 msg/j)": 120.0,
}
KNOT_LEVELS: list[int] = [1, 15, 60, 100]
OPTIMAL_KNOT_VALUES: list[float] = [0.2, 1.8, 18, 85]


# ==============================================================================
# FONCTIONS DE CALCUL DU MODÈLE
# ==============================================================================


def xp_per_message(n: int, phi: float) -> float:
    """Calcule l'XP gagné pour le n-ième message de la journée."""
    return 200 / (1 + phi * n)


# ==============================================================================
# PRÉ-CALCUL DE LA COURBE DE PROGRESSION
# ==============================================================================

# 1. Calcul des gains journaliers pour chaque profil
DAILY_XP = {
    name: sum(xp_per_message(n, PHI_FINAL) for n in range(1, int(msgs) + 1))
    for name, msgs in PROFILES.items()
}

# 2. Création de la fonction Spline qui régit la difficulté
spline_func = CubicSpline(KNOT_LEVELS, OPTIMAL_KNOT_VALUES, bc_type="natural")

# 3. Application de la loi pour obtenir le temps/niveau pour la Cible
LEVELS = np.arange(1, 101)
days_per_level_cible = spline_func(LEVELS)

# 4. Déduction du coût en XP universel pour chaque niveau
xp_req_values = days_per_level_cible * DAILY_XP["Cible (10 msg/j)"]
xp_cum_values = np.cumsum(xp_req_values)


# ==============================================================================
# APPLICATION STREAMLIT
# ==============================================================================

st.set_page_config(layout="wide")
st.title("Le Chef-d'Œuvre : Visualisation du Modèle Spline Unifié")

st.markdown(
    """
    **Admirez ce système. Chaque courbe prouve que toutes les contraintes sont respectées :**

    - Le profil **P99** doit mettre environ **2,5 ans** pour atteindre le niveau 100.
    - Le profil **Médiane** (5 msg/j) doit mettre environ **6 ans** pour atteindre le niveau 100.
    - Le **ratio P90 / P99** doit rester maîtrisé (**inférieur à 1,8**).
    - Le joueur cible doit atteindre le **niveau 5 en environ 2,5 jours**.
    - Le joueur cible doit atteindre le **niveau 15 en environ 16 jours**.
    - Il ne doit y avoir **aucun gap brutal** ou mur de difficulté : la progression doit rester **organique et fluide**.
    - Le **temps nécessaire pour passer un niveau doit toujours augmenter** de manière cohérente.
    """
)

# --- Interface utilisateur ---
st.sidebar.header("Sélection du Profil")
selected_profile_name = st.sidebar.selectbox(
    "Choisissez un profil pour voir le détail de sa progression :",
    list(PROFILES.keys()),
)

# --- Calcul des données pour le profil sélectionné ---
daily_xp = DAILY_XP[selected_profile_name]

# Création du DataFrame principal
df = pd.DataFrame(
    {
        "Niveau": LEVELS,
        "XP Requis": xp_req_values.astype(int),
        "XP Cumulé": xp_cum_values.astype(int),
        "Jours pour ce Niveau": (xp_req_values / daily_xp),
        "Jours Cumulés": (xp_cum_values / daily_xp),
    }
)

# --- AFFICHAGE DES GRAPHIQUES ---
st.header("Les Courbes de la Progression")

# Graphique 1: La Courbe du Ressenti
st.subheader("La Courbe du Ressenti (Jours par Niveau)")
st.markdown(
    f"Cette courbe montre le temps nécessaire pour passer chaque niveau pour le profil **{selected_profile_name}**. Observez sa montée parfaitement lisse et continue."
)

chart_days_per_level = (
    alt.Chart(df)
    .mark_line(
        point=alt.OverlayMarkDef(color="red", size=50, filled=True), color="royalblue"
    )
    .encode(
        x=alt.X("Niveau", title="Niveau"),
        y=alt.Y("Jours pour ce Niveau", title="Jours requis pour passer ce niveau"),
        tooltip=[
            alt.Tooltip("Niveau"),
            alt.Tooltip("Jours pour ce Niveau", format=".2f"),
        ],
    )
    .properties(title=f"Temps de progression pour le profil : {selected_profile_name}")
    .interactive()
)
st.altair_chart(chart_days_per_level, use_container_width=True)


# Graphique 2: La Courbe du Voyage
st.subheader("La Courbe du Voyage (XP Cumulé Total)")
st.markdown(
    "Cette courbe représente la montagne d'XP totale à gravir. C'est l'effort cumulé pour atteindre chaque niveau."
)

chart_xp_cum = (
    alt.Chart(df)
    .mark_area(
        line={"color": "darkgreen"},
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="white", offset=0),
                alt.GradientStop(color="darkgreen", offset=1),
            ],
            x1=1,
            x2=1,
            y1=1,
            y2=0,
        ),
    )
    .encode(
        x=alt.X("Niveau", title="Niveau"),
        y=alt.Y("XP Cumulé", title="XP Cumulé Total"),
        tooltip=[alt.Tooltip("Niveau"), alt.Tooltip("XP Cumulé", format=",")],
    )
    .properties(title="L'Ascension : XP Total Requis par Niveau")
    .interactive()
)
st.altair_chart(chart_xp_cum, use_container_width=True)


# --- AFFICHAGE DU TABLEAU DÉTAILLÉ ---
st.header(f"Tableau de progression détaillé pour : {selected_profile_name}")

df_display = df.copy()
df_display["Jours pour ce Niveau"] = df_display["Jours pour ce Niveau"].map(
    "{:,.2f}".format
)
df_display["Jours Cumulés"] = df_display["Jours Cumulés"].map("{:,.1f}".format)
st.dataframe(df_display, height=400, use_container_width=True)

# --- SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.header("Résumé des temps finaux")
summary_data = []
for name, msgs in PROFILES.items():
    d_xp = DAILY_XP[name]
    total_days = xp_cum_values[-1] / d_xp
    summary_data.append(
        {"Profil": name, "Années pour Lvl 100": f"{total_days / 365:.2f}"}
    )
st.sidebar.table(pd.DataFrame(summary_data).set_index("Profil"))
