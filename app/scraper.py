"""Scraper Jumia : recherche des produits à partir d'un mot-clé (via undetected-chromedriver)."""

import base64
import time
import subprocess

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://www.jumia.ci"


class JumiaVerificationError(Exception):
    """Levée quand Jumia affiche une page de vérification humaine (Cloudflare) au lieu des résultats."""




def _version_chrome_installee():
    """Détecte la version majeure de Chrome installée sur la machine (Windows)."""
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
    """Configure et retourne une instance de Chrome indétectable par Cloudflare."""
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")

    version_majeure = _version_chrome_installee()
    return uc.Chrome(options=options, version_main=version_majeure)

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
            "categorie": carte.get("data-ga4-item_category", ""),
        }
        resultats.append(produit)

    return resultats


def _attendre_image_chargee(navigateur, image_element, delai_max: int = 5) -> bool:
    """Attend que l'image soit réellement chargée dans le navigateur (pas juste le placeholder)."""
    try:
        WebDriverWait(navigateur, delai_max).until(
            lambda nav: nav.execute_script(
                "return arguments[0].complete && arguments[0].naturalWidth > 10;",
                image_element,
            )
        )
        return True
    except Exception:
        return False

def _fermer_popups(navigateur):
    """Ferme ou masque les popups (cookies, newsletter, promos) qui recouvrent les produits."""
    from selenium.webdriver.common.keys import Keys

    # Tentative : Echap ferme souvent une modale standard
    try:
        navigateur.find_element("tag name", "body").send_keys(Keys.ESCAPE)
    except Exception:
        pass

    # Filet de sécurité générique : masque tout élément flottant à l'écran
    # (bandeaux cookies, popups newsletter, promos) qui pourrait recouvrir les produits
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
    time.sleep(0.3)

def search_products(query: str, max_results: int = 5):
    """Recherche des produits sur Jumia : récupère la page via Selenium, puis l'analyse.

    Lève JumiaVerificationError si Cloudflare bloque avec une page de vérification humaine.
    """
    navigateur = creer_navigateur()

    try:
        url = f"{BASE_URL}/catalog/?q={query}"
        navigateur.get(url)

        try:
            WebDriverWait(navigateur, 20).until(
                lambda nav: nav.title != "Un instant…"
            )
        except Exception:
            pass

        time.sleep(2)

        # Détection explicite : Cloudflare a-t-il bloqué avec une vérification humaine ?
        if navigateur.title == "Un instant…" or "Vérification de sécurité" in navigateur.page_source:
            raise JumiaVerificationError(
                "Jumia demande une vérification humaine (Cloudflare). Réessayez dans quelques instants."
            )

        if navigateur.title == "Un instant…" or "Vérification de sécurité" in navigateur.page_source:
            raise JumiaVerificationError(
                "Jumia demande une vérification humaine (Cloudflare). Réessayez dans quelques instants."
            )

        _fermer_popups(navigateur)


        html = navigateur.page_source
        resultats = extraire_produits_depuis_html(html, max_results=max_results)

        # Capture des images directement depuis le navigateur, après chargement réel
        cartes_live = navigateur.find_elements("css selector", "a.core")[:max_results]
        for produit, carte in zip(resultats, cartes_live):
            try:
                image_element = carte.find_element("css selector", "img")
                navigateur.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", image_element
                )
                _attendre_image_chargee(navigateur, image_element)
                image_png = image_element.screenshot_as_png
                produit["image_base64"] = base64.b64encode(image_png).decode("utf-8")
            except Exception:
                produit["image_base64"] = None

        return resultats
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
        for p in produits:
            print(f"{p['titre']} — {p['prix']}")
            print(f"  Lien : {p['lien']}")
            print()
    except JumiaVerificationError as erreur:
        print(f"Bloqué par Cloudflare : {erreur}")