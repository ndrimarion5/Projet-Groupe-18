"""EcoSort-Search : interface Streamlit pour la recherche et le tri de produits."""

import requests
import base64
import streamlit as st

API_URL = "http://127.0.0.1:8000"



st.set_page_config(page_title="EcoSort-Search", layout="centered")



# --- Styles globaux ---
st.markdown(
    """
    <style>
        .ecosort-titre {
            font-size: 2.4rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 0;
        }
        .ecosort-soustitre {
            color: #9BB0A8;
            font-size: 1.05rem;
            margin-bottom: 2rem;
        }

        /* --- Cards produits, style "fiche Jumia" --- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF;
            border-radius: 6px;
            border: 1px solid rgba(0,0,0,0.08);
            overflow: hidden;
            transition: box-shadow 0.15s ease, transform 0.15s ease;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            box-shadow: 0 6px 18px rgba(0,0,0,0.25);
            transform: translateY(-2px);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 0 !important;
        }
        .ecosort-carte-image-wrap {
            width: 100%;
            aspect-ratio: 1 / 1;
            background: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px;
        }
        .ecosort-carte-image {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        .ecosort-carte-corps {
            padding: 12px 14px 16px 14px;
        }
        .ecosort-carte-titre {
            color: #2B2B2B;
            font-weight: 400;
            font-size: 0.88rem;
            line-height: 1.35;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 2.4em;
            margin-bottom: 6px;
        }
        .ecosort-carte-prix {
            color: #F68B1E;
            font-weight: 800;
            font-size: 1.05rem;
        }

        div.stButton > button {
            background-color: #1B5E43;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 20px;
            font-weight: 600;
            width: 100%;
            margin: 0 14px 14px 14px !important;
        }
        div.stButton > button:hover {
            background-color: #24805A;
            color: white;
        }
        div[data-testid="column"] div.stButton {
            padding: 0 14px 14px 14px;
        }

        .ecosort-resultat-poubelle {
            padding: 40px;
            border-radius: 16px;
            text-align: center;
            margin-top: 10px;
        }
        .ecosort-resultat-titre {
            font-size: 1.6rem;
            font-weight: 800;
            color: white;
        }
        .ecosort-resultat-detail {
            color: rgba(255,255,255,0.85);
            margin-top: 6px;
            font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="ecosort-titre">EcoSort-Search</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ecosort-soustitre">Cherchez un produit, on vous montre sa poubelle.</div>',
    unsafe_allow_html=True,
)

mot_cle = st.text_input("Nom du produit", placeholder="ex: bouteille d'eau", label_visibility="collapsed")
lancer_recherche = st.button("Rechercher")

if lancer_recherche and mot_cle.strip():
    with st.spinner("Recherche en cours..."):
        reponse = requests.get(f"{API_URL}/search", params={"q": mot_cle, "max_results": 5})

    if reponse.status_code == 200:
        st.session_state["produits"] = reponse.json()["resultats"]
        st.session_state.pop("produit_choisi", None)
        st.session_state.pop("resultat_classification", None)
    elif reponse.status_code == 503:
        st.warning(
            "Jumia demande une vérification de sécurité en ce moment. "
            "Attendez quelques instants puis réessayez."
        )
    else:
        st.error(f"Erreur lors de la recherche (code {reponse.status_code})")

# --- Grille des produits, style fiche produit ---
if "produits" in st.session_state:
    produits = st.session_state["produits"]
    nb_colonnes = 3

    for debut in range(0, len(produits), nb_colonnes):
        colonnes = st.columns(nb_colonnes)

        for decalage, colonne in enumerate(colonnes):
            index = debut + decalage
            if index >= len(produits):
                continue

            produit = produits[index]

            with colonne:
                with st.container(border=True):
                    if produit.get("image_base64"):
                        st.markdown(
                            f'<div class="ecosort-carte-image-wrap">'
                            f'<img class="ecosort-carte-image" '
                            f'src="data:image/jpeg;base64,{produit["image_base64"]}"></div>',
                            unsafe_allow_html=True,
                        )

                    st.markdown(
                        f"""
                        <div class="ecosort-carte-corps">
                            <div class="ecosort-carte-titre">{produit["titre"]}</div>
                            <div class="ecosort-carte-prix">{produit["prix"]}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if st.button("Choisir", key=f"choisir_{index}", use_container_width=True):
                        st.session_state["produit_choisi"] = produit
                        st.session_state["compteur_animation"] = st.session_state.get("compteur_animation", 0) + 1
                        st.session_state.pop("resultat_classification", None)

# --- Classification du produit choisi ---
if "produit_choisi" in st.session_state:
    produit = st.session_state["produit_choisi"]

    if "resultat_classification" not in st.session_state:
        with st.spinner("Analyse en cours..."):
            if not produit.get("image_base64"):
                st.error("Aucune image disponible pour ce produit.")
                st.stop()

            octets_image = base64.b64decode(produit["image_base64"])
            fichiers = {"file": ("produit.jpg", octets_image, "image/jpeg")}
            parametres = {
                "titre_produit": produit["titre"],
                "categorie": produit.get("categorie", ""),
            }
            resultat_reponse = requests.post(f"{API_URL}/classify", files=fichiers, params=parametres)

        if resultat_reponse.status_code == 200:
            st.session_state["resultat_classification"] = resultat_reponse.json()
        else:
            st.error(f"Erreur lors de la classification (code {resultat_reponse.status_code})")

    if "resultat_classification" in st.session_state:
        resultat = st.session_state["resultat_classification"]
        couleur = resultat["couleur"]
        compteur = st.session_state.get("compteur_animation", 0)

        st.markdown(
            f"""
            <style>
            @keyframes apparitionPoubelle_{compteur} {{
                from {{ transform: scale(0); opacity: 0; }}
                to {{ transform: scale(1); opacity: 1; }}
            }}
            @keyframes tomberDedans_{compteur} {{
                0% {{ transform: translate(-50%, -120px) rotate(0deg); opacity: 1; }}
                65% {{ transform: translate(-50%, 38px) rotate(200deg); opacity: 1; }}
                100% {{ transform: translate(-50%, 50px) rotate(200deg); opacity: 0; }}
            }}
            .ecosort-poubelle-container-{compteur} {{
                position: fixed;
                top: 20px;
                right: 24px;
                width: 84px;
                height: 96px;
                z-index: 9999;
                animation: apparitionPoubelle_{compteur} 0.35s ease-out;
            }}
            .ecosort-dechet-{compteur} {{
                position: absolute;
                top: 0;
                left: 50%;
                width: 20px;
                height: 20px;
                background: #F2F5F3;
                border-radius: 5px;
                animation: tomberDedans_{compteur} 0.9s ease-in forwards;
                animation-delay: 0.25s;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            }}
            </style>
            <div class="ecosort-poubelle-container-{compteur}">
                <div class="ecosort-dechet-{compteur}"></div>
                <svg viewBox="0 0 100 110" width="84" height="96">
                    <rect x="35" y="0" width="30" height="8" rx="2" fill="{couleur}" />
                    <rect x="20" y="8" width="60" height="12" rx="3" fill="{couleur}" />
                    <path d="M 25 24 L 32 100 Q 33 106 40 106 L 60 106 Q 67 106 68 100 L 75 24 Z"
                          fill="{couleur}" opacity="0.88" />
                    <line x1="40" y1="35" x2="42" y2="95" stroke="white" stroke-opacity="0.25" stroke-width="2"/>
                    <line x1="50" y1="35" x2="50" y2="95" stroke="white" stroke-opacity="0.25" stroke-width="2"/>
                    <line x1="60" y1="35" x2="58" y2="95" stroke="white" stroke-opacity="0.25" stroke-width="2"/>
                </svg>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(f'<div style="margin-top: 30px; font-weight: 600;">{produit["titre"]}</div>', unsafe_allow_html=True)

        if resultat["classe"]:
            detail = f"Détecté par le modèle : {resultat['classe']} (confiance {resultat['confiance']:.0%})"
        else:
            detail = "Détecté via la catégorie ou le nom du produit"

        st.markdown(
            f"""
            <div class="ecosort-resultat-poubelle" style="background-color:{couleur};">
                <div class="ecosort-resultat-titre">Poubelle {resultat['poubelle']}</div>
                <div class="ecosort-resultat-detail">{detail}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )