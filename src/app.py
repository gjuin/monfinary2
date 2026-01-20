##### 0. Importation et paramétrages
# les packages
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
#from datetime import datetime
import plotly.express as px

# largeur d'écran streamlit
st.set_page_config(layout="wide")

# style CSS pour compacter la sidebar
st.markdown("""
    <style>
    /* 1. Espace global entre widgets */
    [data-testid="stSidebarUserContent"] div.stElementContainer {
        margin-bottom: -12px !important;
    }

    /* 2. TEXTE DU SLIDER DATE ("Faites glisser...") */
    [data-testid="stWidgetLabel"] p, 
    [data-testid="stSlider"] label {
        font-size: 13px !important;
        line-height: 1.2 !important;
    }

    /* 3. CASES À COCHER (Portefeuilles) */
    [data-testid="stCheckbox"] {
        margin-bottom: -5px !important;  /* On réduit moins agressivement ici */
        padding-top: 2px !important;
    }
    [data-testid="stCheckbox"] label p {
        font-size: 13px !important;
        line-height: 1.4 !important; /* Ajoute un peu d'espace entre le texte et la case */
    }
    
    /* 4. TEXTE DU SELECTBOX (Dimensions d'allocation) */
    [data-testid="stSelectbox"] label p,
    [data-testid="stSelectbox"] div[data-testid="stMarkdownContainer"] p {
        font-size: 13px !important;
    }
    /* Taille du texte à l'intérieur du menu déroulant une fois sélectionné */
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        font-size: 13px !important;
        padding-top: 2px !important;
        padding-bottom: 2px !important;
        min-height: 30px !important;
    }

    /* 5. Dividers compacts */
    [data-testid="stSidebarUserContent"] hr {
        margin-top: 12px !important;
        margin-bottom: 12px !important;
    }

    /* 6. REMONTÉE SYNCHRONISÉE SIDEBAR & CONTENU */
    
    /* On applique la même marge négative aux deux blocs parents */
    .stMain, [data-testid="stSidebar"] {
        margin-top: -2.5rem !important;
    }

    /* On nettoie le Header pour qu'il ne bloque pas la remontée */
    [data-testid="stHeader"] {
        height: 0px !important;
        background: transparent !important;
    }

    /* 7. AJUSTEMENT INTERNE DES CONTENEURS */

    /* Côté Centre : On supprime les marges du premier bloc de KPIs */
    .stApp [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:first-child {
        margin-top: 0rem !important;
        padding-top: 2rem !important;
    }

    /* Côté Sidebar : On ajuste l'espace interne */
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
        margin-top: -2em !important; 
    }

    /* Nettoyage du conteneur de graphiques */
    div.block-container {
        padding-top: 1rem !important; /* Un peu d'air sous le haut de l'écran */
        max-width: 95% !important;
    }

    </style>
    """, unsafe_allow_html=True)

##### 1. Connexion (à adapter avec ton URL)
url = "https://docs.google.com/spreadsheets/d/1ZWOQWdYI7CXen4RRkvKkWnRTA_xydKO0sZHwFdGzj7M/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

##### 2. Chargement des données
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

    # Nettoyage mapping
    df_map = df_map.dropna(subset=['Dimension', 'Sous-Catégorie'])
    df_map['Dimension'] = df_map['Dimension'].astype(str).str.strip()
    df_map['Sous-Catégorie'] = df_map['Sous-Catégorie'].astype(str).str.strip()
    df_map['Pourcentage'] = (
        df_map['Pourcentage']
        .astype(str)                  # Force en texte pour pouvoir utiliser .str
        .str.replace('%', '')         # Enlève le signe %
        .str.replace(',', '.')        # Remplace virgule par point (format FR)
    )
    df_map['Pourcentage'] = pd.to_numeric(df_map['Pourcentage'], errors='coerce').fillna(0)

    return df_long_valo, df_long_vers, df_map

##### 3. Récupération des données
df_valo, df_vers, df_map = get_all_data()

