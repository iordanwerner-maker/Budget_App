import streamlit as st
from utils import get_conn, hash_password, init_db

st.title("🆕 Créer un compte")

init_db()

username = st.text_input("Nom d'utilisateur")
password = st.text_input("Mot de passe", type="password")

if st.button("Créer le compte"):
    if username == "" or password == "":
        st.error("Merci de remplir tous les champs.")
    else:
        conn = get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hash_password(password))
            )
            conn.commit()
            st.success("Compte créé ! Tu peux maintenant te connecter.")
        except Exception:
            st.error("Ce nom d'utilisateur existe déjà.")
        conn.close()

