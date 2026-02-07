import sqlite3
import pandas as pd
import hashlib
import os

DB_PATH = "data/budget.db"

def get_conn():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS depenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            mois TEXT,
            categorie TEXT,
            montant REAL,
            description TEXT,
            type TEXT,
            user_id INTEGER
        )
    """)

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def add_depense(date, mois, categorie, montant, description, type_depense, user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO depenses (date, mois, categorie, montant, description, type, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (date, mois, categorie, montant, description, type_depense, user_id))
    conn.commit()
    conn.close()

def load_data(user_id=None):
    conn = get_conn()
    query = "SELECT * FROM depenses"
    if user_id is not None:
        query += f" WHERE user_id = {user_id}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def export_depenses_to_excel(user_id, path="export.xlsx"):
    df = load_data(user_id)
    if df.empty:
        return False
    df.to_excel(path, index=False)
    return True

def delete_depense(depense_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM depenses WHERE id = ?", (depense_id,))
    conn.commit()
    conn.close()

def export_multi_feuilles(user_id, path="export_budget.xlsx"):
    conn = get_conn()

    # Charger toutes les données de l'utilisateur
    df = pd.read_sql(f"SELECT * FROM depenses WHERE user_id = {user_id}", conn)
    conn.close()

    if df.empty:
        return False

    # Séparer les types
    df_fixe = df[df["type"] == "fixe"]
    df_jour = df[df["type"] == "journalière"]
    df_rev = df[df["type"] == "revenu"]

    # Résumé
    resume = pd.DataFrame({
        "Catégorie": ["Revenus", "Dépenses fixes", "Dépenses journalières", "Reste"],
        "Montant (€)": [
            df_rev["montant"].sum(),
            df_fixe["montant"].sum(),
            df_jour["montant"].sum(),
            df_rev["montant"].sum() - (df_fixe["montant"].sum() + df_jour["montant"].sum())
        ]
    })

    # Export multi-feuilles
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        resume.to_excel(writer, sheet_name="Résumé", index=False)
        df_fixe.to_excel(writer, sheet_name="Dépenses fixes", index=False)
        df_jour.to_excel(writer, sheet_name="Dépenses journalières", index=False)
        df_rev.to_excel(writer, sheet_name="Revenus", index=False)

    return True

def export_par_mois(user_id, path="export_par_mois.xlsx"):
    conn = get_conn()
    df = pd.read_sql(f"SELECT * FROM depenses WHERE user_id = {user_id}", conn)
    conn.close()

    if df.empty:
        return False

    # Liste des mois disponibles
    mois_list = sorted(df["mois"].unique())

    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:

        for mois in mois_list:
            df_mois = df[df["mois"] == mois]

            # Séparer fixes / journalières
            df_fixe = df_mois[df_mois["type"] == "fixe"]
            df_jour = df_mois[df_mois["type"] == "journalière"]

            # Construire une feuille propre
            feuille = pd.DataFrame()

            # Ajouter les dépenses fixes
            if not df_fixe.empty:
                feuille = pd.concat([
                    feuille,
                    pd.DataFrame({"Section": ["Dépenses fixes"]}),
                    df_fixe,
                    pd.DataFrame({"Section": ["Total fixes"], "montant": [df_fixe["montant"].sum()]})
                ], ignore_index=True)

            # Ajouter une ligne vide
            feuille = pd.concat([feuille, pd.DataFrame({"Section": [""]})], ignore_index=True)

            # Ajouter les dépenses journalières
            if not df_jour.empty:
                feuille = pd.concat([
                    feuille,
                    pd.DataFrame({"Section": ["Dépenses journalières"]}),
                    df_jour,
                    pd.DataFrame({"Section": ["Total journalières"], "montant": [df_jour["montant"].sum()]})
                ], ignore_index=True)

            # Ajouter total général du mois
            total_mois = df_mois["montant"].sum()
            feuille = pd.concat([
                feuille,
                pd.DataFrame({"Section": ["Total du mois"], "montant": [total_mois]})
            ], ignore_index=True)

            # Export dans une feuille nommée par le mois
            feuille.to_excel(writer, sheet_name=mois, index=False)

    return True
