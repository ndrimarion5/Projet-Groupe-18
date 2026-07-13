"""Mapping des classes du modèle vers les 5 poubelles officielles du brief."""

# Correspondance directe entre les classes du modèle et les poubelles
MAPPING_CLASSE_POUBELLE = {
    "cardboard": "JAUNE",
    "plastic": "JAUNE",
    "metal": "JAUNE",
    "glass": "VERTE",
    "paper": "BLEUE",
    "trash": "MARRON",
}

# Mots-clés indiquant un produit électronique (bac D3E),
# une catégorie absente du dataset d'entraînement du modèle
MOTS_CLES_ELECTRONIQUE = [
    "smartphone", "téléphone", "telephone", "chargeur", "écouteur",
    "ecouteur", "casque audio", "montre connectée", "montre connectee",
    "mixeur", "batterie", "power bank", "câble usb", "cable usb",
    "ordinateur", "tablette", "clavier", "souris", "enceinte",
    "télévision", "television", "réfrigérateur", "refrigerateur",
    "climatiseur", "ventilateur", "rasoir électrique", "rasoir electrique",
]

# Grandes catégories Jumia correspondant à des appareils électroniques
CATEGORIES_ELECTRONIQUE = [
    "phones & tablets",
    "computing",
    "electronics",
    "gaming",
    "home appliances",
    "cameras",
]

COULEURS_UI = {
    "JAUNE": "#FFD700",
    "VERTE": "#228B22",
    "BLEUE": "#1E90FF",
    "D3E": "#808080",
    "MARRON": "#5C4033",
}


def detecter_electronique_par_categorie(categorie: str) -> bool:
    """Vérifie si la catégorie officielle Jumia correspond à de l'électronique (plus fiable)."""
    categorie_normalisee = categorie.lower()
    return any(cat in categorie_normalisee for cat in CATEGORIES_ELECTRONIQUE)


def detecter_electronique_par_titre(titre_produit: str) -> bool:
    """Filet de sécurité : détection par mots-clés dans le titre, si pas de catégorie fiable."""
    titre_normalise = titre_produit.lower()
    return any(mot in titre_normalise for mot in MOTS_CLES_ELECTRONIQUE)

def classe_vers_poubelle(classe: str) -> str:
    """Traduit une classe du modèle (cardboard, glass...) vers une poubelle officielle."""
    return MAPPING_CLASSE_POUBELLE.get(classe, "MARRON")


def determiner_poubelle(titre_produit: str, classe_modele: str | None = None, categorie: str = "") -> dict:
    """Détermine la poubelle finale : priorité à la catégorie Jumia, puis au titre, puis au modèle."""
    if categorie and detecter_electronique_par_categorie(categorie):
        poubelle = "D3E"
    elif detecter_electronique_par_titre(titre_produit):
        poubelle = "D3E"
    elif classe_modele is not None:
        poubelle = classe_vers_poubelle(classe_modele)
    else:
        poubelle = "MARRON"

    return {
        "poubelle": poubelle,
        "couleur": COULEURS_UI[poubelle],
    }