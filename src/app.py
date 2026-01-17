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
    
    df_long_vers = df_vers.melt(
        id_vars=['Produit', 'Portefeuille', 'Plateforme'], 
        var_name='Date', 
        value_name='Versement'
    )

    # Nettoyage des dates
    df_long_valo['Date'] = pd.to_datetime(df_long_valo['Date'], dayfirst=True, errors='coerce')
    df_long_valo['Date'] = df_long_valo['Date'].dt.date # convertir en date pure yyyy-mm-dd
    df_long_valo = df_long_valo[df_long_valo['Date'] <  pd.Timestamp.now().date()]

    df_long_vers['Date'] = pd.to_datetime(df_long_vers['Date'], dayfirst=True, errors='coerce')
    df_long_vers['Date'] = df_long_vers['Date'].dt.date # convertir en date pure yyyy-mm-dd
    df_long_vers = df_long_vers[df_long_vers['Date'] <  pd.Timestamp.now().date()]

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
    df_map['Pourcentage'] = (
    df_map['Pourcentage']
    .astype(str)                  # Force en texte pour pouvoir utiliser .str
    .str.replace('%', '')         # Enlève le signe %
    .str.replace(',', '.')        # Remplace virgule par point (format FR)
    )
    df_map['Pourcentage'] = pd.to_numeric(df_map['Pourcentage'], errors='coerce').fillna(0)

    return df_long_valo, df_long_vers, df_map

# 3. Récupération des données
df_valo, df_vers, df_map = get_all_data()

# 4. Création de l'UI
# sélection des dates
liste_dates_obj = sorted(df_valo['Date'].unique()) 
liste_dates_str = [d.strftime('%d/%m/%Y') for d in liste_dates_obj] # conversion en string

# Création d'une barre latérale de contrôle
st.sidebar.header("⚙️ Paramètres")

# création d'un slider sur le côté
date_selectionnee_fmt = st.sidebar.select_slider(
    "Faites glisser pour changer de date :",
    options=liste_dates_str,
    value=liste_dates_str[-1] # Par défaut, on se place sur la date la plus récente (à droite)
)

date_cible = pd.to_datetime(date_selectionnee_fmt, dayfirst=True).date()

# 5. Interface et Graphique
#### Synthese 1 ###
df_plot = df_valo[df_valo['Date'] <= date_cible] # filtrage dynamique

df_plot = df_plot.groupby(['Date', 'Portefeuille'])['Valeur'].sum().reset_index()
df_plot = df_plot.sort_values('Date') # ordre chrono
df_plot['Date_Labels'] = pd.to_datetime(df_plot['Date']).dt.strftime('%d/%m/%Y') # reconversion date python puis en charactères

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

couleurs_portefeuille = {
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
    x="Date_Labels", 
    y="Valeur", 
    color="Portefeuille",
    title="<b>Mon épargne</b>",
    category_orders={"Portefeuille": ordre_portefeuille}, 
    color_discrete_map = couleurs_portefeuille,
    template="plotly_white"
)

synthese_1.update_xaxes(type='category',title="", showgrid=False, tickangle=-40) # Rend les distances égales entre barres
synthese_1.update_layout(
    bargap=0.3, # Élargit les barres (0 = collées, 1 = vide total)
    yaxis=dict(
        range=[0, df_valo.groupby('Date')['Valeur'].sum().max() * 1.1], # Fixe le max à +10% du record historique
        title="", showgrid=False, side="right",tickformat=",",ticksuffix=" €"),
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

### Synthese 2 ### 
# Création de l'anneau
couleurs_classe_actifs = {
    "Action": "#ea4335",
    "Obligation": "#4285f4",
    "Cash": "#34a853",
    "Or": "#fbbc04",
    "Crypto": "#ff9900",
    "Métaux": "#f1caad",
    "Divers": "#8e7cc3"
}

ordre_actifs = ["Action", "Obligation","Cash", "Or", "Crypto", "Métaux", "Divers"]

# data_valo filtrée uniquement sur date_cible
df_now = df_valo[df_valo['Date'] == date_cible]

# Merge avec le mapping (Dimension Classe d'actif)
df_alloc = pd.merge(
    df_now, 
    df_map[df_map['Dimension'] == "Classe d'actif"], 
    on="Produit"
)

df_alloc['Valeur_Ponderee'] = df_alloc['Valeur'] * df_alloc['Pourcentage']

# somme par la sous catégorie "Classe d'actif"
df_donut = df_alloc.groupby('Sous-Catégorie')['Valeur_Ponderee'].sum().reset_index()

synthese_2 = px.pie(
    df_donut, 
    names='Sous-Catégorie', 
    values='Valeur_Ponderee',
    hole=0.5, # C'est ce paramètre qui transforme le camembert en anneau
    color='Sous-Catégorie',
    color_discrete_map= couleurs_classe_actifs,
    category_orders={"Sous-Catégorie": ordre_actifs},
    title=f"<b>Mon allocation au {date_selectionnee_fmt}</b>"
)

synthese_2.update_traces(
    textinfo='percent+label',
    textposition='outside',
    rotation=45,
    hovertemplate="<b>%{label}</b><br> %{value:,.0f} €<extra></extra>"
)

synthese_2.update_layout(
    separators=", ",
    showlegend=False,
    legend=dict(orientation="v", 
        yanchor="top", y=0.8, 
        xanchor="right", x=-0.05),
    margin=dict(l=50, r=50, t=80, b=80),
    height=500
)

### KPIs en haut ###
total_patrimoine = df_now['Valeur'].sum() # kpi total patrimoine

### 6. Layout des graphique et KPI
# Agencement du centre
st.markdown(
    f"""
    <div style="padding-left: 5px; margin-bottom: 20px;">
        <span style="color: gray; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px;">Patrimoine total au {date_selectionnee_fmt} :</span>
        <span style="color: #666666; font-size: 1.1em; font-weight: 500; margin-left: 10px;">{total_patrimoine:,.0f} €</span>
    </div>
    """, 
    unsafe_allow_html=True
)

col1, col2 = st.columns([1.5, 1.1]) 

with col1:
    st.plotly_chart(synthese_1, use_container_width=True)
with col2:
    st.plotly_chart(synthese_2, use_container_width=True)
