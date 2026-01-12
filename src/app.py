import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuration de la page (important pour le look mobile)
st.set_page_config(page_title="Mon Finary", layout="centered")

st.title("📊 Mon Finary")

# Connexion sécurisée à Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Remplace par l'URL complète de ton Google Sheet
    url = "https://docs.google.com/spreadsheets/d/1ZWOQWdYI7CXen4RRkvKkWnRTA_xydKO0sZHwFdGzj7M/edit?gid=0#gid=0"
    
    # Lecture des données
    # On ajoute ttl=0 pour forcer le rafraîchissement à chaque fois (pas de cache)
    df = conn.read(spreadsheet=url, ttl=0)

    # Affichage
    if not df.empty:
        st.subheader("Aperçu de mes actifs")
        st.dataframe(df, use_container_width=True)
        
        # Exemple de graphique si tu as des colonnes 'Date' et 'Valeur'
        st.line_chart(df.set_index('Date'))
    else:
        st.warning("Le fichier est vide ou inaccessible.")

except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.info("Vérifie que tu as partagé le Sheet avec l'email du Service Account.")