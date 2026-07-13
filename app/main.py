"""EcoSort-Search : interface Streamlit pour la recherche et le tri de produits."""

import requests
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
        .ecosort-carte {
            background-color: #16241F;
            border: 1px solid #23342C;
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 18px;
        }
        .ecosort-carte img {
            border-radius: 8px;
        }
        .ecosort-carte-titre {
            font-weight: 600;
            font-size: 1rem;
            line-height: 1.3;
        }
        .ecosort-carte-prix {
            color: #5FBF8F;
            font-weight: 700;
            margin-top: 4px;
        }
        div.stButton > button {
            background-color: #1B5E43;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: 600;
        }
        div.stButton > button:hover {
            background-color: #24805A;
            color: white;
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
    else:
        st.error(f"Erreur lors de la recherche (code {reponse.status_code})")

# --- Liste des produits ---
if "produits" in st.session_state:
    for index, produit in enumerate(st.session_state["produits"]):
        col_carte, col_bouton = st.columns([5, 1])

        with col_carte:
            st.markdown(
                f"""
                <div class="ecosort-carte">
                    <img src="{produit['image']}" width="70" height="70">
                    <div>
                        <div class="ecosort-carte-titre">{produit['titre']}</div>
                        <div class="ecosort-carte-prix">{produit['prix']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_bouton:
            if st.button("Choisir", key=f"choisir_{index}"):
                st.session_state["produit_choisi"] = produit
                st.session_state["compteur_animation"] = st.session_state.get("compteur_animation", 0) + 1
                st.session_state.pop("resultat_classification", None)

# --- Classification du produit choisi ---
if "produit_choisi" in st.session_state:
    produit = st.session_state["produit_choisi"]

    if "resultat_classification" not in st.session_state:
        with st.spinner("Analyse en cours..."):
            image_reponse = requests.get(produit["image"])
            fichiers = {"file": ("produit.jpg", image_reponse.content, "image/jpeg")}
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

        # Animation : poubelle en haut à droite, objet qui y tombe
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