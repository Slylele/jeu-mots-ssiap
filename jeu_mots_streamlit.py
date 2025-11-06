import streamlit as st
import pandas as pd
#import random
import os

# Chargement du fichier CSV
csv_path = os.path.join(os.path.dirname(__file__), "mots_definitions.csv")

try:
    df = pd.read_csv(csv_path)
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

# Initialisation de l'état
if "mot_courant" not in st.session_state:
    st.session_state.mot_courant = None
    st.session_state.definition_visible = False

# Bouton pour afficher un mot aléatoire
if st.button("🎲 Nouveau mot"):
    ligne = df.sample().iloc[0]
    st.session_state.mot_courant = {"mot": ligne["mot"], "definition": ligne["definition"]}
    st.session_state.definition_visible = False

# Affichage du mot
if st.session_state.mot_courant:
    st.subheader(st.session_state.mot_courant["mot"])
    if st.button("📖 Voir la définition"):
        st.session_state.definition_visible = True
    if st.session_state.definition_visible:
        st.write(st.session_state.mot_courant["definition"])