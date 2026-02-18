##### 0. Importation et paramétrages
# les packages
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
#from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# largeur d'écran streamlit
st.set_page_config(layout="wide")

# fond d'écran de l'app :)
img_url = "https://raw.githubusercontent.com/gjuin/monfinary2/342da2d2bb2fde053acc12f25a9b80c35bbedfd2/pic/Gemini_Generated_Image_5523w75523w75523.png"

def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        /* On crée un calque spécifique derrière l'application */
        .stApp::before {{
            filter: brightness(50%);
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: -1; /* Indispensable pour ne pas bloquer les clics */
            
            /* Mon image avec le filtre blanc pour la lisibilité */
            background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.95)),
                              url("{img_url}");
            
            background-attachment: fixed;
            background-size: cover;
            background-position: center 5%;
            
            /* Effet de traveling / zoom léger */
            animation: slow_pan 80s ease-in-out infinite;
        }}

        /* Animation pour le mouvement de l'image */
        @keyframes slow_pan {{
            0% {{ transform: scale(1.0); background-position: center; }}
            50% {{ transform: scale(1.1); background-position: top; }}
            100% {{ transform: scale(1.0); background-position: center; }}
        }}

        /* On s'assure que les fonds des widgets ne masquent pas l'image */
        .stApp {{
            background: transparent !important;
            
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_url()

# style CSS pour compacter la sidebar et zone principale
st.markdown("""
    <style>
    /* 1. Espace global entre widgets */
    [data-testid="stSidebarUserContent"] div.stElementContainer {
        margin-bottom: -0.9rem !important;
    }
    
    [data-testid="stSidebarUserContent"] label[data-testid="stWidgetLabel"] {
    margin-top: 0.100rem !important;
    }

    [data-testid="stSidebarUserContent"] [data-testid="stMarkdownContainer"] p {
    margin-bottom: 0.75rem !important;
    margin-top: 0rem !important;
    }

    /* 2. 📅 SLIDER DATE */
    [data-testid="stWidgetLabel"] p, 
    [data-testid="stSlider"] label {
        line-height: 1.0 !important;
    }

    /* 3. ⚙️ CASES À COCHER (OPTIONS uniquement) */
    [data-testid="stSidebarUserContent"] div.stCheckbox {
        margin-bottom: -0.313rem !important;
        padding-top: 0.125rem !important;
    }

    [data-testid="stSidebarUserContent"] div.stCheckbox label p {
        line-height: 1.0 !important;
    }
    
    /* 4. 📊 SELECTBOX (Allocation) */
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        font-size: 0.75rem !important;
        padding-top: 0.125rem !important;
        padding-bottom: 0.125rem !important;
    }

    /* 5. 🗂️ MULTISELECT COMPACT (Portefeuilles) */
    /* Tags sélectionnés : plus compacts et sur plusieurs colonnes */
    [data-testid="stSidebarUserContent"] [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    font-size: 0.625rem !important;
    padding: 0.125rem 0.375rem !important;
    margin: 0.125rem !important;
    height: auto !important;
    min-height: 1.25rem !important;
    }

    /* Conteneur des tags : permet le wrap sur plusieurs lignes */
    [data-testid="stSidebarUserContent"] [data-testid="stMultiSelect"] > div > div {
    flex-wrap: wrap !important;
    gap: 0.125rem !important;
    }

    /* Icône de fermeture (X) dans les tags */
    [data-testid="stSidebarUserContent"] [data-testid="stMultiSelect"] span[data-baseweb="tag"] svg {
    width: 0.65rem !important;
    height: 0.65rem !important;
    }

    /* Options dans le dropdown */
    [data-testid="stSidebarUserContent"] [data-testid="stMultiSelect"] > div
        font-size: 0.75rem !important;
        padding-top: 0.125rem !important;
        padding-bottom: 0.125rem !important;
    }

    /* ajuster l'espace au-dessus */
    [data-testid="stSidebarUserContent"] [data-testid="stMultiSelect"] {
    margin-top: 0.12rem !important;
    margin-bottom: 0rem !important;
    }

    /* Colorisation dynamique des tags du Multiselect */
    /* On cible les spans qui contiennent le nom du portefeuille */
    span[data-baseweb="tag"]:has(span[title="Livret A"]) { background-color: #b6d7a8 !important; }
    span[data-baseweb="tag"]:has(span[title="LDDS"]) { background-color: #93c47d !important; }
    span[data-baseweb="tag"]:has(span[title="Livret Bourso +"]) { background-color: #6aa84f !important; }
    span[data-baseweb="tag"]:has(span[title="Compte-Courant"]) { background-color: #38761d !important; }
    span[data-baseweb="tag"]:has(span[title="Airliquide.fr"]) { background-color: #9fc5e8 !important; }
    span[data-baseweb="tag"]:has(span[title="PEE"]) { background-color: #e06666 !important; }
    span[data-baseweb="tag"]:has(span[title="PEA"]) { background-color: #cc0000 !important; }
    span[data-baseweb="tag"]:has(span[title="AV Bourso"]) { background-color: #c27ba0 !important; }
    span[data-baseweb="tag"]:has(span[title="AV Mutavie"]) { background-color: #d0d0d0 !important; }
    span[data-baseweb="tag"]:has(span[title="CTO"]) { background-color: #f1c232 !important; }
    span[data-baseweb="tag"]:has(span[title="Wallet"]) { background-color: #ff9900 !important; }

    /* Ajustement de la couleur du texte pour la lisibilité si besoin */
    span[data-baseweb="tag"] span {
        color: white !important;
        font-weight: bold !important;
    }

    /* On s'assure que le bouton de suppression (X) reste blanc */
        span[data-baseweb="tag"] svg {
        fill: white !important;
    }


    /* 6. Dividers compacts */
    [data-testid="stSidebarUserContent"] hr {
        margin-top: 0.75rem !important;
        margin-bottom: 1.25rem !important;
    }

    /* 7. REMONTÉE SYNCHRONISÉE SIDEBAR & CONTENU */
    .stMain, [data-testid="stSidebar"] {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0rem !important;
        margin-bottom: 0rem !important;
    }

    [data-testid="stHeader"] {
        height: 0px !important;
        background: transparent !important;
    }

    /* 8. AJUSTEMENT INTERNE DES CONTENEURS */
    .stApp [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:first-child {
        margin-top: 0rem !important;
    }
    [data-testid="stSidebarUserContent"] {
        margin-top: -2.5em !important; 
    }
    div.block-container {
        padding-top: 0rem !important;
        max-width: 99% !important;
    }

    /* 9. BOUTON ICONE QUADRANTS */

    /* 13. UNIFORMISATION DES ESPACEMENTS APRÈS TITRES */
    
    </style>
    """, unsafe_allow_html=True)

# info sur les quadrants
@st.dialog("Comprendre les quadrants", width="large")
def show_help_quadrants():
    st.markdown("""
    ### 🧭 Les 4 Régimes Économiques
    **Principe** : L'économie oscille selon deux forces : l'**Inflation** et la **Croissance**. \n
    L'inflation est une mesure de l'évolution des prix, tandis que la croissance est une mesure de la valeur de l'accroissement du capital.
    Ces deux forces peuvent evoluer independament, donnant ainsi 4 cas de figures possibles. 
    Chaque quadrant favorise des actifs spécifiques. Ils offrent une grille de lecture macroeconomique de la finance et permettent a l'investisseur de se positionner. \n
    \n
    *Ce que vous payez c'est le prix, ce que vous achetez c'est la valeur.* - Warren Buffet
    
    \n
    **Les cycles :**
    """)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **⚡ Nord-Ouest : Bust Inflationiste**
        *Stagflation, hausse des coûts.*
        * La croissance chute alors que l'inflation reste haute (choc d'offre). Les banques centrales sont bloquées : monter les taux tue la croissance, les baisser nourrit l'inflation.
        * **Actifs :** Or, Cash, Obligations Courtes, Actions Défensives (Agro, Santé)
        
        **🌊 Sud-Ouest : Bust Déflationiste**
        *Récession classique, déflation.*
        * Contraction du PIB, hausse du chômage. La baisse de la demande brise les prix. Les taux chutent massivement.
        * **Actifs :** Obligations Longues, Cash, Actions Défensives (Agro, Santé)
        """)
    with col_b:
        st.markdown("""
        **🔥 Nord-Est : Boom Inflationiste**
        *Surchauffe, forte demande.*
        * L'économie tourne trop vite, les pénuries de main-d'œuvre et de matières premières poussent les prix. La demande excède l'offre. La banque centrale peut alors décider de monter les taux pour freiner la demande et ralentir l'économie.
        * **Actifs :** Matières Premières, Energie, Or, Actions de Rareté (Mines, Energie), Immobilier.
        
        **❄️ Sud-Est : Boom Déflationiste**
        *Croissance saine, "Goldilocks".*
        * C'est le cycle typique de la croissance capitaliste : accroissement du capital et baisse des prix. Tout le monde s'enrichit. Les entreprises les plus innovantes dominent. 
        * **Actifs :** Actions d'Efficacité (Tech, Croissance, Qualité, Cyclique - infra, industrie), Bitcoin, Obligations Longues
        """)
    
    st.markdown("""
    ### 🎯 Schéma des Transitions
    """)

    # Schéma textuel
    st.code("""
                   INFLATION (Nord)
                          ▲
          STAGFLATION     |    SURCHAUFFE
         (Inflationiste)  |   (Inflationiste)
              BUST        |        BOOM
                          |
    <--- BUST (Ouest) --------------> BOOM (Est)
                          |
          RÉCESSION       |    GOLDILOCKS
       (Déflationiste)    |  (Déflationiste)
              BUST        |        BOOM
                          ▼
                  DÉSINFLATION (Sud)
    """, language=None)
    
    st.markdown("""
    \n
    ### 🔄 Les Mécanismes de Transition & Rotations
    L'économie ne reste jamais figée ; elle circule entre ces quadrants. Anticiper la bascule est la clé de la performance. \n \n
    **A. La Surchauffe :** Passage de boom déflationiste à inflationiste
    * **Le mécanisme :** L'économie tourne à plein régime, les pénuries apparaissent, les salaires montent.
    * **Signes avant-coureurs :** Hausse des prix des intrants (énergie, matières premières), plein emploi, courbes de taux qui se pentifient (yield curve), ratio or/cuivre
    * **Rotation :** Vendre les Actions d'Efficacité (tech, sensibles aux taux) pour acheter des Actions de Rareté (énergie, matieres premieres) \n

    **B. Le Serrage Monétaire :** Passage de boom inflationiste au bust inflationniste
    * **Le mécanisme :** La Banque Centrale monte les taux violemment pour casser l'inflation. Le crédit s'assèche, la croissance cale mais les prix restent hauts.
    * **Signes avant-coureurs :** Inversion de la courbe des taux (taux courts > taux longs), chute du moral des entreprises (PMI).
    * **Rotation :** Vendre les Actions cycliques pour l'Or et le Cash. On cherche la protection du capital. \n \n
    
    **C. Le Crack Déflationniste :** Passage de bust inflationniste au bust déflationniste**
    * **Le mécanisme :** La "destruction de la demande". Le chômage monte, la consommation s'effondre, les prix finissent par baisser.
    * **Signes avant-coureurs :** Chute brutale du prix du pétrole, explosion des faillites, pivot de la Banque Centrale (baisse des taux).
    * **Rotation :** Vendre l'Or/Matières Premières pour les Obligations d'État Long Terme. Les taux baissent, donc le prix des obligations explose. \n \n

    **D. La Relance :** Passage de bust déflationniste au boom déflationniste**
    * **Le mécanisme :** Les injections de liquidités massives portent leurs fruits. La croissance repart sur une base de prix bas.
    * **Signes avant-coureurs :** Reprise des indicateurs avancés (PMI), retour de l'appétit pour le risque.
    * **Rotation :** Vendre les Obligations et le Cash pour revenir massivement sur les Actions. \n \n
    \n

    ### 🧠 Comment reconnaître le virage ?
    * Mouvement anti-horaire (classique) : Boom ➔ Surchauffe ➔ Stagflation ➔ Récession. C'est le cycle naturel de la dette.
    * Mouvement diagonal (choc) : Un "Cygne Noir" (Guerre, Pandémie) peut vous projeter du Boom Déflationniste (SE) au Bust Inflationniste (NO) en quelques semaines.  
    \n \n
    """)

    st.markdown("""
    \n
    ### 📊 Les différents styles d'actions
        """)
    
    st.markdown("""
    | Style d'Action | Caractéristiques | Secteurs Clés | Comportement vs Cycle |
    | :--- | :--- | :--- | :--- |
    | **Croissance** | Sociétés qui réinvestissent tout pour croître. Valorisation basée sur les profits futurs. | Tech, IA, Fintech, Cloud, Quantique | Explose en **Expansion**. Très sensible aux taux. |
    | **Cyclique** | Fortement liées à la santé de l'économie mondiale et à la demande. | Luxe, Mines, Industrie, Énergie | Suit la santé du PIB. Surperforment en **Surchauffe** ou début de cycle. Souffrent en **Récession**. |
    | **Qualité** | Marges élevées, peu d'endettement, barrières à l'entrée fortes (Moat). | Luxe (Top), Santé, Tech (Gafam) | Résilientes. Elles sont le "fond de portefeuille" qui traverse les crises. |
    | **Efficacité** | Sociétés qui optimisent la productivité par l'innovation (concept "Goldilocks") | Logiciels, Semi-conducteurs | Optimise la productivité mondiale. Profitent d'un monde avec peu d'inflation et une croissance technologique forte |
    | **Rareté** | Actifs tangibles ou finis qui protègent contre la dévaluation monétaire. | Or, Agriculture, Immo prestige | Les champions de la **Stagflation**. Valeur refuge quand le papier monnaie perd du pouvoir. |
    | **Défensives** | Besoins primaires. La demande reste stable même si l'économie s'effondre. | Infra, Santé, Conso de base, Utilities | Protègent le capital en **Ralentissement** et **Récession**. |

    \n
""")

    st.info("💡 **Conseil :** Si votre radar est équilibré sur les 4 quadrants, vous n'avez pas besoin de prédire la prochaine transition, votre patrimoine est prêt à l'absorber.")



##### 1. Connexion 
url = "https://docs.google.com/spreadsheets/d/1ZWOQWdYI7CXen4RRkvKkWnRTA_xydKO0sZHwFdGzj7M/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)



##### 2. Chargement des données
@st.cache_data(ttl=600)
def get_all_data():
    # Lecture de des onglets data_valo et data_vers
    df_valo = conn.read(spreadsheet=url, worksheet="data_valo")
    df_vers = conn.read(spreadsheet=url, worksheet="data_vers")
    df_map = conn.read(spreadsheet=url, worksheet="mapping")
    df_scenar = conn.read(spreadsheet=url, worksheet="scenar")
    df_date_creation = conn.read(spreadsheet=url, worksheet="crea_pf")
    
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

    # Nettoyage scenar
    for col in df_scenar.columns[2:]:
        df_scenar[col] = (
            df_scenar[col]
            .astype(str)
            .str.replace(',', '.')
            .pipe(pd.to_numeric, errors='coerce')
            .fillna(0)
        )
    
    df_scenar['Dimension'] = df_scenar['Dimension'].astype(str).str.strip()
    df_scenar['Sous-Catégorie'] = df_scenar['Sous-Catégorie'].astype(str).str.strip()

    # Nettoyage date_creation
    df_date_creation['Date_Creation'] = pd.to_datetime(df_date_creation['Date_Creation'], dayfirst=True, errors='coerce')


    return df_long_valo, df_long_vers, df_map, df_scenar, df_date_creation



##### 3. Récupération des données
df_valo, df_vers, df_map, df_scenar, df_date_creation = get_all_data()



##### 4. Mapping de style
# création de la superclasse d'actif : 4-5 sous-catgéories max action or oblig cash ...
df_classes = df_map[df_map['Dimension'] == "Classe d'actif"].copy()
df_classes['Sous-Catégorie'] = df_classes['Sous-Catégorie'].astype(str).str.split().str[0]
df_classes['Dimension'] = "Superclasse d'actif"
df_map = pd.concat([df_map, df_classes], ignore_index=True)

# gestion des portefeuilles
ordre_portefeuille = ["Livret A", 
                      "LDDS", 
                      "Livret Bourso +",
                      "Compte-Courant", 
                      "Airliquide.fr",
                      "PEE",
                      "PEA",
                      "AV Bourso",
                      "AV Mutavie",
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
    "AV Bourso": "#c27ba0",
    "AV Mutavie": "#d0d0d0",
    "CTO": "#f1c232",
    "Wallet": "#ff9900"
}

# gestion des styles par dimension
CONFIG_STYLES = {
    "Superclasse d'actif": {
        "couleurs": {
            "Action": "#ea4335", 
            "Obligation": "#4285f4", "Cash": "#34a853",
            "Or": "#fbbc04", "Crypto": "#ff9900", "Métaux": "#f1caad", "Divers": "#8e7cc3"
        },
        "ordre": ["Action", "Obligation","Cash", "Or", "Crypto", "Métaux", "Divers"]
    },
    "Classe d'actif": {
        "couleurs": {
            "Action": "#ea4335", 
            "Obligation CT": "#4285f4", "Obligation MT": "#4285f4", "Obligation LT": "#4285f4",
            "Cash 0%": "#34a853", "Cash Rémunéré": "#34a853",
            "Or": "#fbbc04", "Crypto": "#ff9900", "Métaux": "#f1caad", "Divers": "#8e7cc3"
        },
        "ordre": ["Action", "Obligation CT", "Obligation MT", "Obligation LT",
        "Cash 0%", "Cash Rémunéré", "Or", "Crypto", "Métaux", "Divers"]
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
            "Action": "#ea4335", "ETF": "#9900ff", "OPCVM": "#cccc00", 
            "Cash  0%": "#34a853", "Cash Rémunéré": "#34a853", 
            "Fonds €": "#0f2a8e",
            "Crypto": "#ff9900"
        },
        "ordre": ["Cash  0%", "Cash Rémunéré", "ETF", "Action", "OPCVM", "Crypto", "Fonds €"]
    }
}



##### 5. Création de l'UI
# Item 1 - Slider date 📅
liste_dates_obj = sorted(df_valo['Date'].unique()) 
liste_dates_str = [d.strftime('%d/%m/%Y') for d in liste_dates_obj]

st.sidebar.markdown("<p style='font-size: 1.1em; font-weight: bold; color: lightgray; margin-bottom: 0.5rem;'>DATE 📅</p>", unsafe_allow_html=True)
date_selectionnee_fmt = st.sidebar.select_slider(
    "Faites glisser pour changer de date :",
    options=liste_dates_str,
    value=liste_dates_str[-1]
)

date_cible = pd.to_datetime(date_selectionnee_fmt, dayfirst=True).date()

#  Item 2 - Filtre de portefeuille (multiselect) 🗂️
st.sidebar.divider()
st.sidebar.markdown("<p style='font-size: 1.1em; font-weight: bold; color: lightgray; margin-bottom: 0.5rem;'>PORTEFEUILLES 🗂️</p>", unsafe_allow_html=True)

portefeuilles_selectionnes = st.sidebar.multiselect(
    "Sélectionner :",
    options=ordre_portefeuille,
    default=ordre_portefeuille,
    label_visibility="collapsed"
)

#  Item 3 - Filtrer l'allocation selon la sous-catégorie 📊
st.sidebar.divider()
st.sidebar.markdown("<p style='font-size: 1.1em; font-weight: bold; color: lightgray; margin-bottom: 0.5rem;'>ALLOCATION 📊</p>", unsafe_allow_html=True)

ordre_dimensions = ["Superclasse d'actif", "Classe d'actif", "Géo", "Type de produit"]

dimensions_disponibles = [d for d in ordre_dimensions if d not in ["Sous-jacent", "Secteur"]]

try:
    default_index = dimensions_disponibles.index("Superclasse d'actif")
except ValueError:
    default_index = 0

dimension_choisie = st.sidebar.selectbox(
    "Regrouper par :",
    options=dimensions_disponibles,
    index=0
)

# Item 4 - Information Quadrant ℹ️
st.sidebar.divider()
# 1. Le titre et la ligne de texte en un seul bloc Markdown pour contrôler l'espace
st.sidebar.markdown("""
    <div style='margin-bottom: -0.938rem;'>
        <p style='font-size: 1.1em; font-weight: bold; color: transparent; margin-bottom: 0.625rem;'>INFOS ℹ️</p>
    </div>
    """, unsafe_allow_html=True)

# 2. Le bouton positionné par-dessus
# On utilise le CSS pour le remonter exactement au niveau du texte "Comprendre..."
if st.sidebar.button("LES QUADRANTS ℹ️", key="btn_quadrant_info", help="Ouvrir l'aide"):
    show_help_quadrants()

#  Item 5 - Exclure ou non les versements dans synthese_3 💸
st.sidebar.divider()
st.sidebar.markdown("<p style='font-size: 1.1em; font-weight: bold; color: lightgray; margin-bottom: 0.5rem;'>OPTIONS ⚙️</p>", unsafe_allow_html=True)
exclure_versements = st.sidebar.toggle("Exclure les versements 💸", value=False)

#  Item 6 - ajout d'un mode discret 🔒
# (pas de divider ici, on reste dans la section OPTIONS)
mode_discret = st.sidebar.checkbox("Mode discret 🔒", value=False)


##### 6. Interface et Graphique
if not portefeuilles_selectionnes:
    st.warning("Veuillez sélectionner au moins un portefeuille dans la barre latérale.")
    st.stop()

# largeur des graphiques
width_col1 = 500
width_col2 = 425
height = 325


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
    showlegend=False,
    legend=dict(
        orientation="v",
        yanchor="top", y=0.9, 
        xanchor="right", x=-0.05,
        traceorder ="reversed", #normal
        title=""),
    margin=dict(l=20, r=20, t=50, b=50),
    height= height,
    width = width_col1,
    hovermode="closest", # uniquement où je pointe
    paper_bgcolor='rgba(0,0,0,0)', # Fond extérieur
    plot_bgcolor='rgba(0,0,0,0)'   # Fond du tracé 
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
couleurs_map = config_actuelle.get("couleurs", {}) # None ou {} si la dimension n'a pas de config de style
ordre_cat = config_actuelle.get("ordre", {})

synthese_2 = px.pie(
    df_donut, 
    names='Sous-Catégorie', 
    values='Valeur_Ponderee',
    hole=0.5,
    color='Sous-Catégorie',
    color_discrete_map=couleurs_map, 
    category_orders={"Sous-Catégorie": ordre_cat} if ordre_cat else None, 
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
    margin=dict(l=50, r=50, t=60, b=40),
    height= height,
    width = width_col2,
    paper_bgcolor='rgba(0,0,0,0)', # Fond extérieur
    plot_bgcolor='rgba(0,0,0,0)'   # Fond du tracé 
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
    
    max_delta = df_histo_delta['Diff'].max() * 1.2
    min_delta = df_histo_delta['Diff'].min() * 2.5
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
        margin=dict(l=50, r=50, t=50, b=50),
        height= height,
        width = width_col2,
        paper_bgcolor='rgba(0,0,0,0)', # Fond extérieur
        plot_bgcolor='rgba(0,0,0,0)'   # Fond du tracé (entre les axes)
    )
else:
    # Si c'est la première date, on s'assure que df_delta est vide pour le message final
    df_delta = pd.DataFrame()
    synthese_3 = None

### Synthese 4 - l'antifragilité  ### 
df_map_filtree = df_map[df_map['Dimension'].isin(['Géo','Secteur',"Classe d'actif"])] # on ne garde que ces 3 dimensions
df_radar = pd.merge(df_map_filtree, df_now, on='Produit') # merge avec la valo à la date voulue et aux portefeuilles choisis
df_radar = pd.merge(df_radar, df_scenar, on=['Dimension', 'Sous-Catégorie']) # on enrichit avec les scores des dimensions par scénario

categories_exclues = ['Obligation CT', 'Obligation MT', 'Obligation LT', 'Cash 0%', 'Cash Rémunéré','Crypto','Métaux','Or']
df_radar = df_radar[~((df_radar['Dimension'] == 'Secteur') & 
      (df_radar['Sous-Catégorie'].isin(categories_exclues)))
      ]

df_radar['Valo_Ponderee'] = df_radar['Valeur'] * df_radar['Pourcentage'] # un produit peut être doublé voir triplé car ventilé par dimension

# Définir une règle de gestion sur le poids des dimensions
df_nb_dim = df_radar.groupby(['Plateforme', 'Produit'])['Dimension'].nunique().reset_index(name='nb_dim')

df_radar = pd.merge(df_radar, df_nb_dim, on= ['Plateforme', 'Produit'] )

def attribuer_poids(row):
    d = row['Dimension']
    n = row['nb_dim']
    
    # Cas où le produit est sur 3 dimensions
    if n == 3:
        poids = {"Classe d'actif": 0.50, "Secteur": 0.25, "Géo": 0.25}
        return poids.get(d, 0)
    
    # Cas où le produit est sur 2 dimensions (Classe d'actif + Géo ou Secteur)
    elif n == 2:
        poids = {"Classe d'actif": 0.70, "Géo": 0.30, "Secteur": 0.30}
        return poids.get(d, 0)
    
    # Cas par défaut (1 seule dimension)
    return 1.0

# On applique la règle sur chaque ligne
df_radar['poids_dimension'] = df_radar.apply(attribuer_poids, axis=1)


# calcul du score par produit et dimension
scenarios = df_scenar.columns[2:12]
df_prod = df_radar[['Produit', 'Dimension', 'Sous-Catégorie', 'Portefeuille', 'Plateforme', 'Valeur', 'Valo_Ponderee','nb_dim']].copy()
for scenario in scenarios:
    df_prod[scenario] = (
        df_radar['Pourcentage'] * df_radar['poids_dimension'] * df_radar[scenario]
    )


# la somme de Valo_Ventilee = l'épargne totale sur les portefeuilles choisis
df_prod['Valo_Ventilee'] = df_prod['Valo_Ponderee'] / df_prod['nb_dim']


# calcul du score par produit
cols_to_sum = list(scenarios) + ['Valo_Ventilee']
df_prod_agg = df_prod.groupby(['Produit', 'Portefeuille', 'Plateforme'], as_index=False)[cols_to_sum].sum()


# calcul du score sur la sélection
total_valo = df_prod_agg['Valo_Ventilee'].sum()
moyenne_finale = []
resultats_radar = []

for s in scenarios:
    # Calcul : Somme de (Score du produit * sa Valo) / Somme totale des Valo
    weighted_score = (df_prod_agg[s] * df_prod_agg['Valo_Ventilee']).sum() / total_valo
    moyenne_finale.append(weighted_score)
    resultats_radar.append(50 + (weighted_score * 50)) # score normalisé de 0 à 100


# Préparation au graphique
# on met les résultats dans un table à 2 colonnes (label et score)
scenarios_labels = [s.replace('_', ' ').title() for s in scenarios]
scores = resultats_radar

# On ferme la boucle pour le tracé
scores_plot = scores + [scores[0]]
angles_scenarios = scenarios_labels + [scenarios_labels[0]]

# le graphique
synthese_4 = go.Figure()

# Trace 1 : Le Halo (L'effet de lueur 3D)
synthese_4.add_trace(go.Scatterpolar(
    r=scores_plot,
    theta=angles_scenarios,
    mode='lines',
    line=dict(color='#4285F4', width=12, shape='linear'),
    opacity=0.15, # Très léger pour l'effet de flou
    hoverinfo='none'
))

# mon patrimoine
synthese_4.add_trace(go.Scatterpolar(
    r=scores_plot,
    theta=angles_scenarios,
    fill='toself',
    customdata=scenarios_labels + [scenarios_labels[0]],
    hovertemplate="<b>%{customdata}</b><br>%{r:.1f}<extra></extra>",
    line=dict(color='#4285F4', width=2),
    marker=dict(size=8, opacity=0, symbol='circle-open'), 
    fillcolor='rgba(66, 133, 244, 1)' # Bleu Google transparent
))

# le max
synthese_4.add_trace(go.Scatterpolar(
    r=[100] * len(angles_scenarios),
    theta=angles_scenarios,
    mode='markers',
    marker=dict(
        size=8, 
        color='#4285F4', # Bleu Google
        opacity=1,
        symbol='circle'
    ),
    hoverinfo='none',
    showlegend=False
))

synthese_4.update_layout(
    title="<b>Antifragilité et les Quatre Quadrants </b>",
    height= height,
    width = width_col1,
    margin=dict(l=20, r=20, t=60, b=40),
    polar=dict(
        bgcolor='rgba(0,0,0,0)', # Fond du radar transparent
        radialaxis=dict(
            visible=True,
            range=[0, 100],
            showticklabels=False,
            showgrid=True,
            showline=False, # Masque l'axe radial noir
            ticks="",       # Supprime les petits traits de graduation    
            gridcolor="rgba(128, 128, 128, 0.2)",
            linecolor='rgba(0,0,0,0)', # Cache la ligne d'axe centrale
        ),
        angularaxis=dict(
            direction="clockwise",
            period=8,
            gridcolor="rgba(128, 128, 128, 0.5)",
            linecolor="rgba(128, 128, 128, 0.5)", # Bordure extérieure
            tickfont=dict(size=11),
            rotation=90
        ),
        gridshape='linear' # transforme les cercles en lignes droites
    ),
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',  # Fond global transparent
    plot_bgcolor='rgba(0,0,0,0)'    # Fond du tracé transparent
)


### Synthese 5 - Performence par portefeuille  ### 
if idx_actuel > 0:
    # sommer les versements jusqu'à la date choisie et les dates précédentes
    df_vers_select = df_vers[
        (df_vers['Date'] <= date_cible) &                           # filtrage dynamique sur la date
        (df_vers['Portefeuille'].isin(portefeuilles_selectionnes))  # filtrage dynamique sur les portefeuilles
        & ~(df_vers['Portefeuille'].isin(['Compte-Courant']))
    ]
    df_vers_select = df_vers_select.groupby(['Portefeuille','Date'])['Versement'].sum().reset_index()
    df_vers_select = df_vers_select.sort_values(['Portefeuille', 'Date'])
    df_vers_select['Versement_Cumule'] = df_vers_select.groupby('Portefeuille')['Versement'].cumsum() # somme cumulée par portefeuille

    # sommer les valo à la date choisie et les dates précédentes
    df_valo_select = df_valo[
        (df_valo['Date'] <= date_cible) &                           # filtrage dynamique sur la date
        (df_valo['Portefeuille'].isin(portefeuilles_selectionnes))  # filtrage dynamique sur les portefeuilles
        & ~(df_vers['Portefeuille'].isin(['Compte-Courant']))
    ]
    df_valo_select = df_valo_select.groupby(['Portefeuille','Date'])['Valeur'].sum().reset_index()

    # merge
    df_perf = pd.merge(df_valo_select, df_vers_select, on=["Portefeuille","Date"])

    # calcul de perf
    df_perf['G_P'] = df_perf['Valeur'] - df_perf['Versement_Cumule']
    df_perf['Performence'] = df_perf['G_P']/df_perf['Versement_Cumule'] 
    df_perf['Date_Labels'] = pd.to_datetime(df_perf['Date']).dt.strftime('%d/%m/%Y') # reconversion date python puis en charactères

    # Création du graphique en courbe
    synthese_5 = px.line(
        df_perf,
        x='Date_Labels',
        y=['Performence'], 
        color='Portefeuille',
        color_discrete_map = couleurs_portefeuille,
        category_orders={"Portefeuille": ordre_portefeuille},
        title="<b>Performence par portefeuille</b>",
        template="plotly_white",
        markers=False,
        line_shape='spline'
    )

    # config des axes : suppression du grid, des labels, formats...
    synthese_5.update_xaxes(type='category', title="", showgrid=False, tickangle=-40) # Rend les distances égales entre barres
    max_perf = df_perf[
            (~df_perf['Portefeuille'].isin(['Compte-Courant','Wallet']))
            ]['Performence'].max() * 1.2
    min_perf = df_perf[
            (~df_perf['Portefeuille'].isin(['Compte-Courant','Wallet']))
            ]['Performence'].min() * 1,2
    tick_positions = np.linspace(min_perf, max_perf, 5)
    if mode_discret:
        y_axis_config2 = dict(
            range=[min_perf, max_perf],
            tickvals=tick_positions,
            ticktext=["•••• %"] * 5 , 
            title="",
            showgrid=False,
            side="right"
        )
    else:
        y_axis_config2 = dict(
            range=[min_perf, max_perf],
            title="",
            showgrid=False,
            side="right",
            tickformat=".1%"
        )

    synthese_5.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=50, b=50), # les marges de zone de dessin 
        font_color="white",
        hovermode="closest", 
        yaxis=y_axis_config2,
        height= height,
        width = width_col1,
        showlegend=False,
        legend=dict(orientation="v",
            yanchor="top", y=0.9, 
            xanchor="right", x=-0.05,
            traceorder ="reversed", #normal
            title="")
    )
    synthese_5.update_traces(
        line=dict(width=3, shape='spline', smoothing=1.3),
        
        hovertemplate="<b>%{fullData.name}</b> : •••• %<extra></extra>" if mode_discret 
        else "<b>%{fullData.name}</b> : %{y:.1%}<extra></extra>"
    )

else:
    # Si c'est la première date, on s'assure que df_delta est vide pour le message final
    df_delta = pd.DataFrame()
    synthese_5 = None


### Synthese 6 - Matrice de corrélation  ### 
# sommer les versements jusqu'à la date choisie et les dates précédentes
df_vers_correl = df_vers[
    (df_vers['Date'] <= date_cible) &                           # filtrage dynamique sur la date
    (df_vers['Portefeuille'].isin(portefeuilles_selectionnes))  # filtrage dynamique sur les portefeuilles
    & ~(df_vers['Portefeuille'].isin(['Compte-Courant','LDDS','Livret A','Livret Bourso +'])) # on exclut les portefeuilles uniquement cash
]
df_vers_correl = df_vers_correl.groupby(['Portefeuille','Date'])['Versement'].sum().reset_index()

# les valo par portefeuille par date
df_valo_correl = df_valo[
    (df_valo['Date'] <= date_cible) &                           # filtrage dynamique sur la date
    (df_valo['Portefeuille'].isin(portefeuilles_selectionnes))  # filtrage dynamique sur les portefeuilles
    & ~(df_valo['Portefeuille'].isin(['Compte-Courant','LDDS','Livret A','Livret Bourso +'])) # on exclut les portefeuilles uniquement cash
]
df_valo_correl = df_valo_correl.groupby(['Portefeuille', 'Date'])['Valeur'].sum().reset_index()

# on pivote
df_pivot_valo = df_valo_correl.pivot(index='Date', columns='Portefeuille', values='Valeur')
df_pivot_vers = df_vers_correl.pivot(index='Date', columns='Portefeuille', values='Versement').fillna(0)

# rendement relatif net : (Val_t - Vers_t - Val_t-1) / Val_t-1
df_perf_correl = (df_pivot_valo - df_pivot_vers - df_pivot_valo.shift(1)) / df_pivot_valo.shift(1) # On utilise .shift(1) pour récupérer la valeur du mois précédent
df_perf_correl = df_perf_correl.replace([np.inf, -np.inf], np.nan).dropna(how='all') # nettoyage (la première ligne sera NaN car pas de t-1)

# liste des portefeuilles choisis
portefeuilles_correl = pd.unique(df_valo_correl['Portefeuille'])

# la matrice
corr_matrix = df_perf_correl.corr().fillna(0)
#mask = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool) # on prépare un mask pour retirer la moitié nord-est
np.fill_diagonal(corr_matrix.values, np.nan)
#corr_matrix = corr_matrix.where(~mask)
text_values = corr_matrix.round(1).astype(str).replace('nan', '')

# Le graphique
synthese_6 = px.imshow(
    corr_matrix,
    text_auto=".1f", # une décimale
    aspect="auto",
    color_continuous_scale='BrBG', # Rouge (négatif) à Bleu (positif) Viridis BrBG Magma PiYG
    range_color=[-1, 1],
    labels=dict(color="Corrélation"),
    title="<b>Corrélation entre portefeuilles</b>",
    template="plotly_white"
)

synthese_6.update_layout(
    height=height,
    width=width_col2,
    margin=dict(l=0, r=0, t=50, b=50),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color="white",
    xaxis_title="",
    yaxis_title="",
    coloraxis_showscale=False # On cache la barre de couleur pour compacter
)

synthese_6.update_xaxes(type='category', title="", showgrid=False, tickangle=-40) 
synthese_6.update_yaxes(type='category', title="", showgrid=False) 

hover_temp = [
    ["<b>%{x}</b> et <b>%{y}</b> :<br>Coefficient : <b>%{z:.2f}</b><extra></extra>" if not np.isnan(val) else None 
     for val in row] 
    for row in corr_matrix.values
]

synthese_6.update_traces(
    text=text_values,
    texttemplate="%{text}",
    hovertemplate=(
        "<b>%{x}</b> et <b>%{y}</b> :<br>"
        "Coefficient : <b>%{z:.2f}</b>"
        "<extra></extra>"
    )
)
synthese_6.update_traces(hoverinfo="z", selector=dict(type='heatmap'))


### KPIs en haut ###
total_patrimoine = df_now['Valeur'].sum() # kpi total patrimoine
total_investi = df_vers[
    (df_vers['Date'] <= date_cible) & 
    (df_vers['Portefeuille'].isin(portefeuilles_selectionnes))
]['Versement'].sum()
plus_value_globale = total_patrimoine - total_investi
perf_globale = (plus_value_globale / total_investi * 100) if total_investi != 0 else 0


### Synthese 7 - Performance moyenne et projection  ### 

# 1. Outils et préparation
dict_dates = pd.Series(df_date_creation.Date_Creation.values, index=df_date_creation.Portefeuille).to_dict()
date_lancement_app = pd.to_datetime(df_valo['Date'].min())
ts_cible = pd.to_datetime(date_cible)

# Liste pour stocker les DataFrames de projection de chaque portefeuille
all_projections = []
# Liste pour l'historique global (pour le graphique)
all_hist = []

# 2. Boucle de calcul par portefeuille
for p in portefeuilles_selectionnes:
    # A. Historique et calcul du CAGR spécifique
    df_p_valo = df_valo[(df_valo['Portefeuille'] == p) & (pd.to_datetime(df_valo['Date']) <= ts_cible)].groupby('Date')['Valeur'].sum().reset_index()
    df_p_vers = df_vers[(df_vers['Portefeuille'] == p) & (pd.to_datetime(df_vers['Date']) <= ts_cible)].groupby('Date')['Versement'].sum().reset_index()
    
    if not df_p_valo.empty:
        df_p = pd.merge(df_p_valo, df_p_vers, on='Date', how='left').fillna(0)
        df_p['Date'] = pd.to_datetime(df_p['Date'])
        df_p = df_p.sort_values('Date')
        
        # Calcul du CAGR historique moyen (pondéré par la valeur du portefeuille au fil du temps)
        df_p['Cumul_Investi'] = df_p['Versement'].cumsum()
        date_ouverture = pd.to_datetime(dict_dates.get(p, date_lancement_app))
        df_p['Annees_Reelles'] = (df_p['Date'] - date_ouverture).dt.days / 365.25
        df_p['Perf_Brute'] = df_p['Valeur'] / df_p['Cumul_Investi'].clip(lower=1)
        df_p['CAGR_Point'] = (df_p['Perf_Brute'] ** (1 / df_p['Annees_Reelles'].clip(lower=0.1))) - 1
        
        # Nettoyage des taux aberrants
        df_p = df_p.replace([np.inf, -np.inf], np.nan).dropna(subset=['CAGR_Point'])
        
        # Le taux de projection propre à CE portefeuille (moyenne pondérée historique)
        cagr_p_moyen = (df_p['CAGR_Point'] * df_p['Valeur']).sum() / df_p['Valeur'].sum()
        
        # B. Création de la trajectoire future pour CE portefeuille
        cap_actuel_p = df_p['Valeur'].iloc[-1]
        dates_f = [ts_cible + pd.DateOffset(years=i) for i in range(0, 31)]
        # Formule : Capital * (1+r)^n (Versements à venir = 0 pour l'instant)
        valeurs_f = [cap_actuel_p * (1 + cagr_p_moyen)**i for i in range(0, 31)]
        
        df_proj_p = pd.DataFrame({'Date': dates_f, 'Valeur': valeurs_f})
        all_projections.append(df_proj_p)
        all_hist.append(df_p[['Date', 'Valeur']])

# 3. Aggregation des résultats pour le graphique
# Somme des historiques
df_hist = pd.concat(all_hist).groupby('Date')['Valeur'].sum().reset_index()
df_hist['Type'] = 'Historique'

# Somme des projections (la magie opère ici)
df_proj = pd.concat(all_projections).groupby('Date')['Valeur'].sum().reset_index()
df_proj['Type'] = 'Projection'

# Calcul d'un taux moyen affiché (pour la légende uniquement)
# C'est un taux implicite : (Total_Final / Total_Initial)^(1/30) - 1
val_init = df_proj['Valeur'].iloc[0]
val_final = df_proj['Valeur'].iloc[-1]
taux_implicite = (val_final / val_init)**(1/30) - 1 if val_init > 0 else 0

# Le graphique
synthese_7 = go.Figure()

# Historique
synthese_7.add_trace(go.Scatter(
    x=df_hist['Date'], y=df_hist['Valeur'],
    mode='lines', name='Historique Réel',
    line=dict(color='#00CC96', width=3),
    fill='tozeroy', fillcolor='rgba(0, 204, 150, 0.1)'
))

# Projection
synthese_7.add_trace(go.Scatter(
    x=df_proj['Date'], y=df_proj['Valeur'],
    mode='lines', name=f'Projection à {taux_implicite:.1%}/an',
    line=dict(color='#636EFA', width=3, dash='dash')
))

synthese_7.update_layout(
    title=f"<b>Trajectoire à 30 ans</b>",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color="white",
    height= height+100,
    #width = width_col1,
    xaxis=dict(showgrid=False),
    yaxis=dict(title="Capital (€)", gridcolor='rgba(255,255,255,0.1)'),
    legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center")
)


##### 7. Layout des graphique et KPI
# Gestion du texte pour le mode discret
if mode_discret:
    txt_patrimoine = "•••••• €"
    txt_investi = "•••••• €"
    txt_pv = "•••"
else:
    txt_patrimoine = f"{total_patrimoine:,.0f} €".replace(",", " ")
    txt_investi = f"{total_investi:,.0f} €".replace(",", " ")
    txt_pv = f"{plus_value_globale:+,.0f} € ({perf_globale:+.1f}%)".replace(",", " ")

# Affichage des KPIs en ligne
st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.625rem; border-bottom: 0.125rem solid #f0f2f6; margin-bottom: 1.25rem;">
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
col1, col2 = st.columns([1.4, 1.1]) 

with col1:
    st.plotly_chart(synthese_1, use_container_width=False)
with col2:
    if not df_delta.empty:
        st.plotly_chart(synthese_3, use_container_width=False) 
    else:
        # Si c'est vide (première date), on affiche un petit message discret
        st.info("Sélectionnez une date ultérieure pour voir les mouvements par rapport au mois précédent.")

st.markdown("<hr style='margin: 0rem 0rem 0.938rem 0rem; border: 0.063rem solid #f0f2f6;'>", unsafe_allow_html=True)
col3, col4 = st.columns([1.4, 1.1])

with col3:
    st.plotly_chart(synthese_4, use_container_width=False)

with col4:
    st.plotly_chart(synthese_2, use_container_width=False)

st.markdown("<hr style='margin: 0rem 0rem 0.938rem 0rem; border: 0.063rem solid #f0f2f6;'>", unsafe_allow_html=True)
col5, col6 = st.columns([1.4, 1.1])

with col5:
    if not df_delta.empty:
        st.plotly_chart(synthese_5, use_container_width=False)
    else:
        # Si c'est vide (première date), on affiche un petit message discret
        st.info("Sélectionnez une date ultérieure pour voir les performances d'une date à l'autre.")

with col6:
    if len(portefeuilles_correl) > 1:
        st.plotly_chart(synthese_6, use_container_width=False)
    else:
        st.info("Sélectionnez au moins 2 portefeuilles boursiers pour voir les corrélations.")

st.plotly_chart(synthese_7, use_container_width=True)

#st.markdown("<hr style='margin: 0rem 0rem 0.938rem 0rem; border: 0.063rem solid #f0f2f6;'>", unsafe_allow_html=True)

#st.write("### Données brutes du Radar")
#st.dataframe(df_prod_agg[df_prod_agg['Portefeuille'] == 'PEE'], use_container_width=True)
#st.dataframe(scores, use_container_width=True)
#st.dataframe(df_perf, use_container_width=True)
#st.dataframe(df_perf_correl, use_container_width=True)
#st.dataframe(df_vers_correl, use_container_width=True)
#st.dataframe(df_valo_correl, use_container_width=True)
#st.dataframe(df_p, use_container_width=True)