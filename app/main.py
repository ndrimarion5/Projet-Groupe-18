"""EcoSort-Search : interface Streamlit pour la recherche et le tri de produits."""

import html

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"


@st.cache_resource
def get_session_http():
    """Reutilise les connexions HTTP au lieu d'en recreer a chaque rerun."""
    return requests.Session()


@st.cache_data(ttl=600, max_entries=50, show_spinner=False)
def rechercher_produits_api(mot_cle: str, max_results: int = 6):
    reponse = get_session_http().get(
        f"{API_URL}/search",
        params={"q": mot_cle, "max_results": max_results},
        timeout=60,
    )
    return reponse.status_code, reponse.json() if reponse.content else {}


@st.cache_data(ttl=3600, max_entries=100, show_spinner=False)
def telecharger_image(image_url: str):
    reponse = get_session_http().get(image_url, timeout=20)
    reponse.raise_for_status()
    return reponse.content, reponse.headers.get("content-type", "image/jpeg")


@st.cache_data(ttl=3600, max_entries=100, show_spinner=False)
def classifier_produit(titre: str, categorie: str, image_url: str):
    contenu_image, content_type = telecharger_image(image_url)
    fichiers = {"file": ("produit.jpg", contenu_image, content_type)}
    parametres = {"titre_produit": titre, "categorie": categorie}
    reponse = get_session_http().post(
        f"{API_URL}/classify",
        files=fichiers,
        params=parametres,
        timeout=60,
    )
    return reponse.status_code, reponse.json() if reponse.content else {}

st.set_page_config(page_title="EcoSort-Search", layout="wide")

