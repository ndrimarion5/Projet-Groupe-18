"""EcoSort-Search : interface Streamlit pour la recherche et le tri de produits."""

import html
import time

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

# Duree minimale (secondes) d'affichage de la poubelle coloree avant de reveler
# la consigne : laisse le temps de voir l'objet tomber dedans, meme si l'API repond vite.
DUREE_MIN_ANIMATION_POUBELLE = 2.4

# Consignes citoyennes affichees selon la poubelle determinee par l'API.
# Le texte parle a l'utilisateur final, pas au developpeur.
CONSIGNES_POUBELLE = {
    "JAUNE": {
        "nom": "Bac jaune",
        "sous_titre": "Emballages recyclables",
        "consigne": "Videz et deposez l'emballage dans le bac jaune : plastiques, "
        "metaux et cartons d'emballage y sont recycles.",
    },
    "VERTE": {
        "nom": "Bac vert",
        "sous_titre": "Verre d'emballage",
        "consigne": "Deposez le verre (bouteilles, bocaux, pots) dans le bac vert. "
        "Retirez les bouchons et couvercles au prealable.",
    },
    "BLEUE": {
        "nom": "Bac bleu",
        "sous_titre": "Papiers et cartons",
        "consigne": "Deposez les papiers propres et secs dans le bac bleu : "
        "journaux, cahiers, livres et enveloppes.",
    },
    "D3E": {
        "nom": "Point de collecte D3E",
        "sous_titre": "Appareils electriques et electroniques",
        "consigne": "Cet appareil ne va pas a la poubelle. Rapportez-le dans un "
        "point de collecte D3E ou en magasin : il contient des composants a traiter.",
    },
    "MARRON": {
        "nom": "Bac a ordures menageres",
        "sous_titre": "Dechets non recyclables",
        "consigne": "Ce produit n'est pas recyclable en l'etat. Jetez-le dans le "
        "bac a ordures menageres classique.",
    },
}

# Version claire de la couleur de chaque poubelle, pour le texte sur fond colore.
TEXTE_SUR_COULEUR = {
    "JAUNE": "#1a1400",
    "VERTE": "#ffffff",
    "BLEUE": "#ffffff",
    "D3E": "#ffffff",
    "MARRON": "#ffffff",
}


def scene_poubelle_html(image_produit: str, couleur: str | None = None) -> str:
    """Construit le HTML de la poubelle animee, coloree selon la categorie une fois connue."""
    if image_produit:
        item_html = f'<img class="eco-bin-item" src="{html.escape(image_produit, quote=True)}" />'
    else:
        item_html = '<div class="eco-bin-item"></div>'

    style_attr = f' style="--bin-color: {html.escape(couleur, quote=True)};"' if couleur else ""

    scene = f"""<div class="eco-bin-scene"{style_attr}>
            <div class="eco-bin-shadow"></div>
            {item_html}
            <div class="eco-bin-lid-wrap">
                <div class="eco-bin-lid"></div>
            </div>
            <div class="eco-bin-body">
                <div class="eco-bin-rib"></div>
                <div class="eco-bin-rib"></div>
                <div class="eco-bin-rib"></div>
            </div>
        </div>"""
    # .strip() : une ligne vide (espaces avant le """) coupe le bloc HTML englobant
    # en plein milieu quand cette chaine est inseree dans un autre st.markdown().
    return scene.strip()


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


st.set_page_config(page_title="EcoSort-Search", page_icon="\u267b\ufe0f", layout="wide")

