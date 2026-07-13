"""Tests de la logique d'extraction du scraper Jumia (sans navigateur ni internet)."""

from app.scraper import extraire_produits_depuis_html

# Extrait de HTML représentatif d'une page de résultats Jumia (2 produits),
# basé sur la structure réelle observée sur le site.
HTML_EXEMPLE = """
<div class="row">
    <a class="core" href="/produit-test-un-12345.html">
        <div class="img-c">
            <img data-src="https://ci.jumia.is/image1.jpg" alt="Produit un">
        </div>
        <div class="info">
            <h3 class="name">Bouteille d'eau en inox 500ml</h3>
            <div class="prc">3,600 FCFA</div>
        </div>
    </a>
    <a class="core" href="/produit-test-deux-67890.html">
        <div class="img-c">
            <img data-src="https://ci.jumia.is/image2.jpg" alt="Produit deux">
        </div>
        <div class="info">
            <h3 class="name">Gourde pliable 750ml</h3>
            <div class="prc">2,150 FCFA</div>
        </div>
    </a>
</div>
"""


def test_extrait_le_bon_nombre_de_produits():
    resultats = extraire_produits_depuis_html(HTML_EXEMPLE, max_results=5)
    assert len(resultats) == 2


def test_extrait_le_titre_correctement():
    resultats = extraire_produits_depuis_html(HTML_EXEMPLE, max_results=5)
    assert resultats[0]["titre"] == "Bouteille d'eau en inox 500ml"


def test_extrait_le_prix_correctement():
    resultats = extraire_produits_depuis_html(HTML_EXEMPLE, max_results=5)
    assert resultats[0]["prix"] == "3,600 FCFA"


def test_construit_le_lien_complet():
    resultats = extraire_produits_depuis_html(HTML_EXEMPLE, max_results=5)
    assert resultats[0]["lien"] == "https://www.jumia.ci/produit-test-un-12345.html"


def test_respecte_la_limite_max_results():
    resultats = extraire_produits_depuis_html(HTML_EXEMPLE, max_results=1)
    assert len(resultats) == 1


def test_html_vide_retourne_liste_vide():
    resultats = extraire_produits_depuis_html("<div></div>", max_results=5)
    assert resultats == []