# --- CSS STYLE PREMIUM AVEC ALIGNEMENT PARFAIT ---
st.markdown(
    """
    <style>
        /* ----- TRANSPARENCE TOTALE ----- */
        html, body, .stApp, .stApp > div, .stApp > div > div,
        [data-testid="stAppViewContainer"], [data-testid="stMain"],
        [data-testid="stMainBlockContainer"], [data-testid="stVerticalBlock"],
        [data-testid="stElementContainer"], [data-testid="stBlock"],
        .st-emotion-cache-* {
            background: transparent !important;
            background-color: transparent !important;
        }
        .stApp, .stMain, .stMainBlockContainer {
            background: transparent !important;
            background-color: transparent !important;
        }

        /* ----- CONTENEUR PRINCIPAL : largeur maîtrisée et centré ----- */
        .main-content {
            position: relative;
            z-index: 2;
            max-width: 1100px;
            margin: 0 auto;
            padding: 20px 60px;          /* Padding latéral augmenté */
        }

        /* ----- FOND DIVISÉ EN TROIS (bandes latérales larges) ----- */
        #bg-container {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: -3;
            display: flex;
            flex-wrap: nowrap;
            pointer-events: none;
        }
        #bg-left, #bg-right {
            flex: 0 0 200px;
            min-width: 160px;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        #bg-center {
            flex: 1;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-color: #0a1f18;
            animation: kenBurns 25s ease-in-out infinite alternate;
            filter: blur(8px) brightness(0.7);
            transform: scale(1.15);
        }
        @keyframes kenBurns {
            0% { transform: scale(1.15); }
            100% { transform: scale(1.28); }
        }

        #bg-left {
            background-image: url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=600&q=80');
        }
        #bg-center {
            background-image: url('https://static.vecteezy.com/system/resources/previews/022/715/810/large_2x/3d-rendering-green-recycle-sign-with-globe-on-background-save-the-world-and-environment-concept-generat-ai-free-photo.jpg');
        }
        #bg-right {
            background-image: url('https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=600&q=80');
        }

        /* Overlay pour lisibilité */
        #overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: -2;
            background: rgba(0, 0, 0, 0.55);
            pointer-events: none;
        }

        /* Ciel (effet de profondeur) */
        #sky {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 45%;
            z-index: -1;
            background: linear-gradient(180deg, rgba(10, 26, 42, 0.4) 0%, rgba(26, 58, 74, 0.2) 30%, rgba(42, 90, 74, 0.05) 60%, transparent 100%);
            pointer-events: none;
        }

        /* Soleil */
        .sun {
            position: fixed;
            top: 5%;
            right: 10%;
            width: 80px;
            height: 80px;
            background: radial-gradient(circle, #FFD700 0%, #FFA500 30%, transparent 70%);
            border-radius: 50%;
            opacity: 0.6;
            box-shadow: 0 0 100px #FFD70020;
            z-index: -1;
        }

        /* Nuages */
        .cloud {
            position: fixed;
            background: rgba(255, 255, 255, 0.06);
            border-radius: 100px;
            backdrop-filter: blur(2px);
            z-index: -1;
            animation: floatCloud 20s ease-in-out infinite;
        }
        .cloud-1 { width: 200px; height: 32px; top: 8%; left: 5%; }
        .cloud-2 { width: 150px; height: 26px; top: 16%; left: 65%; animation-duration: 25s; animation-direction: reverse; }
        .cloud-3 { width: 180px; height: 30px; top: 4%; left: 35%; animation-duration: 18s; animation-delay: 5s; }
        @keyframes floatCloud {
            0%, 100% { transform: translateX(0); }
            50% { transform: translateX(90px); }
        }

        /* Herbe */
        .grass-blade {
            position: fixed;
            bottom: 0;
            width: 2px;
            background: linear-gradient(to top, #2a5a3a, #3a7a4a);
            transform-origin: bottom center;
            border-radius: 2px;
            z-index: -1;
            animation: sway 3s ease-in-out infinite;
        }
        @keyframes sway {
            0%, 100% { transform: rotate(-5deg); }
            50% { transform: rotate(5deg); }
        }

        /* Fleurs, papillons, oiseaux, feuilles */
        .flower, .butterfly, .bird, .leaf {
            position: fixed;
            z-index: -1;
            font-size: 22px;
        }
        .flower { font-size: 20px; animation: sway 3s ease-in-out infinite; }
        .butterfly { font-size: 24px; animation: fly 14s ease-in-out infinite; }
        .bird { font-size: 18px; animation: flyBird 18s ease-in-out infinite; }
        .leaf { font-size: 26px; opacity: 0.3; animation: leafFloat 8s ease-in-out infinite; }

        @keyframes fly {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            25% { transform: translate(90px, -45px) rotate(8deg); }
            50% { transform: translate(180px, 0) rotate(0deg); }
            75% { transform: translate(90px, 45px) rotate(-8deg); }
        }
        @keyframes flyBird {
            0%, 100% { transform: translateX(0) translateY(0); }
            25% { transform: translateX(160px) translateY(-28px); }
            50% { transform: translateX(320px) translateY(12px); }
            75% { transform: translateX(160px) translateY(-18px); }
        }
        @keyframes leafFloat {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            25% { transform: translate(35px, -22px) rotate(90deg); }
            50% { transform: translate(70px, 0) rotate(180deg); }
            75% { transform: translate(35px, 22px) rotate(270deg); }
        }

        .flower-1 { left: 10%; bottom: 18%; animation-delay: 0s; }
        .flower-2 { left: 75%; bottom: 15%; animation-delay: 1.5s; }
        .flower-3 { left: 45%; bottom: 20%; animation-delay: 0.8s; }
        .flower-4 { left: 30%; bottom: 12%; animation-delay: 2s; }

        .butterfly-1 { top: 25%; left: 15%; animation-delay: 0s; }
        .butterfly-2 { top: 35%; left: 70%; animation-delay: 5s; }
        .butterfly-3 { top: 20%; left: 50%; animation-delay: 9s; }

        .bird-1 { top: 10%; left: 25%; animation-delay: 0s; }
        .bird-2 { top: 18%; left: 55%; animation-delay: 6s; }

        .leaf-1 { top: 15%; left: 8%; animation-delay: 0s; }
        .leaf-2 { top: 25%; right: 12%; animation-delay: 3s; }
        .leaf-3 { top: 10%; left: 40%; animation-delay: 6s; }

        /* ----- HEADER PREMIUM ----- */
        .ecosort-header-panel {
            background: rgba(8, 20, 15, 0.7);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border-radius: 24px;
            padding: 32px 48px;
            margin-bottom: 32px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 12px 48px rgba(0,0,0,0.5);
            text-align: center;
        }

        .ecosort-titre-wrapper {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 18px;
            flex-wrap: wrap;
        }

        .ecosort-icon {
            width: 52px;
            height: 52px;
            fill: none;
            stroke: #3b9eff;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
            filter: drop-shadow(0 0 12px rgba(59, 158, 255, 0.2));
        }

        .ecosort-titre {
            font-size: 3.8rem;
            font-weight: 800;
            margin: 0;
            background: linear-gradient(135deg, #3b9eff, #1a6bb0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 2px 30px rgba(59, 158, 255, 0.15);
        }

        .ecosort-soustitre {
            color: #b0d4f0;
            font-size: 1.5rem;
            margin-top: 10px;
            font-weight: 300;
            letter-spacing: 1px;
            text-shadow: 0 2px 12px rgba(0,0,0,0.3);
        }
        .ecosort-soustitre span {
            font-weight: 400;
            color: #8dc4f0;
        }

        /* ----- RECHERCHE COURT ET CENTRÉ (largeur réduite) ----- */
        .search-container {
            max-width: 380px;          /* réduit pour rester dans la zone centrale */
            margin: 0 auto;
            padding: 0 12px;
        }

        .stTextInput {
            position: relative;
        }
        .stTextInput::before {
            content: '';
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            width: 22px;
            height: 22px;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.5)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E") no-repeat center;
            background-size: contain;
            pointer-events: none;
            z-index: 1;
        }
        .stTextInput > div > div > input {
            padding-left: 48px !important;
            border-radius: 40px !important;
            background: rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            color: #ffffff !important;
            font-size: 17px !important;
            font-weight: 400 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 24px rgba(0,0,0,0.2) !important;
            height: 56px !important;
            width: 100% !important;
        }
        .stTextInput > div > div > input::placeholder {
            color: rgba(255,255,255,0.4) !important;
            font-weight: 300;
            font-size: 16px;
        }
        .stTextInput > div > div > input:focus {
            background: rgba(255,255,255,0.14) !important;
            border-color: #3b9eff !important;
            box-shadow: 0 0 30px rgba(59, 158, 255, 0.15), 0 4px 30px rgba(0,0,0,0.25) !important;
        }

        /* ----- BOUTON RECHERCHE ----- */
        .action-group {
            display: flex;
            align-items: center;
            gap: 18px;
            margin-top: 16px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .action-group .stButton {
            flex: 0 0 auto;
        }
        .action-group .stButton button {
            background: linear-gradient(135deg, #3b9eff, #1a6bb0) !important;
            border: none !important;
            border-radius: 40px !important;
            padding: 14px 32px !important;
            color: white !important;
            font-weight: 600 !important;
            font-size: 17px !important;
            letter-spacing: 0.5px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 24px rgba(59, 158, 255, 0.3) !important;
            min-width: 150px !important;
        }
        .action-group .stButton button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 40px rgba(59, 158, 255, 0.5) !important;
            background: linear-gradient(135deg, #2a8aee, #155a9a) !important;
        }

        /* ----- CARTES PRODUITS PREMIUM ----- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(10, 20, 16, 0.75) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 24px;
            border: 1px solid rgba(255,255,255,0.06);
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            padding: 0 !important;
            margin-bottom: 28px;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-10px) scale(1.01);
            box-shadow: 0 16px 60px rgba(0,0,0,0.5);
            border-color: rgba(59, 158, 255, 0.25);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 0 !important;
        }

        .ecosort-carte-image-wrap {
            width: 100%;
            aspect-ratio: 1 / 1;
            background: rgba(255,255,255,0.03);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .ecosort-carte-image {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            transition: transform 0.4s ease;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover .ecosort-carte-image {
            transform: scale(1.06);
        }

        .ecosort-carte-corps {
            padding: 18px 20px 20px 20px;
        }
        .ecosort-carte-titre {
            color: #ffffff !important;
            font-weight: 600;
            font-size: 1.5rem !important;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 4.5em;
            margin-bottom: 12px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.5);
        }
        .ecosort-carte-prix {
            color: #f5b342 !important;
            font-weight: 800;
            font-size: 2rem !important;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.5);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] div.stButton > button {
            background: linear-gradient(135deg, #1e7a4a, #145a32) !important;
            border-radius: 40px !important;
            padding: 16px 28px !important;
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            margin: 0 18px 18px 18px !important;
            width: calc(100% - 36px) !important;
            box-shadow: 0 2px 16px rgba(20, 90, 50, 0.4) !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] div.stButton > button:hover {
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 8px 36px rgba(20, 90, 50, 0.6) !important;
        }

        /* ----- RÉSULTAT POUBELLE ----- */
        .ecosort-resultat-poubelle {
            padding: 48px 32px;
            border-radius: 20px;
            text-align: center;
            margin-top: 16px;
            box-shadow: 0 12px 48px rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.08);
            backdrop-filter: blur(6px);
        }
        .ecosort-resultat-titre {
            font-size: 2rem;
            font-weight: 800;
            color: #FFFFFF;
            text-shadow: 0 2px 16px rgba(0,0,0,0.5);
        }
        .ecosort-resultat-detail {
            color: rgba(255,255,255,0.9);
            margin-top: 8px;
            font-size: 1.2rem;
            text-shadow: 0 1px 8px rgba(0,0,0,0.3);
        }

        /* ----- MESSAGE D'ATTENTE ----- */
        .waiting-message {
            color: #b0d4f0;
            font-size: 1.3rem;
            text-align: center;
            margin-top: 24px;
            padding: 18px;
            background: rgba(0,0,0,0.3);
            border-radius: 16px;
            backdrop-filter: blur(6px);
            border: 1px solid rgba(255,255,255,0.05);
        }

        /* ----- ANIMATION POUBELLE ----- */
        @keyframes sortirDuBas {
            0%   { transform: translateY(280px); opacity: 0; }
            70%  { transform: translateY(-18px); opacity: 1; }
            100% { transform: translateY(0); opacity: 1; }
        }
        @keyframes tomberDansPoubelle {
            0%   { transform: translate(-50%, -60px) rotate(0deg); opacity: 0; }
            10%  { opacity: 1; }
            80%  { transform: translate(-50%, 160px) rotate(360deg); opacity: 1; }
            100% { transform: translate(-50%, 180px) rotate(360deg); opacity: 0; }
        }
        .ecosort-poubelle-outer {
            position: fixed;
            top: 50%;
            right: 5%;
            transform: translateY(-50%);
            width: 250px;
            height: 290px;
            z-index: 9999;
            pointer-events: none;
            animation: sortirDuBas 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }
        .ecosort-poubelle-anim {
            position: relative;
            width: 100%;
            height: 100%;
        }
        .ecosort-dechet {
            position: absolute;
            top: -50px;
            left: 50%;
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #E8EDEA, #C5D0CA);
            border-radius: 8px;
            opacity: 0;
            animation: tomberDansPoubelle 0.9s ease-in forwards;
            animation-delay: 0.8s;
            box-shadow: 0 4px 16px rgba(0,0,0,0.4);
        }

        /* Responsive */
        @media (max-width: 1024px) {
            .main-content { max-width: 100%; padding: 20px 30px; }
            #bg-left, #bg-right { flex: 0 0 100px; min-width: 80px; }
            .search-container { max-width: 340px; }
        }
        @media (max-width: 768px) {
            .main-content { max-width: 100%; padding: 12px; }
            #bg-left, #bg-right { flex: 0 0 50px; min-width: 40px; }
            .ecosort-titre { font-size: 2.4rem; }
            .ecosort-header-panel { padding: 20px; }
            .ecosort-poubelle-outer { width: 160px; height: 190px; right: 2%; }
            .action-group { flex-direction: column; align-items: stretch; }
            .ecosort-carte-titre { font-size: 1.2rem !important; min-height: 3.6em; }
            .ecosort-carte-prix { font-size: 1.6rem !important; }
            .stTextInput > div > div > input { font-size: 16px !important; height: 52px !important; }
            .action-group .stButton button { font-size: 16px !important; padding: 12px 24px !important; }
            div[data-testid="stVerticalBlockBorderWrapper"] div.stButton > button { font-size: 1.1rem !important; padding: 12px 20px !important; }
            .search-container { max-width: 100%; padding: 0 16px; }
        }

        /* Mode plus leger pour eviter les ralentissements dans le navigateur */
        #bg-center {
            animation: none !important;
            filter: brightness(0.72) !important;
            transform: scale(1.04) !important;
        }
        .cloud, .flower, .butterfly, .bird, .leaf, .grass-blade {
            animation: none !important;
        }
        .grass-blade {
            display: none !important;
        }
    </style>

    <!-- Éléments du fond -->
    <div id="bg-container">
        <div id="bg-left"></div>
        <div id="bg-center"></div>
        <div id="bg-right"></div>
    </div>
    <div id="overlay"></div>
    <div id="sky"></div>
    <div class="sun"></div>
    <div class="cloud cloud-1"></div>
    <div class="cloud cloud-2"></div>
    <div class="cloud cloud-3"></div>

    <div class="flower flower-1">🌸</div>
    <div class="flower flower-2">🌺</div>
    <div class="flower flower-3">🌼</div>
    <div class="flower flower-4">🌷</div>

    <div class="butterfly butterfly-1">🦋</div>
    <div class="butterfly butterfly-2">🦋</div>
    <div class="butterfly butterfly-3">🦋</div>

    <div class="bird bird-1">🐦</div>
    <div class="bird bird-2">🐦</div>

    <div class="leaf leaf-1">🍃</div>
    <div class="leaf leaf-2">🍃</div>
    <div class="leaf leaf-3">🍃</div>

    """,
    unsafe_allow_html=True,
)