##### 4. Mapping de style
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

CONFIG_STYLES = {
    "Classe d'actif": {
        "couleurs": {
            "Action": "#ea4335", "Obligation": "#4285f4", "Cash": "#34a853",
            "Or": "#fbbc04", "Crypto": "#ff9900", "Métaux": "#f1caad", "Divers": "#8e7cc3"
        },
        "ordre": ["Action", "Obligation", "Cash", "Or", "Crypto", "Métaux", "Divers"]
    },
    "Géo": {
        "couleurs": {
            "Amérique": "#bf0a30", "Europe": "#0f2a8e", "Asie": "#ffde00", "Afrique": "#016235",
            "Monde": "#4090e0"
        },
        "ordre": ["Amérique", "Europe", "Asie", "Afrique"]
    },
    "Type de produit": {
        "couleurs": {
            "Action": "#ea4335", "ETF": "#9900ff", "OPCVM": "#cccc00", "Cash": "#34a853", "Fonds €": "#0f2a8e",
            "Crypto": "#ff9900"
        },
        "ordre": ["Cash", "ETF", "Action", "OPCVM", "Crypto", "Fonds €"]
    }
}

##### 5. Création de l'UI
# Slider date
liste_dates_obj = sorted(df_valo['Date'].unique()) 
liste_dates_str = [d.strftime('%d/%m/%Y') for d in liste_dates_obj] # conversion en string

st.sidebar.markdown("<p style='font-size: 1.1em; font-weight: bold; color: lightgray; margin-bottom: 5px;'>DATE ⚙️</ :", unsafe_allow_html=True)
date_selectionnee_fmt = st.sidebar.select_slider(
    "Faites glisser pour changer de date :",
    options=liste_dates_str,
    value=liste_dates_str[-1] # Par défaut, on se place sur la date la plus récente (à droite)
)

date_cible = pd.to_datetime(date_selectionnee_fmt, dayfirst=True).date()

# Filtre de portefeuille (multiselect)
st.sidebar.divider()
st.sidebar.markdown("<p style='font-size: 1.1em; font-weight: bold; color: lightgray; margin-bottom: 5px;'>PORTEFEUILLES 🗂️</ :", unsafe_allow_html=True)

portefeuilles_selectionnes = [] # On crée une liste vide pour stocker les choix
liste_portefeuilles_dispo = sorted(df_valo['Portefeuille'].unique()) # On boucle sur chaque portefeuille unique pour créer sa case à cocher

for p in liste_portefeuilles_dispo:
    # On crée la checkbox. 'value=True' permet de les cocher par défaut
    if st.sidebar.checkbox(p, value=True, key=f"check_{p}"):
        portefeuilles_selectionnes.append(p)

# Filtrer l'allocation selon la sous-catégorie
st.sidebar.divider()
st.sidebar.markdown("<p style='font-size: 1.1em; font-weight: bold; color: lightgray; margin-bottom: 5px;'>ALLOCATION 📊</ :", unsafe_allow_html=True)

dimensions_disponibles = sorted(df_map['Dimension'].unique()) # On récupère les dimensions uniques présentes dans ton onglet mapping
dimensions_disponibles = [d for d in dimensions_disponibles if d not in ["Sous-jacent", "Secteur"]]

dimension_choisie = st.sidebar.selectbox(
    "Regrouper par :",
    options=dimensions_disponibles,
    index=0
)

# Exclure ou non les versements dans synthese_3
st.sidebar.divider()
exclure_versements = st.sidebar.toggle("Exclure les versements 💸", value=False)

# ajout d'un mode discret
st.sidebar.divider()
mode_discret = st.sidebar.checkbox("Mode discret 🔒", value=False)


##### 6. Interface et Graphique
if not portefeuilles_selectionnes:
    st.warning("Veuillez sélectionner au moins un portefeuille dans la barre latérale.")
    st.stop()

