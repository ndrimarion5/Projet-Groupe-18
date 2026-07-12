"""API EcoSort-Search : classification d'images et recherche de produits."""

from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image
from tensorflow.keras.models import load_model
import io

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "modele_eco_sort_finetuned.h5"

IMG_HEIGHT = 300
IMG_WIDTH = 300
CLASS_NAMES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]

app = FastAPI(title="EcoSort-Search API")

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
async def classify(file: UploadFile = File(...)):
    """Reçoit une image, retourne la classe de déchet prédite."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image.")

    contenu = await file.read()
    image = Image.open(io.BytesIO(contenu)).convert("RGB")
    image = image.resize((IMG_WIDTH, IMG_HEIGHT))

    tableau_image = np.array(image)
    tableau_image = np.expand_dims(tableau_image, axis=0)

    predictions = modele.predict(tableau_image, verbose=0)
    index_predit = int(np.argmax(predictions[0]))
    classe_predite = CLASS_NAMES[index_predit]
    confiance = float(predictions[0][index_predit])

    return {
        "classe": classe_predite,
        "confiance": round(confiance, 4),
    }