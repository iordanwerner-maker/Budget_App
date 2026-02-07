import streamlit as st
from utils import init_db

st.title("🎯 Objectifs financiers")
init_db()

if "user_id" not in st.session_state:
    st.error("Tu dois être connecté pour accéder à cette page.")
    st.stop()

with st.sidebar:
    st.write(f"👤 {st.session_state.username}")
    if st.button("🔓 Se déconnecter"):
        st.session_state.clear()
        st.success("Déconnexion réussie.")
        st.switch_page("home.py")

st.subheader("Définir un objectif d’épargne mensuelle")

objectif = st.number_input("Objectif d’épargne mensuelle (€)", min_value=0.0, step=50.0)

if "objectif_epargne" not in st.session_state:
    st.session_state.objectif_epargne = 0.0

if st.button("Enregistrer l’objectif"):
    st.session_state.objectif_epargne = objectif
    st.success("Objectif enregistré.")

if st.session_state.objectif_epargne > 0:
    st.info(f"🎯 Objectif actuel : {st.session_state.objectif_epargne:.2f} € / mois")
else:
    st.info("Aucun objectif défini pour l’instant.")