#### Synthese 1 - histo empilé par portefeuille ###
df_plot = df_valo[
    (df_valo['Date'] <= date_cible) &                           # filtrage dynamique sur la date
    (df_valo['Portefeuille'].isin(portefeuilles_selectionnes))  # filtrage dynamique sur les portefeuilles
]

df_plot = df_plot.groupby(['Date', 'Portefeuille'])['Valeur'].sum().reset_index()
df_plot = df_plot.sort_values('Date') # ordre chrono
df_plot['Date_Labels'] = pd.to_datetime(df_plot['Date']).dt.strftime('%d/%m/%Y') # reconversion date python puis en charactères

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

# Si mode discret on : on n'affiche rien (on vide les labels)
if mode_discret:
    # On définit 5 graduations réparties sur l'échelle max
    max_val = df_valo.groupby('Date')['Valeur'].sum().max() * 1.1
    vals = [max_val * i/4 for i in range(5)] # [0, 25%, 50%, 75%, 100%]
    
    y_axis_config = dict(
        range=[0, max_val],
        tickvals=vals,
        ticktext=["•••• €"] * 5, # Remplace chaque chiffre par les points
        title="",
        showgrid=False,
        side="right"
    )
else:
    y_axis_config = dict(
        range=[0, df_valo.groupby('Date')['Valeur'].sum().max() * 1.1],
        title="",
        showgrid=False,
        side="right",
        tickformat=",",
        ticksuffix=" €"
    )

synthese_1.update_layout(
    bargap=0.3, # Élargit les barres (0 = collées, 1 = vide total)
    yaxis=y_axis_config,
    separators=", ", # Définit l'espace comme séparateur de milliers
    #xaxis=dict(title="", showgrid=False, tickangle=-40),
    legend=dict(
        orientation="v",
        yanchor="top", y=0.8, 
        xanchor="right", x=-0.05,
        traceorder ="reversed", #normal
        title=""),
    margin=dict(l=50, r=50, t=50, b=50),
    height= 400,
    hovermode="closest" # uniquement où je pointe
)
synthese_1.update_traces(
    hovertemplate="<b>%{fullData.name}</b> : •••• €<extra></extra>" if mode_discret else "<b>%{fullData.name}</b> : %{y:,.0f} €<extra></extra>"
)

### Synthese 2 - anneau circulaire dynamique ### 
# data_valo filtrée uniquement sur date_cible
df_now = df_valo[
    (df_valo['Date'] == date_cible) &
    (df_valo['Portefeuille'].isin(portefeuilles_selectionnes))
]

# Merge avec le mapping (Dimension dynamique selon le filtre)
df_alloc = pd.merge(
    df_now, 
    df_map[df_map['Dimension'] == dimension_choisie], 
    on="Produit"
)

df_alloc['Valeur_Ponderee'] = df_alloc['Valeur'] * df_alloc['Pourcentage']

# somme par la sous catégorie "Classe d'actif"
df_donut = df_alloc.groupby('Sous-Catégorie')['Valeur_Ponderee'].sum().reset_index()

# on récupère la config spécifique à la dimension choisie
config_actuelle = CONFIG_STYLES.get(dimension_choisie, {}) # .get() permet de ne pas planter si la dimension n'est pas encore définie dans CONFIG_STYLES
couleurs_map = config_actuelle.get("couleurs", None)
ordre_cat = config_actuelle.get("ordre", None)

synthese_2 = px.pie(
    df_donut, 
    names='Sous-Catégorie', 
    values='Valeur_Ponderee',
    hole=0.5,
    color='Sous-Catégorie',
    color_discrete_map=couleurs_map, # Applique tes couleurs personnalisées
    category_orders={"Sous-Catégorie": ordre_cat}, # Applique ton ordre
    title=f"<b>Répartition par {dimension_choisie}</b>",
    template="plotly_white"
)

