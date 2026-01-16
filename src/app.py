import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
#from datetime import datetime
import plotly.express as px

# 1. Connexion (à adapter avec ton URL)
url = "https://docs.google.com/spreadsheets/d/1ZWOQWdYI7CXen4RRkvKkWnRTA_xydKO0sZHwFdGzj7M/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Chargement des données
@st.cache_data(ttl=600)
def get_clean_data():
    # Lecture de des onglets data_valo et data_vers
    df_valo = conn.read(spreadsheet=url, worksheet="data_valo")
    
    # Transformation de "Wide" à "Long" (Melt)
    # On garde Produit, Véhicule, Plateforme et on bascule les dates en lignes
    df_long_valo = df_valo.melt(
        id_vars=['Produit', 'Portefeuille', 'Plateforme'], 
        var_name='Date', 
        value_name='Valeur'
    )
    
    # Nettoyage des dates
    df_long_valo['Date'] = pd.to_datetime(df_long_valo['Date'], dayfirst=True, errors='coerce')
    df_long_valo = df_long_valo[df_long_valo['Date'] <  pd.Timestamp.now()]
    
    # Nettoyage des données (important !)
    # On retire les espaces dans les nombres et on convertit en numérique
    df_long_valo['Valeur'] = (
        df_long_valo['Valeur']
        .astype(str)
        .replace(r'[\s\xa0]', '', regex=True) # Enlever les espaces
        .str.replace(',', '.')                # Remplacer virgule par point
    )
    df_long_valo['Valeur'] = pd.to_numeric(df_long_valo['Valeur'], errors='coerce').fillna(0)
    
    return df_long_valo

# 3. Récupération des données
df = get_clean_data()

# 4. Interface et Graphique
df_plot = df.groupby(['Date', 'Portefeuille'])['Valeur'].sum().reset_index()

ordre_portefeuille = ["Livret A", 
                      "LDDS", 
                      "Livret Bourso +",
                      "Compte-Courant", 
                      "Airliquide.fr",
                      "PEE",
                      "PEA",
                      "AV",
                      "CTO",
                      "Wallet"]

couleurs_perso = {
    "Livret A": "#b6d7a8", 
    "LDDS": "#93c47d", 
    "Livret Bourso +": "#6aa84f",
    "Compte-Courant": "#38761d", 
    "Airliquide.fr": "#9fc5e8",
    "PEE": "#e06666",
    "PEA": "#cc0000",
    "AV": "#c27ba0", 
    "CTO": "#f1c232",
    "Wallet": "#ff9900"
}

synthese_1 = px.bar(
    df_plot, 
    x="Date", 
    y="Valeur", 
    color="Portefeuille",
    title="<b>Mon épargne</b>",
    category_orders={"Portefeuille": ordre_portefeuille}, 
    color_discrete_map = couleurs_perso,
    template="plotly_white"
)

synthese_1.update_traces(
    hovertemplate="%{y:,.0f} €<extra></extra>" # <extra></extra> enlève le nom du portefeuille à droite
)
synthese_1.update_xaxes(type='category') # Rend les distances égales entre barres
synthese_1.update_layout(
    bargap=0.1, # POINT 1 : Élargit les barres (0 = collées, 1 = vide total)
    yaxis=dict(title="", showgrid=False, side="right", gridcolor="#f0f0f0"),
    xaxis=dict(title="", showgrid=False, tickformat="%b %y"),
    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, title=""),
    margin=dict(l=20, r=50, t=80, b=20),
    hovermode="closest" # Recommandé pour voir le total par date
)

st.plotly_chart(synthese_1, use_container_width=True)