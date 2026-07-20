"""API EcoSort-Search : classification d'images et recherche de produits."""

import io
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image
from tensorflow.keras.models import load_model

from app.cache import SimpleCache
from app.mapping import determiner_poubelle
from app.scraper import JumiaVerificationError, search_products

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "modele_eco_sort_finetuned.h5"

IMG_HEIGHT = 300
IMG_WIDTH = 300
CLASS_NAMES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]

app = FastAPI(title="EcoSort-Search API")
cache_recherche = SimpleCache(ttl_secondes=3600)  # 1 heure

# Chargement du modèle une seule fois, au démarrage du serveur
modele = None


@app.on_event("startup")
def charger_modele():
    global modele
    modele = load_model(MODEL_PATH)


@app.get("/")
def racine():
    """Vérification rapide que l'API tourne."""
    return {"message": "EcoSort-Search API opérationnelle"}


@app.post("/classify")
async def classify(file: UploadFile = File(...), titre_produit: str = "", categorie: str = ""):
    """Reçoit une image (et optionnellement le titre/categorie du produit), retourne la poubelle."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image.")

    resultat_preliminaire = determiner_poubelle(titre_produit, categorie=categorie)
    if resultat_preliminaire["poubelle"] == "D3E":
        return {
            "classe": None,
            "confiance": None,
            "poubelle": resultat_preliminaire["poubelle"],
            "couleur": resultat_preliminaire["couleur"],
            "methode": "categorie-ou-titre",
        }

    contenu = await file.read()
    image = Image.open(io.BytesIO(contenu)).convert("RGB")
    image = image.resize((IMG_WIDTH, IMG_HEIGHT))

    tableau_image = np.array(image)
    tableau_image = np.expand_dims(tableau_image, axis=0)

    predictions = modele.predict(tableau_image, verbose=0)
    index_predit = int(np.argmax(predictions[0]))
    classe_predite = CLASS_NAMES[index_predit]
    confiance = float(predictions[0][index_predit])

    resultat = determiner_poubelle(titre_produit, classe_modele=classe_predite, categorie=categorie)

    return {
        "classe": classe_predite,
        "confiance": round(confiance, 4),
        "poubelle": resultat["poubelle"],
        "couleur": resultat["couleur"],
        "methode": "modele-ia",
    }


@app.get("/search")
def search(q: str, max_results: int = 5):
    """Recherche des produits sur Jumia à partir d'un mot-clé (avec cache)."""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Le paramètre 'q' ne peut pas être vide.")

    cle_cache = f"{q.lower().strip()}:{max_results}"
    resultats_en_cache = cache_recherche.get(cle_cache)

    if resultats_en_cache is not None:
        return {"query": q, "resultats": resultats_en_cache, "source": "cache"}

    try:
        resultats = search_products(q, max_results=max_results)
    except JumiaVerificationError as erreur:
        raise HTTPException(status_code=503, detail=str(erreur))

    cache_recherche.set(cle_cache, resultats)

    return {"query": q, "resultats": resultats, "source": "scraping"}
