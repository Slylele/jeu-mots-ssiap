import streamlit as st
import pandas as pd
import random
import os

# =============================
# Chargement du fichier CSV
# =============================
csv_path = os.path.join(os.path.dirname(__file__), "mots_definitions.csv")

try:
    df = pd.read_csv(csv_path, delimiter=";")
except FileNotFoundError:
    st.error("Le fichier 'mots_definitions.csv' est introuvable.")
    st.stop()
except Exception as e:
    st.error(f"Erreur lors du chargement du fichier CSV : {e}")
    st.stop()

# Vérification des colonnes
if "mot" not in df.columns or "definition" not in df.columns:
    st.error("Le fichier CSV doit contenir les colonnes 'mot' et 'definition'.")
    st.stop()

# =============================
# Initialisation des états
# =============================
if "mot_courant" not in st.session_state:
    ligne = df.sample().iloc[0]
    st.session_state.mot_courant = {"mot": ligne["mot"], "definition": ligne["definition"]}
    st.session_state.definition_visible = False

# =============================
# Gestion des deux états
# =============================
col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    st.subheader(st.session_state.mot_courant["mot"])

with col2:
    if st.session_state.definition_visible:
        # État 2 : bouton = Nouveau mot
        if st.button("Nouveau mot"):
            ligne = df.sample().iloc[0]
            st.session_state.mot_courant = {"mot": ligne["mot"], "definition": ligne["definition"]}
            st.session_state.definition_visible = False
            st.rerun()  # Recharge immédiatement
    else:
        # État 1 : bouton = Afficher la définition
        if st.button("Afficher la définition"):
            st.session_state.definition_visible = True
            st.rerun()  # Recharge immédiatement

# =============================
# Ligne 2 : affichage conditionnel de la définition
# =============================
if st.session_state.definition_visible:
    st.write(st.session_state.mot_courant["definition"])