# --- STYLE : sobre, sombre, centre sur le geste de tri ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

        /* Fond uni vert profond, sans images externes ni animations distrayantes */
        html, body, .stApp,
        [data-testid="stAppViewContainer"], [data-testid="stMain"],
        [data-testid="stHeader"] {
            background: #0d1f17 !important;
        }
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(1200px 600px at 50% -10%, #16352600 0%, transparent 60%),
                linear-gradient(180deg, #10281d 0%, #0d1f17 55%, #0a1811 100%) !important;
        }

        /* Masque le menu et le bandeau par defaut de Streamlit pour un rendu fini */
        #MainMenu, header [data-testid="stToolbar"], footer {
            visibility: hidden;
        }
        [data-testid="stHeader"] { height: 0; }

        .stApp, .stApp * {
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .block-container {
            max-width: 1080px;
            padding-top: 2.5rem;
            padding-bottom: 4rem;
        }

        /* ----- EN-TETE ----- */
        .eco-header {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        .eco-eyebrow {
            display: inline-block;
            color: #6fcf97;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            margin-bottom: 0.9rem;
        }
        .eco-title {
            font-size: 3.1rem;
            font-weight: 800;
            color: #f4f9f6;
            margin: 0;
            letter-spacing: -0.02em;
            line-height: 1.05;
        }
        .eco-title .accent { color: #6fcf97; }
        .eco-subtitle {
            color: #9fb8ac;
            font-size: 1.1rem;
            font-weight: 400;
            margin-top: 0.75rem;
        }

        /* ----- RECHERCHE ----- */
        .stTextInput > div > div > input {
            border-radius: 12px !important;
            background: #12291e !important;
            border: 1px solid #24463500 !important;
            border: 1px solid #234634 !important;
            color: #f4f9f6 !important;
            font-size: 1.05rem !important;
            height: 54px !important;
            padding-left: 18px !important;
        }
        .stTextInput > div > div > input::placeholder {
            color: #6d8579 !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #6fcf97 !important;
            box-shadow: 0 0 0 3px rgba(111, 207, 151, 0.15) !important;
        }

        div[data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
        }
        div[data-testid="stForm"] .stButton > button {
            background: #6fcf97 !important;
            color: #08130d !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.8rem 2rem !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            width: 100% !important;
            transition: background 0.2s ease, transform 0.2s ease !important;
        }
        div[data-testid="stForm"] .stButton > button:hover {
            background: #5bbf85 !important;
            transform: translateY(-1px) !important;
        }

        /* ----- CARTES PRODUITS ----- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #12291e !important;
            border: 1px solid #1f3d2d !important;
            border-radius: 16px !important;
            overflow: hidden;
            transition: border-color 0.2s ease, transform 0.2s ease;
            margin-bottom: 1.25rem;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #3f6b52 !important;
            transform: translateY(-3px);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div { padding: 0 !important; }

        .eco-card-image {
            width: 100%;
            aspect-ratio: 1 / 1;
            background: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }
        .eco-card-image img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        .eco-card-body { padding: 16px 18px 6px 18px; }
        .eco-card-title {
            color: #eaf3ee;
            font-weight: 600;
            font-size: 1rem;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 2.8em;
            margin-bottom: 8px;
        }
        .eco-card-price {
            color: #f5b342;
            font-weight: 700;
            font-size: 1.35rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] div.stButton > button {
            background: transparent !important;
            color: #6fcf97 !important;
            border: 1px solid #3f6b52 !important;
            border-radius: 10px !important;
            padding: 0.6rem !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            margin: 0 18px 18px 18px !important;
            width: calc(100% - 36px) !important;
            transition: background 0.2s ease, color 0.2s ease !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] div.stButton > button:hover {
            background: #6fcf97 !important;
            color: #08130d !important;
        }

        /* ----- LIEN "VOIR SUR JUMIA" (independant du tri) ----- */
        .eco-jumia-link {
            display: block;
            text-align: center;
            text-decoration: none;
            color: #f68b1e !important;
            border: 1px solid #f68b1e;
            border-radius: 10px;
            padding: 0.55rem;
            font-size: 0.9rem;
            font-weight: 600;
            margin: 0 18px 18px 18px;
            transition: background 0.2s ease, color 0.2s ease;
        }
        .eco-jumia-link:hover {
            background: #f68b1e;
            color: #08130d !important;
        }

        /* ----- SECTION PRODUIT CHOISI ----- */
        .eco-section-label {
            color: #6fcf97;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin: 2.5rem 0 1rem 0;
        }
        .eco-selected-title { color: #f4f9f6; font-size: 1.3rem; font-weight: 700; }
        .eco-selected-price { color: #f5b342; font-size: 1.1rem; font-weight: 600; margin-top: 4px; }

        /* ----- RESULTAT DE TRI ----- */
        .eco-result {
            border-radius: 16px;
            padding: 2rem 2rem;
            margin-top: 1.25rem;
        }
        .eco-result-badge {
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 999px;
            background: rgba(0,0,0,0.18);
            margin-bottom: 0.9rem;
        }
        .eco-result-title { font-size: 2rem; font-weight: 800; margin: 0; line-height: 1.1; }
        .eco-result-subtitle { font-size: 1rem; font-weight: 600; opacity: 0.85; margin-top: 2px; }
        .eco-result-consigne { font-size: 1.05rem; line-height: 1.5; margin-top: 1rem; opacity: 0.95; }
        .eco-result-meta {
            font-size: 0.8rem;
            margin-top: 1.25rem;
            opacity: 0.6;
        }

        .eco-waiting {
            color: #9fb8ac;
            text-align: center;
            padding: 2rem;
            background: #12291e;
            border: 1px solid #1f3d2d;
            border-radius: 16px;
            margin-top: 1.25rem;
        }

        /* ----- POUBELLE ANIMEE (analyse en cours) ----- */
        .eco-bin-waiting {
            text-align: center;
            padding: 2.5rem 2rem 2rem 2rem;
            background: #12291e;
            border: 1px solid #1f3d2d;
            border-radius: 16px;
            margin-top: 1.25rem;
        }
        .eco-bin-scene {
            position: relative;
            width: 150px;
            height: 150px;
            margin: 0 auto 1.25rem auto;
        }
        .eco-bin-shadow {
            position: absolute;
            bottom: 4px;
            left: 50%;
            transform: translateX(-50%);
            width: 90px;
            height: 14px;
            background: radial-gradient(ellipse at center, rgba(0,0,0,0.45) 0%, transparent 70%);
            border-radius: 50%;
        }
        .eco-bin-scene { --bin-color: #3f6b52; }
        .eco-bin-body {
            position: absolute;
            bottom: 14px;
            left: 50%;
            transform: translateX(-50%);
            width: 92px;
            height: 96px;
            background: var(--bin-color);
            clip-path: polygon(12% 0%, 88% 0%, 80% 100%, 20% 100%);
            box-shadow: inset -8px 0 14px rgba(0,0,0,0.3), inset 8px 0 14px rgba(255,255,255,0.12);
            transition: background 0.3s ease;
            z-index: 1;
        }
        .eco-bin-rib {
            position: absolute;
            top: 14px;
            bottom: 10px;
            width: 2px;
            background: rgba(0,0,0,0.2);
        }
        .eco-bin-rib:nth-child(1) { left: 30%; }
        .eco-bin-rib:nth-child(2) { left: 50%; }
        .eco-bin-rib:nth-child(3) { left: 70%; }
        .eco-bin-lid-wrap {
            position: absolute;
            top: 40px;
            left: 50%;
            transform: translateX(-50%);
            width: 104px;
            height: 18px;
            perspective: 220px;
            z-index: 3;
        }
        .eco-bin-lid {
            position: relative;
            width: 100%;
            height: 100%;
            background: var(--bin-color);
            filter: brightness(1.25);
            border-radius: 8px 8px 3px 3px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.35);
            transform-origin: 50% 100%;
            transition: background 0.3s ease;
            animation: eco-bin-lid-open 2.2s ease-in-out infinite;
        }
        .eco-bin-lid::after {
            content: "";
            position: absolute;
            top: 4px;
            left: 50%;
            transform: translateX(-50%);
            width: 22px;
            height: 5px;
            background: rgba(8, 19, 13, 0.4);
            border-radius: 3px;
        }
        .eco-bin-item {
            position: absolute;
            top: 6px;
            left: 50%;
            width: 44px;
            height: 44px;
            margin-left: -22px;
            object-fit: contain;
            background: #ffffff;
            border-radius: 8px;
            padding: 4px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.35);
            z-index: 2;
            animation: eco-bin-item-fall 2.2s ease-in infinite;
        }
        .eco-waiting-text {
            color: #9fb8ac;
            font-size: 1rem;
        }
        @keyframes eco-bin-lid-open {
            0%, 28% { transform: rotateX(0deg); }
            42%, 60% { transform: rotateX(-68deg); }
            78%, 100% { transform: rotateX(0deg); }
        }
        @keyframes eco-bin-item-fall {
            0% { transform: translateY(-46px) scale(1); opacity: 0; }
            12% { opacity: 1; }
            38% { transform: translateY(2px) scale(1); opacity: 1; }
            52% { transform: translateY(30px) scale(0.55); opacity: 1; }
            68% { transform: translateY(42px) scale(0.15); opacity: 0; }
            100% { transform: translateY(42px) scale(0.15); opacity: 0; }
        }

        hr { border-color: #1f3d2d !important; }

        @media (max-width: 768px) {
            .eco-title { font-size: 2.2rem; }
            .block-container { padding-top: 1.5rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- EN-TETE ---
st.markdown(
    """
    <div class="eco-header">
        <span class="eco-eyebrow">&#9851; Tri selectif assiste</span>
        <h1 class="eco-title">EcoSort<span class="accent">-Search</span></h1>
        <p class="eco-subtitle">Cherchez un produit, choisissez-le, obtenez sa consigne de tri.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- BARRE DE RECHERCHE ---
with st.form("formulaire_recherche", border=False):
    col_champ, col_bouton = st.columns([4, 1])
    with col_champ:
        mot_cle = st.text_input(
            "Recherche",
            placeholder="Ex. : bouteille, cahier, chargeur, montre...",
            label_visibility="collapsed",
        )
    with col_bouton:
        lancer_recherche = st.form_submit_button("Rechercher")

# --- LOGIQUE DE RECHERCHE ---
if lancer_recherche and mot_cle.strip():
    try:
        with st.spinner("Recherche en cours..."):
            statut_recherche, donnees_recherche = rechercher_produits_api(
                mot_cle.strip(), max_results=6
            )
    except requests.exceptions.ConnectionError:
        st.error(
            "Le service de recherche est momentanement indisponible. "
            "Reessayez dans un instant."
        )
        st.stop()
    except requests.exceptions.Timeout:
        st.error("La recherche prend trop de temps. Reessayez dans un instant.")
        st.stop()

    if statut_recherche == 200:
        st.session_state["produits"] = donnees_recherche.get("resultats", [])
        st.session_state["source_recherche"] = donnees_recherche.get("source", "inconnue")
        st.session_state.pop("produit_choisi", None)
        st.session_state.pop("resultat_classification", None)
        st.session_state.pop("show_waiting", None)
    elif statut_recherche == 503:
        st.warning(
            "Jumia demande une verification de securite. "
            "Patientez quelques instants puis relancez la recherche."
        )
    else:
        st.error(f"La recherche a echoue (code {statut_recherche}). Reessayez.")

# --- SECTION : PRODUIT CHOISI + RESULTAT ---
# Placee juste sous la barre de recherche (et avant la grille de resultats) pour
# rester visible sans avoir a faire defiler la page une fois un produit choisi.
if "produit_choisi" in st.session_state:
    produit = st.session_state["produit_choisi"]

    st.markdown('<div class="eco-section-label">Produit selectionne</div>', unsafe_allow_html=True)
    col_img, col_info = st.columns([1, 3])
    with col_img:
        if produit.get("image"):
            st.image(produit["image"], width=140)
    with col_info:
        st.markdown(
            f'<div class="eco-selected-title">'
            f'{html.escape(produit.get("titre") or "Produit sans titre")}</div>'
            f'<div class="eco-selected-price">'
            f'{html.escape(produit.get("prix") or "Prix indisponible")}</div>',
            unsafe_allow_html=True,
        )

    result_placeholder = st.empty()
    image_produit = produit.get("image") or ""

    if st.session_state.get("show_waiting", False):
        result_placeholder.markdown(
            f"""
            <div class="eco-bin-waiting">
                {scene_poubelle_html(image_produit)}
                <div class="eco-waiting-text">Analyse du produit en cours...</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if "resultat_classification" not in st.session_state:
        if not produit.get("image"):
            st.error("Aucune image disponible pour ce produit, impossible de l'analyser.")
        else:
            try:
                statut_classification, donnees_classification = classifier_produit(
                    produit.get("titre") or "",
                    produit.get("categorie", ""),
                    produit["image"],
                )
            except requests.exceptions.ConnectionError:
                st.error(
                    "Le service d'analyse est momentanement indisponible. "
                    "Reessayez dans un instant."
                )
                st.stop()
            except requests.exceptions.Timeout:
                st.error("L'analyse prend trop de temps. Reessayez dans un instant.")
                st.stop()
            except requests.exceptions.RequestException as erreur:
                st.error(f"Impossible de recuperer l'image du produit : {erreur}")
                st.stop()

            if statut_classification == 200:
                # On connait desormais la couleur de la bonne poubelle : on rejoue
                # l'animation avec cette couleur et on la maintient un instant avant
                # de reveler la consigne, meme si l'API a repondu tres vite.
                couleur_trouvee = donnees_classification["couleur"]
                result_placeholder.markdown(
                    f"""
                    <div class="eco-bin-waiting">
                        {scene_poubelle_html(image_produit, couleur_trouvee)}
                        <div class="eco-waiting-text">Tri en cours...</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                time.sleep(DUREE_MIN_ANIMATION_POUBELLE)
                st.session_state["resultat_classification"] = donnees_classification
                st.session_state["show_waiting"] = False
                st.rerun()
            else:
                st.error(
                    f"L'analyse a echoue (code {statut_classification}). Reessayez."
                )
                st.session_state["show_waiting"] = False

    if "resultat_classification" in st.session_state:
        resultat = st.session_state["resultat_classification"]
        couleur = resultat["couleur"]
        poubelle = resultat["poubelle"]

        infos = CONSIGNES_POUBELLE.get(
            poubelle,
            {
                "nom": f"Poubelle {poubelle}",
                "sous_titre": "",
                "consigne": "",
            },
        )
        texte_couleur = TEXTE_SUR_COULEUR.get(poubelle, "#ffffff")

        # Ligne technique discrete : utile a l'evaluation, secondaire pour l'usager.
        if resultat.get("classe"):
            meta = (
                f"Analyse : matiere &laquo; {html.escape(str(resultat['classe']))} &raquo; "
                f"reconnue par le modele (confiance {resultat['confiance']:.0%})."
            )
        else:
            meta = "Analyse : categorie determinee a partir du type de produit."

        result_placeholder.empty()
        with result_placeholder.container():
            st.markdown(
                f"""
                <div class="eco-result" style="background:{couleur}; color:{texte_couleur};">
                    <span class="eco-result-badge">Consigne de tri</span>
                    <h2 class="eco-result-title">{html.escape(infos['nom'])}</h2>
                    <div class="eco-result-subtitle">{html.escape(infos['sous_titre'])}</div>
                    <div class="eco-result-consigne">{html.escape(infos['consigne'])}</div>
                    <div class="eco-result-meta">{meta}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<hr>", unsafe_allow_html=True)

# --- AFFICHAGE DES PRODUITS ---
if "produits" in st.session_state:
    produits = st.session_state["produits"]
    nb_colonnes = 3

    if not produits:
        st.info(
            "Aucun produit trouve pour cette recherche. "
            "Essayez un mot-cle plus simple, comme bouteille, calculatrice ou cahier."
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
                            f'<div class="eco-card-image">'
                            f'<img loading="lazy" '
                            f'src="{html.escape(produit["image"], quote=True)}"></div>',
                            unsafe_allow_html=True,
                        )

                    titre = html.escape(produit.get("titre") or "Produit sans titre")
                    prix = html.escape(produit.get("prix") or "Prix indisponible")
                    st.markdown(
                        f"""
                        <div class="eco-card-body">
                            <div class="eco-card-title">{titre}</div>
                            <div class="eco-card-price">{prix}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if st.button("Choisir ce produit", key=f"choisir_{index}", width="stretch"):
                        st.session_state["produit_choisi"] = produit
                        st.session_state.pop("resultat_classification", None)
                        st.session_state["show_waiting"] = True
                        st.rerun()

                    lien_produit = produit.get("lien")
                    if lien_produit:
                        st.markdown(
                            f'<a class="eco-jumia-link" '
                            f'href="{html.escape(lien_produit, quote=True)}" '
                            f'target="_blank" rel="noopener noreferrer">'
                            f'Voir sur Jumia &#8599;</a>',
                            unsafe_allow_html=True,
                        )