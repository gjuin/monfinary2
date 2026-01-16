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
def get_all_data():
    # Lecture de des onglets data_valo et data_vers
    df_valo = conn.read(spreadsheet=url, worksheet="data_valo")
    df_vers = conn.read(spreadsheet=url, worksheet="data_vers")
    df_map = conn.read(spreadsheet=url, worksheet="mapping")
    
    # Transformation de "Wide" à "Long" (Melt)
    # On garde Produit, Véhicule, Plateforme et on bascule les dates en lignes
    df_long_valo = df_valo.melt(
        id_vars=['Produit', 'Portefeuille', 'Plateforme'], 
        var_name='Date', 
        value_name='Valeur'
    )
    
    df_long_vers = df_valo.melt(
        id_vars=['Produit', 'Portefeuille', 'Plateforme'], 
        var_name='Date', 
        value_name='Versement'
    )

    # Nettoyage des dates
    df_long_valo['Date'] = pd.to_datetime(df_long_valo['Date'], dayfirst=True, errors='coerce')
    df_long_valo = df_long_valo[df_long_valo['Date'] <  pd.Timestamp.now()]

    df_long_vers['Date'] = pd.to_datetime(df_long_vers['Date'], dayfirst=True, errors='coerce')
    df_long_vers = df_long_vers[df_long_vers['Date'] <  pd.Timestamp.now()]

    # On retire les espaces dans les nombres et on convertit en numérique
    df_long_valo['Valeur'] = (
        df_long_valo['Valeur']
        .astype(str)
        .replace(r'[\s\xa0]', '', regex=True) # Enlever les espaces
        .str.replace(',', '.')                # Remplacer virgule par point
    )
    df_long_valo['Valeur'] = pd.to_numeric(df_long_valo['Valeur'], errors='coerce').fillna(0)
    
    df_long_vers['Versement'] = (
        df_long_vers['Versement']
        .astype(str)
        .replace(r'[\s\xa0]', '', regex=True) # Enlever les espaces
        .str.replace(',', '.')                # Remplacer virgule par point
    )
    df_long_vers['Versement'] = pd.to_numeric(df_long_vers['Versement'], errors='coerce').fillna(0)

    # Nettoyage du pourcentage (ex: "75%" -> 0.75)
    df_map['Pourcentage'] = df_map['Pourcentage'].str.rstrip('%').astype(float) / 100

    return df_long_valo, df_long_vers, df_map

# 3. Récupération des données
df_valo, df_vers, df_map = get_all_data()

# 4. Interface et Graphique
#### Synthese 1 ###
df_plot = df_valo.groupby(['Date', 'Portefeuille'])['Valeur'].sum().reset_index()
df_plot = df_plot.sort_values('Date') # ordre chrono
df_plot['Date'] = df_plot['Date'].dt.strftime('%d/%m/%Y') # conversion en charactères

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

synthese_1.update_xaxes(type='category',title="", showgrid=False, tickangle=-40) # Rend les distances égales entre barres
synthese_1.update_layout(
    bargap=0.3, # Élargit les barres (0 = collées, 1 = vide total)
    yaxis=dict(title="", showgrid=False, side="right", gridcolor="#f0f0f0",tickformat=",",ticksuffix=" €"),
    separators=", ", # Définit l'espace comme séparateur de milliers
    #xaxis=dict(title="", showgrid=False, tickangle=-40),
    legend=dict(
        orientation="v",
        yanchor="top", y=0.8, 
        xanchor="right", x=-0.05,
        traceorder ="reversed", #normal
        title=""),
    margin=dict(l=50, r=50, t=80, b=80),
    hovermode="closest" # uniquement où je pointe
)
synthese_1.update_traces(
    hovertemplate="<b>%{fullData.name}</b> : %{y:,.0f} €<extra></extra>"
)

st.plotly_chart(synthese_1, use_container_width=True)

### Synthese 2 ### (to be continued)
# --- 2. Préparation des données pour l'anneau (dernière date connue) ---
# On prend la valo la plus récente
derniere_date = df_valo['Date'].max()
df_recent = df_valo[df_valo['Date'] == derniere_date]

# Merger avec le mapping (Filtre sur Dimension == "Classe d'actif")
df_alloc = pd.merge(df_recent, df_map[df_map['Dimension'] == "Classe d'actif"], on="Produit")

# Calcul de la valeur pondérée : Valeur totale du produit * % d'allocation de la ligne
df_alloc['Valeur_Ponderee'] = df_alloc['Valeur'] * df_alloc['Pourcentage']

# --- 3. Création du graphique Sunburst ---
synthese_2 = px.sunburst(
    df_alloc,
    path=['Sous-Catégorie', 'Produit'], # Hiérarchie : Classe d'actif -> Produit
    values='Valeur_Ponderee',
    title=f"<b>Répartition au {derniere_date.strftime('%d/%m/%Y')}</b>",
    color='Sous-Catégorie',
    color_discrete_map={
        "Action": "#cc0000",
        "Obligation": "#c27ba0",
        "Cash": "#6aa84f",
        "Immo": "#38761d",
        "Crypto": "#ff9900"
    },
    template="plotly_white"
)

# --- 4. Cosmétique ---
synthese_2.update_traces(
    textinfo="label+percent entry",
    hovertemplate="<b>%{label}</b><br>Valeur : %{value:,.0f} €"
)

synthese_2.update_layout(
    margin=dict(t=80, l=0, r=0, b=0),
    separators=", "
)

st.plotly_chart(synthese_2, use_container_width=True)