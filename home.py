import streamlit as st
from utils import init_db

st.set_page_config(page_title="Budget Manager", layout="wide")
init_db()

st.image("assets/logo.png", width=120)

with st.sidebar:
    st.image("assets/logo.png", width=120)


st.title("💰 Budget Manager")

st.write("Bienvenue dans ton gestionnaire de budget.")

if "user_id" in st.session_state:
    st.success(f"Connecté en tant que {st.session_state.username}")
    st.page_link("pages/4_Dashboard.py", label="📊 Aller au dashboard")
else:
    st.warning("Tu n'es pas connecté.")
    st.page_link("pages/0_Login.py", label="🔐 Se connecter")
    st.page_link("pages/1_Signup.py", label="🆕 Créer un compte")

if "user_id" in st.session_state:
    st.success(f"Connecté en tant que {st.session_state.username}")
    st.page_link("pages/4_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_Dépenses_fixes.py", label="🏠 Dépenses fixes")
    st.page_link("pages/3_Dépenses_journalières.py", label="🛒 Dépenses journalières")
    st.page_link("pages/6_Revenus.py", label="💵 Revenus")
    st.page_link("pages/5_Import_Export.py", label="📂 Import / Export")
    st.page_link("pages/7_Objectifs.py", label="🎯 Objectifs")
