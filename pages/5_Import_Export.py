import streamlit as st
import pandas as pd
from utils import get_conn, export_depenses_to_excel, init_db
from utils import export_multi_feuilles
from utils import export_par_mois


st.title("📂 Import / Export")
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

# ---------------------------------------------------------
# EXPORT
# ---------------------------------------------------------

st.subheader("📘 Export multi-feuilles (Excel)")

if st.button("Exporter en Excel (multi-feuilles)"):
    ok = export_multi_feuilles(user_id, "export_budget.xlsx")
    if ok:
        st.success("Export multi-feuilles réalisé : 'export_budget.xlsx'")
        with open("export_budget.xlsx", "rb") as f:
            st.download_button("Télécharger le fichier", f, file_name="export_budget.xlsx")
    else:
        st.info("Aucune donnée à exporter.")
        
st.subheader("📅 Export par mois (multi-feuilles)")

if st.button("Exporter par mois"):
    ok = export_par_mois(user_id, "export_par_mois.xlsx")
    if ok:
        st.success("Export mensuel réalisé : 'export_par_mois.xlsx'")
        with open("export_par_mois.xlsx", "rb") as f:
            st.download_button("Télécharger le fichier", f, file_name="export_par_mois.xlsx")
    else:
        st.info("Aucune donnée à exporter.")


# ---------------------------------------------------------
# IMPORT
# ---------------------------------------------------------

st.subheader("📥 Import depuis un fichier Excel")

uploaded = st.file_uploader("Choisir un fichier Excel", type=["xlsx"])

if uploaded is not None:
    try:
        df = pd.read_excel(uploaded)

        # Colonnes obligatoires
        colonnes_attendues = ["date", "mois", "categorie", "montant", "description", "type"]

        # Vérification
        colonnes_manquantes = [c for c in colonnes_attendues if c not in df.columns]
        if colonnes_manquantes:
            st.error(f"Colonnes manquantes dans le fichier : {', '.join(colonnes_manquantes)}")
            st.stop()

        # Ajout user_id si absent
        df["user_id"] = user_id

        # Nettoyage des données
        df["montant"] = pd.to_numeric(df["montant"], errors="coerce")
        df = df.dropna(subset=["montant"])

        # Import dans SQLite
        conn = get_conn()
        df.to_sql("depenses", conn, if_exists="append", index=False)
        conn.close()

        st.success("Données importées avec succès.")

    except Exception as e:
        st.error(f"Erreur lors de l'import : {e}")
