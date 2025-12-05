import streamlit as st
import os, runpy

st.set_page_config(page_title="Revisions SSIAP 2025", layout="wide")

# State
if 'current_app' not in st.session_state:
    st.session_state.current_app = None

# Header
st.title("Révisions SSIAP")

# Home view
if st.session_state.current_app is None:
    st.markdown("Choisissez une application à lancer :")
    col1, col2 = st.columns([1, 4]) #st.columns(2)
    with col1:
        if st.button("📘 QCM SSIAP"):
            st.session_state.current_app = 'qcm'
            st.rerun()
    with col2:
        if st.button("🔤 Définitions"):
            st.session_state.current_app = 'mots'
            st.rerun()
else:
    # Back button
    if st.button("⬅️ Retour à l'accueil"):
        st.session_state.current_app = None
        st.rerun()

    # Resolve script path in same directory
    base_dir = os.path.dirname(__file__)
    if st.session_state.current_app == 'qcm':
        script_path = os.path.join(base_dir, 'qcm_ssiap_app.py')
        # Execute the app script in the same Streamlit run
        runpy.run_path(script_path, run_name='__main__')
    elif st.session_state.current_app == 'mots':
        script_path = os.path.join(base_dir, 'jeu_mots_streamlit.py')
        runpy.run_path(script_path, run_name='__main__')
