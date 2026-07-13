"""Scraper Jumia : recherche des produits à partir d'un mot-clé (via undetected-chromedriver)."""

import time

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://www.jumia.ci"


def creer_navigateur():
    """Configure et retourne une instance de Chrome indétectable par Cloudflare."""
    options = uc.ChromeOptions()
    # options.add_argument("--headless=new")  # décommenter pour un usage serveur (API)
    return uc.Chrome(options=options)


def extraire_produits_depuis_html(html: str, max_results: int = 5):
    """Analyse un HTML de page de résultats Jumia et retourne les produits trouvés.

    Fonction indépendante de Selenium : testable avec un HTML statique.
    """
    soup = BeautifulSoup(html, "html.parser")
    cartes_produits = soup.select("a.core")

    resultats = []
    for carte in cartes_produits[:max_results]:
        lien = carte.get("href", "")
        titre_element = carte.select_one("h3.name")
        prix_element = carte.select_one("div.prc")
        image_element = carte.select_one("img")

        produit = {
            "titre": titre_element.get_text(strip=True) if titre_element else None,
            "prix": prix_element.get_text(strip=True) if prix_element else None,
            "lien": (BASE_URL + lien) if lien and lien.startswith("/") else lien,
            "image": image_element.get("data-src") if image_element else None,
        }
        resultats.append(produit)

    return resultats


def search_products(query: str, max_results: int = 5):
    """Recherche des produits sur Jumia : récupère la page via Selenium, puis l'analyse."""
    navigateur = creer_navigateur()

    try:
        url = f"{BASE_URL}/catalog/?q={query}"
        navigateur.get(url)

        # Attendre que la page de vérification Cloudflare ("Un instant…") disparaisse
        try:
            WebDriverWait(navigateur, 20).until(
                lambda nav: nav.title != "Un instant…"
            )
        except Exception:
            pass

        time.sleep(2)

        html = navigateur.page_source
        return extraire_produits_depuis_html(html, max_results=max_results)
    finally:
        try:
            navigateur.quit()
        except OSError:
            pass


if __name__ == "__main__":
    import sys

    mot_cle = sys.argv[1] if len(sys.argv) > 1 else "bouteille d'eau"
    produits = search_products(mot_cle)

    for p in produits:
        print(f"{p['titre']} — {p['prix']}")
        print(f"  Lien : {p['lien']}")
        print()