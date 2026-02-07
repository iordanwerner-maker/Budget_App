import streamlit as st
import plotly.express as px
from utils import load_data, init_db

st.title("📊 Dashboard général")
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

data = load_data(user_id)

# Sélecteur de mois
mois_disponibles = sorted(data["mois"].unique())

mois_selectionne = st.selectbox("📆 Choisir un mois", ["Tous"] + mois_disponibles)

if mois_selectionne != "Tous":
    data = data[data["mois"] == mois_selectionne]


# Calcul revenu total
revenus = data[data["type"] == "revenu"]["montant"].sum()

# Calcul dépenses totales
depenses = data[data["type"] != "revenu"]["montant"].sum()

# Reste
reste = revenus - depenses

st.metric("💶 Revenu total", f"{revenus:.2f} €")
st.metric("💸 Dépenses totales", f"{depenses:.2f} €")
st.metric("🟢 Reste du mois", f"{reste:.2f} €")


if data.empty:
    st.info("Aucune donnée enregistrée pour le moment.")
else:
    # Séparation revenus / dépenses
    revenus_df = data[data["type"] == "revenu"]
    depenses_df = data[data["type"] != "revenu"]

    total_revenus = revenus_df["montant"].sum()
    total_depenses = depenses_df["montant"].sum()
    reste = total_revenus - total_depenses
    taux_epargne = (reste / total_revenus * 100) if total_revenus > 0 else 0



    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💶 Revenus totaux", f"{total_revenus:.2f} €")
    col2.metric("💸 Dépenses totales", f"{total_depenses:.2f} €")
    col3.metric("🟢 Reste", f"{reste:.2f} €")
    col4.metric("📈 Taux d’épargne", f"{taux_epargne:.1f} %")
    
    # Totaux par type
    total_fixes = data[data["type"] == "fixe"]["montant"].sum()
    total_journalieres = data[data["type"] == "journalière"]["montant"].sum()

    colA, colB = st.columns(2)
    colA.metric("🏠 Dépenses fixes", f"{total_fixes:.2f} €")
    colB.metric("🛒 Dépenses journalières", f"{total_journalieres:.2f} €")
    
    # Cheltuieli fixe
    
    st.markdown("## 🏠 Dépenses fixes par catégorie")

    df_fixe = data[data["type"] == "fixe"]

    if df_fixe.empty:
        st.info("Aucune dépense fixe.")
    else:
        df_cat_fixe = df_fixe.groupby("categorie")["montant"].sum().reset_index()
        colF1, colF2 = st.columns(2)

        for index, row in df_cat_fixe.iterrows():
            with colF1 if index % 2 == 0 else colF2:
                st.metric(f"{row['categorie']}", f"{row['montant']:.2f} €")

    # Cheltuieli zilnice

    st.markdown("## 🛒 Dépenses journalières par catégorie")

    df_jour = data[data["type"] == "journalière"]

    if df_jour.empty:
        st.info("Aucune dépense journalière.")
    else:
        df_cat = df_jour.groupby("categorie")["montant"].sum().reset_index()
        colA, colB = st.columns(2)

        for index, row in df_cat.iterrows():
            with colA if index % 2 == 0 else colB:
                st.metric(f"{row['categorie']}", f"{row['montant']:.2f} €")


    # Évolution des dépenses mensuelles
    if not depenses_df.empty:
        df_dep_mois = depenses_df.groupby("mois")["montant"].sum().reset_index()
        fig_dep = px.line(df_dep_mois, x="mois", y="montant", markers=True,
                          title="Évolution des dépenses mensuelles")
        st.plotly_chart(fig_dep, use_container_width=True)

    # Revenus vs dépenses par mois
    if not data.empty:
        df_mois_type = data.groupby(["mois", "type"])["montant"].sum().reset_index()
        fig_comp = px.bar(df_mois_type, x="mois", y="montant", color="type",
                          barmode="group",
                          title="Revenus vs Dépenses par mois")
        st.plotly_chart(fig_comp, use_container_width=True)

    # Répartition par type (fixes / journalières / revenus)
    df_type = data.groupby("type")["montant"].sum().reset_index()
    fig_type = px.pie(df_type, names="type", values="montant",
                      title="Répartition par type")
    st.plotly_chart(fig_type, use_container_width=True)

    st.markdown("### 📆 Reste par mois")

    # Revenus et dépenses par mois
    rev_mois = revenus_df.groupby("mois")["montant"].sum().reset_index(name="revenus")
    dep_mois = depenses_df.groupby("mois")["montant"].sum().reset_index(name="depenses")

    df_reste = rev_mois.merge(dep_mois, on="mois", how="outer").fillna(0)
    df_reste["reste"] = df_reste["revenus"] - df_reste["depenses"]
    df_reste = df_reste.sort_values("mois")

    st.dataframe(df_reste)
