"""Scraper Jumia : recherche des produits à partir d'un mot-clé (via undetected-chromedriver)."""

import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://www.jumia.ci"


def creer_navigateur():
    """Configure et retourne une instance de Chrome indétectable par Cloudflare."""
    options = uc.ChromeOptions()
    # options.add_argument("--headless=new")  # décommenter pour un usage serveur (API)
    return uc.Chrome(options=options)


def search_products(query: str, max_results: int = 5):
    """Recherche des produits sur Jumia et retourne une liste de dictionnaires."""
    navigateur = creer_navigateur()
    resultats = []

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

        cartes_produits = navigateur.find_elements(By.CSS_SELECTOR, "a.core")

        for carte in cartes_produits[:max_results]:
            lien = carte.get_attribute("href")

            try:
                titre = carte.find_element(By.CSS_SELECTOR, "h3.name").text
            except Exception:
                titre = None

            try:
                prix = carte.find_element(By.CSS_SELECTOR, "div.prc").text
            except Exception:
                prix = None

            try:
                image = carte.find_element(By.CSS_SELECTOR, "img").get_attribute("data-src")
            except Exception:
                image = None

            resultats.append({
                "titre": titre,
                "prix": prix,
                "lien": lien,
                "image": image,
            })
    finally:
        try:
            navigateur.quit()
        except OSError:
            pass

    return resultats


if __name__ == "__main__":
    import sys

    mot_cle = sys.argv[1] if len(sys.argv) > 1 else "bouteille d'eau"
    produits = search_products(mot_cle)

    for p in produits:
        print(f"{p['titre']} — {p['prix']}")
        print(f"  Lien : {p['lien']}")
        print()