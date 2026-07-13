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

COULEURS_UI = {
    "JAUNE": "#FFD700",
    "VERTE": "#228B22",
    "BLEUE": "#1E90FF",
    "D3E": "#808080",
    "MARRON": "#5C4033",
}


def detecter_electronique(titre_produit: str) -> bool:
    """Vérifie si un titre de produit correspond à un appareil électronique (D3E)."""
    titre_normalise = titre_produit.lower()
    return any(mot in titre_normalise for mot in MOTS_CLES_ELECTRONIQUE)


def classe_vers_poubelle(classe: str) -> str:
    """Traduit une classe du modèle (cardboard, glass...) vers une poubelle officielle."""
    return MAPPING_CLASSE_POUBELLE.get(classe, "MARRON")


def determiner_poubelle(titre_produit: str, classe_modele: str | None = None) -> dict:
    """Détermine la poubelle finale : priorité au titre (D3E), sinon la classe du modèle."""
    if detecter_electronique(titre_produit):
        poubelle = "D3E"
    elif classe_modele is not None:
        poubelle = classe_vers_poubelle(classe_modele)
    else:
        poubelle = "MARRON"

    return {
        "poubelle": poubelle,
        "couleur": COULEURS_UI[poubelle],
    }