synthese_2.update_traces(
    textinfo='percent+label' if not mode_discret else 'label',
    textposition='outside',
    rotation=90,
    hovertemplate="<b>%{label}</b><br>•••• €<extra></extra>" if mode_discret else "<b>%{label}</b><br> %{value:,.0f} €<extra></extra>"
)

synthese_2.update_layout(
    separators=", ",
    showlegend=False,
    legend=dict(
        orientation="v",
        yanchor="top", y=0.8, 
        xanchor="right", x=-0.05,
        title=""),
    margin=dict(l=50, r=50, t=50, b=50),
    height=400
)

### Synthese 3 - les mouvements du patrimoine T - T-1 ### 
# (avec ou hors versement en option ?)
idx_actuel = liste_dates_obj.index(date_cible)

# calcul des mouvements
if idx_actuel > 0:
    date_precedente = liste_dates_obj[idx_actuel - 1]
    
    # 1. Calcul de la variation de valeur totale (A)
    val_t = df_now.groupby('Portefeuille')['Valeur'].sum()
    val_t_moins_1 = df_valo[
        (df_valo['Date'] == date_precedente) & 
        (df_valo['Portefeuille'].isin(portefeuilles_selectionnes))
    ].groupby('Portefeuille')['Valeur'].sum()
    
    delta_total = (val_t - val_t_moins_1).fillna(0)
    
    # 2. Gestion des versements (B)
    if exclure_versements:
        # On somme les versements enregistrés entre la date précédente (exclue) et la date cible (incluse)
        mask_vers = (df_vers['Date'] > date_precedente) & \
                    (df_vers['Date'] <= date_cible) & \
                    (df_vers['Portefeuille'].isin(portefeuilles_selectionnes))
        
        vers_periode = df_vers[mask_vers].groupby('Portefeuille')['Versement'].sum().fillna(0)
        # Variation Nette = Variation Totale - Versements
        df_delta = (delta_total - vers_periode).reset_index()
    else:
        df_delta = delta_total.reset_index()

    df_delta.columns = ['Portefeuille', 'Variation']
    df_delta['Variation'] = df_delta['Variation'].round(0) # Arrondi à l'euro dès le calcul
    df_delta = df_delta.sort_values('Variation', ascending=True) # On trie pour avoir les plus grosses hausses en haut

    # calcul du titre dynamique
    total_variation = df_delta['Variation'].sum()
    color_var = "#34a853" if total_variation >= 0 else "#ea4335"

    if mode_discret:
        val_affichage = "•••• €"
    else:
        val_affichage = f"{total_variation:+,.0f} €".replace(",", " ")
    
    txt_total_var = f"<span style='color:{color_var};'>{val_affichage}</span>"

    if exclure_versements:
        titre_graph = f"<b>Performance nette : {txt_total_var}</b> <br><span style='font-size:0.8em; color:gray;'>(hors versements au {date_cible.strftime('%d/%m/%Y')} vs {date_precedente.strftime('%d/%m/%Y')})</span>"
    else:
        titre_graph = f"<b>Variation totale : {txt_total_var}</b> <br><span style='font-size:0.8em; color:gray;'>(avec versements au {date_cible.strftime('%d/%m/%Y')} vs {date_precedente.strftime('%d/%m/%Y')})</span>"

    # --- Bornes fixes de l'axe X ---
    df_histo_delta = df_valo.groupby(['Date', 'Portefeuille'])['Valeur'].sum().reset_index()
    df_histo_delta['Prev_Valeur'] = df_histo_delta.groupby('Portefeuille')['Valeur'].shift(1)
    df_histo_delta['Diff'] = df_histo_delta['Valeur'] - df_histo_delta['Prev_Valeur']
    
    max_delta = df_histo_delta['Diff'].max() * 1.15
    min_delta = df_histo_delta['Diff'].min() * 1.15
    range_x = [min_delta if min_delta < 0 else -100, max_delta if max_delta > 0 else 100]

    # --- Génération du graphique ---
    df_delta['Couleur'] = df_delta['Variation'].apply(lambda x: '#34a853' if x >= 0 else '#ea4335')

    synthese_3 = px.bar(
        df_delta,
        x='Variation',
        y='Portefeuille',
        orientation='h',
        title=titre_graph,
        text='Variation',
        template="plotly_white",
        color='Couleur',
        color_discrete_map="identity"
    )
    
    # Formatage des étiquettes (Mode Discret inclus)
    text_template = '•••• €' if mode_discret else '%{text:,.0f} €'
    
    synthese_3.update_traces(
        texttemplate=text_template, 
        textposition='outside',
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>•••• €<extra></extra>" if mode_discret else "<b>%{y}</b><br>%{x:+.0f} €<extra></extra>"
    )

    synthese_3.update_layout(
        xaxis=dict(title="", range=range_x, showgrid=False, zeroline=True, zerolinewidth=2, zerolinecolor='grey', showticklabels=False),
        yaxis=dict(title="", showgrid=False),
        separators=", ",
        showlegend=False,
        margin=dict(l=50, r=50, t=60, b=50),
        height=400
    )