# --- CONTENU PRINCIPAL ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# HEADER
st.markdown(
    """
    <div class="ecosort-header-panel">
        <div class="ecosort-titre-wrapper">
            <svg class="ecosort-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2v4M12 22v-4M4 12H2M22 12h-2M4 4l2 2M20 20l-2-2M4 20l2-2M20 4l-2 2" />
                <path d="M12 6a6 6 0 0 0-6 6 6 6 0 0 0 6 6 6 6 0 0 0 6-6 6 6 0 0 0-6-6z" />
            </svg>
            <div class="ecosort-titre">EcoSort-Search</div>
        </div>
        <div class="ecosort-soustitre">
            <span>Recherchez, choisissez, triez</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Barre de recherche courte et centrée ---
st.markdown('<div class="search-container">', unsafe_allow_html=True)
with st.form("formulaire_recherche", border=False):
    mot_cle = st.text_input(
        "Recherche",
        placeholder="Que souhaitez-vous trier ?",
        label_visibility="collapsed",
    )
    lancer_recherche = st.form_submit_button("Rechercher")
st.markdown('</div>', unsafe_allow_html=True)

# --- Logique de recherche ---
if lancer_recherche and mot_cle.strip():
    try:
        with st.spinner("Recherche en cours..."):
            statut_recherche, donnees_recherche = rechercher_produits_api(mot_cle.strip(), max_results=6)
    except requests.exceptions.ConnectionError:
        st.error("Le service de recherche est momentanément indisponible. Réessayez dans un instant.")
        st.stop()
    except requests.exceptions.Timeout:
        st.error("La recherche prend trop de temps. Réessayez dans un instant.")
        st.stop()

    if statut_recherche == 200:
        st.session_state["produits"] = donnees_recherche.get("resultats", [])
        st.session_state["source_recherche"] = donnees_recherche.get("source", "inconnue")
        st.session_state.pop("produit_choisi", None)
        st.session_state.pop("resultat_classification", None)
        st.session_state.pop("show_waiting", None)
    elif statut_recherche == 503:
        st.warning("⚠️ Jumia demande une vérification de sécurité. Attendez puis réessayez.")
    else:
        st.error(f"❌ Erreur lors de la recherche (code {statut_recherche})")

# --- Affichage des produits ---
if "produits" in st.session_state:
    produits = st.session_state["produits"]
    nb_colonnes = 3

    if not produits:
        st.warning(
            "Aucun produit n'a ete trouve pour cette recherche. "
            "Essayez un mot-cle plus simple comme bouteille, calculatrice ou cahier."
        )
        st.stop()

    for debut in range(0, len(produits), nb_colonnes):
        colonnes = st.columns(nb_colonnes)

        for decalage, colonne in enumerate(colonnes):
            index = debut + decalage
            if index >= len(produits):
                continue

            produit = produits[index]

            with colonne:
                with st.container(border=True):
                    if produit.get("image"):
                        st.markdown(
                            f'<div class="ecosort-carte-image-wrap">'
                            f'<img class="ecosort-carte-image" '
                            f'loading="lazy" src="{html.escape(produit["image"], quote=True)}"></div>',
                            unsafe_allow_html=True,
                        )

                    titre = html.escape(produit.get("titre") or "Produit sans titre")
                    prix = html.escape(produit.get("prix") or "Prix indisponible")
                    st.markdown(
                        f"""
                        <div class="ecosort-carte-corps">
                            <div class="ecosort-carte-titre">{titre}</div>
                            <div class="ecosort-carte-prix">{prix}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if st.button("Choisir", key=f"choisir_{index}", width="stretch"):
                        st.session_state["produit_choisi"] = produit
                        st.session_state.pop("resultat_classification", None)
                        st.session_state["show_waiting"] = True
                        st.rerun()

# --- Section : produit choisi + résultat ---
if "produit_choisi" in st.session_state:
    produit = st.session_state["produit_choisi"]

    st.markdown("---")
    st.markdown("### Produit sélectionné")
    col_img, col_info = st.columns([1, 2])
    with col_img:
        if produit.get("image"):
            st.image(produit["image"], width=200)
    with col_info:
        st.markdown(f"**{produit.get('titre') or 'Produit sans titre'}**")
        st.markdown(f"*{produit.get('prix') or 'Prix indisponible'}*")

    result_placeholder = st.empty()

    if st.session_state.get("show_waiting", False):
        result_placeholder.markdown(
            '<div class="waiting-message">⏳ Analyse en cours, la poubelle arrive...</div>',
            unsafe_allow_html=True,
        )

    if "resultat_classification" not in st.session_state:
        if not produit.get("image"):
            st.error("❌ Aucune image disponible pour ce produit.")
        else:
            try:
                statut_classification, donnees_classification = classifier_produit(
                    produit.get("titre") or "",
                    produit.get("categorie", ""),
                    produit["image"],
                )
            except requests.exceptions.ConnectionError:
                st.error("Le service de classification est momentanément indisponible. Réessayez dans un instant.")
                st.stop()
            except requests.exceptions.Timeout:
                st.error("La classification prend trop de temps. Réessayez dans un instant.")
                st.stop()
            except requests.exceptions.RequestException as erreur:
                st.error(f"Impossible de récupérer l'image du produit : {erreur}")
                st.stop()

            if statut_classification == 200:
                st.session_state["resultat_classification"] = donnees_classification
                st.session_state["show_waiting"] = False
                st.rerun()
            else:
                st.error(f"❌ Erreur lors de la classification (code {statut_classification})")
                st.session_state["show_waiting"] = False

    if "resultat_classification" in st.session_state:
        resultat = st.session_state["resultat_classification"]
        couleur = resultat["couleur"]

        result_placeholder.empty()
        with result_placeholder.container():
            st.markdown(
                f"""
                <div class="ecosort-poubelle-outer">
                    <div class="ecosort-poubelle-anim">
                        <div class="ecosort-dechet"></div>
                        <svg viewBox="0 0 100 110" width="250" height="280">
                            <rect x="33" y="0" width="34" height="9" rx="2" fill="{couleur}" />
                            <rect x="17" y="9" width="66" height="14" rx="3" fill="{couleur}" />
                            <path d="M 22 26 L 30 102 Q 31 108 39 108 L 61 108 Q 69 108 70 102 L 78 26 Z"
                                  fill="{couleur}" opacity="0.9" />
                            <line x1="38" y1="38" x2="40" y2="98" stroke="white" stroke-opacity="0.25" stroke-width="2.5"/>
                            <line x1="50" y1="38" x2="50" y2="98" stroke="white" stroke-opacity="0.25" stroke-width="2.5"/>
                            <line x1="62" y1="38" x2="60" y2="98" stroke="white" stroke-opacity="0.25" stroke-width="2.5"/>
                        </svg>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div style="margin-top: 40px; font-weight: 600; font-size: 1.2rem; color: #F2F5F3; text-shadow: 0 2px 8px rgba(0,0,0,0.5);">{html.escape(produit.get("titre") or "Produit sans titre")}</div>',
                unsafe_allow_html=True,
            )

            if resultat["classe"]:
                detail = f"Détecté par le modèle : {resultat['classe']} (confiance {resultat['confiance']:.0%})"
            else:
                detail = "Détecté via la catégorie ou le nom du produit"

            st.markdown(
                f"""
                <div class="ecosort-resultat-poubelle" style="background-color:{couleur};">
                    <div class="ecosort-resultat-titre">♻️ Poubelle {resultat['poubelle']}</div>
                    <div class="ecosort-resultat-detail">{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown('</div>', unsafe_allow_html=True)
