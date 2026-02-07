import streamlit as st
from utils import get_conn, verify_password, init_db

st.title("🔐 Connexion")

init_db()

username = st.text_input("Nom d'utilisateur")
password = st.text_input("Mot de passe", type="password")

if st.button("Se connecter"):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and verify_password(password, user[1]):
        st.session_state.user_id = user[0]
        st.session_state.username = username
        st.success("Connexion réussie.")
        st.switch_page("home.py")
    else:
        st.error("Identifiants incorrects")