else:
    # Si c'est la première date, on s'assure que df_delta est vide pour le message final
    df_delta = pd.DataFrame()
    synthese_3 = None

### KPIs en haut ###
total_patrimoine = df_now['Valeur'].sum() # kpi total patrimoine
total_investi = df_vers[
    (df_vers['Date'] <= date_cible) & 
    (df_vers['Portefeuille'].isin(portefeuilles_selectionnes))
]['Versement'].sum()
plus_value_globale = total_patrimoine - total_investi


##### 7. Layout des graphique et KPI
# Gestion du texte pour le mode discret
if mode_discret:
    txt_patrimoine = "•••••• €"
    txt_investi = "•••••• €"
    txt_pv = "•••"
else:
    txt_patrimoine = f"{total_patrimoine:,.0f} €".replace(",", " ")
    txt_investi = f"{total_investi:,.0f} €".replace(",", " ")
    # Calcul du % de performance globale
    perf_globale = (plus_value_globale / total_investi * 100) if total_investi != 0 else 0
    txt_pv = f"{plus_value_globale:+,.0f} € ({perf_globale:+.1f}%)".replace(",", " ")

# Affichage des KPIs en ligne
st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 2px solid #f0f2f6; margin-bottom: 20px;">
        <div>
            <span style="color: gray; font-size: 0.8em; text-transform: uppercase;">Patrimoine Total</span><br>
            <span style="font-size: 1.5em; font-weight: 700; color: #1f77b4;">{txt_patrimoine}</span>
        </div>
        <div style="text-align: center;">
            <span style="color: gray; font-size: 0.8em; text-transform: uppercase;">Total Investi</span><br>
            <span style="font-size: 1.2em; font-weight: 600; color: #666666;">{txt_investi}</span>
        </div>
        <div style="text-align: right;">
            <span style="color: gray; font-size: 0.8em; text-transform: uppercase;">Plus-value Latente</span><br>
            <span style="font-size: 1.2em; font-weight: 600; color: {'#34a853' if plus_value_globale >= 0 else '#ea4335'};">{txt_pv}</span>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# Layout des graphiques
col1, col2 = st.columns([1.5, 1.1]) 

with col1:
    st.plotly_chart(synthese_1, use_container_width=True)
with col2:
    # Si le donut est trop bas, on peut forcer une marge négative ici
    st.plotly_chart(synthese_2, use_container_width=True)

st.markdown("<hr style='margin: 0px 0px 15px 0px; border: 1px solid #f0f2f6;'>", unsafe_allow_html=True)
if not df_delta.empty:
    st.plotly_chart(synthese_3, use_container_width=True) # Affichage sur toute la largeur sous les deux autres graphiques
else:
    # Si c'est vide (première date), on affiche un petit message discret
    st.info("Sélectionnez une date ultérieure pour voir les mouvements par rapport au mois précédent.")