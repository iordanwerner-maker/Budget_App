import streamlit as st
from utils import add_depense, load_data, delete_depense, init_db

st.title("💵 Revenus")
init_db()

if "user_id" not in st.session_state:
    st.error("Tu dois être connecté pour accéder à cette page.")
    st.stop()

user_id = st.session_state.user_id

with st.sidebar:
    st.write(f"👤 {st.session_state.username}")
    if st.button("🔓 Se déconnecter"):
        st.session_state.clear()
        st.success("Déconnexion réussie.")
        st.switch_page("home.py")

st.subheader("Ajouter un revenu")

date = st.date_input("Date")
mois = date.strftime("%Y-%m")
categorie = st.text_input("Source du revenu")
montant = st.number_input("Montant (€)", min_value=0.0, step=0.1)
description = st.text_area("Description")
type_depense = "revenu"

if st.button("Ajouter le revenu"):
    if categorie == "" or montant == 0:
        st.error("Merci de remplir les champs obligatoires.")
    else:
        add_depense(str(date), mois, categorie, montant, description, type_depense, user_id)
        st.success("Revenu ajouté.")

st.subheader("📋 Historique des revenus")
df = load_data(user_id)
df = df[df["type"] == "revenu"] if not df.empty else df

if df.empty:
    st.info("Aucun revenu enregistré.")
else:
    for index, row in df.iterrows():
        col1, col2 = st.columns([5, 1])

        with col1:
            st.write(f"📅 {row['date']} — **{row['categorie']}** : {row['montant']} €")
            if row["description"]:
                st.caption(row["description"])

        with col2:
            if st.button("🗑️", key=f"del_rev_{row['id']}"):
                delete_depense(row["id"])
                st.success("Revenu supprimé.")
                st.rerun()
