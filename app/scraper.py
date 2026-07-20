"""Scraper Jumia : recherche de produits via undetected-chromedriver."""

import subprocess
from urllib.parse import quote_plus

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://www.jumia.ci"


class JumiaVerificationError(Exception):
    """Levee quand Jumia affiche une verification humaine au lieu des resultats."""


def _version_chrome_installee():
    """Detecte la version majeure de Chrome installee sur Windows, si disponible."""
    try:
        sortie = subprocess.check_output(
            r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
            shell=True,
            text=True,
        )
        version_complete = sortie.strip().split()[-1]
        return int(version_complete.split(".")[0])
    except Exception:
        return None


def creer_navigateur():
    """Configure et retourne un navigateur Chrome rapide pour lire la page."""
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.page_load_strategy = "eager"
    options.add_experimental_option(
        "prefs",
        {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
        },
    )

    version_majeure = _version_chrome_installee()
    if version_majeure:
        navigateur = uc.Chrome(options=options, version_main=version_majeure)
    else:
        navigateur = uc.Chrome(options=options)
    navigateur.set_page_load_timeout(20)
    return navigateur


def extraire_produits_depuis_html(html: str, max_results: int = 5):
    """Analyse un HTML de resultats Jumia et retourne les produits trouves."""
    soup = BeautifulSoup(html, "html.parser")
    cartes_produits = soup.select("a.core")

    resultats = []
    for carte in cartes_produits[:max_results]:
        lien = carte.get("href", "")
        titre_element = carte.select_one("h3.name")
        prix_element = carte.select_one("div.prc")
        image_element = carte.select_one("img")
        image = None

        if image_element:
            image = (
                image_element.get("data-src")
                or image_element.get("src")
                or image_element.get("data-lazy-src")
            )
            if image and image.startswith("//"):
                image = f"https:{image}"
            elif image and image.startswith("/"):
                image = f"{BASE_URL}{image}"

        produit = {
            "titre": titre_element.get_text(strip=True) if titre_element else None,
            "prix": prix_element.get_text(strip=True) if prix_element else None,
            "lien": (BASE_URL + lien) if lien and lien.startswith("/") else lien,
            "image": image,
            "categorie": carte.get("data-ga4-item_category", ""),
        }
        resultats.append(produit)

    return resultats


def _fermer_popups(navigateur):
    """Ferme ou masque les popups qui peuvent recouvrir les produits."""
    from selenium.webdriver.common.keys import Keys

    try:
        navigateur.find_element("tag name", "body").send_keys(Keys.ESCAPE)
    except Exception:
        pass

    navigateur.execute_script(
        """
        document.querySelectorAll('*').forEach(function(el) {
            var style = window.getComputedStyle(el);
            var zIndex = parseInt(style.zIndex) || 0;
            if ((style.position === 'fixed' || style.position === 'sticky') && zIndex > 50) {
                el.style.display = 'none';
            }
        });
        """
    )


def _page_verification(navigateur) -> bool:
    """Indique si Jumia affiche une verification humaine."""
    titre = navigateur.title.lower()
    source = navigateur.page_source.lower()
    return (
        "un instant" in titre
        or "verification de securite" in source
        or "vérification de sécurité" in source
        or ("cloudflare" in source and "verify" in source)
    )


def search_products(query: str, max_results: int = 5):
    """Recherche des produits sur Jumia, puis analyse le HTML obtenu."""
    navigateur = creer_navigateur()

    try:
        url = f"{BASE_URL}/catalog/?q={quote_plus(query.strip())}"
        navigateur.get(url)

        try:
            WebDriverWait(navigateur, 12).until(
                lambda nav: _page_verification(nav)
                or len(nav.find_elements("css selector", "a.core")) > 0
            )
        except Exception:
            pass

        if _page_verification(navigateur):
            raise JumiaVerificationError(
                "Jumia demande une verification humaine (Cloudflare). Reessayez dans quelques instants."
            )

        _fermer_popups(navigateur)
        return extraire_produits_depuis_html(navigateur.page_source, max_results=max_results)
    finally:
        try:
            navigateur.quit()
        except OSError:
            pass


if __name__ == "__main__":
    import sys

    mot_cle = sys.argv[1] if len(sys.argv) > 1 else "bouteille d'eau"

    try:
        produits = search_products(mot_cle)
        for produit in produits:
            print(f"{produit['titre']} - {produit['prix']}")
            print(f"  Lien : {produit['lien']}")
            print()
    except JumiaVerificationError as erreur:
        print(f"Bloque par Cloudflare : {erreur}")
