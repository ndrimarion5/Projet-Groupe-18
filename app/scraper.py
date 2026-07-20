"""Scraper Jumia : recherche de produits via HTTP puis Selenium en secours."""

import os
import re
import shutil
import subprocess
from urllib.parse import quote_plus

import requests
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://www.jumia.ci"
PRODUCT_SELECTORS = "article.prd, a.core, [data-ga4-item_name]"
HEADERS_HTTP = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


class JumiaVerificationError(Exception):
    """Levee quand Jumia affiche une verification humaine au lieu des resultats."""


def _chemin_chrome_installe():
    """Retourne le chemin de Chrome/Chromium sur Windows, Linux ou Docker."""
    candidats = [
        os.getenv("CHROME_BIN"),
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]

    for chemin in candidats:
        if chemin and os.path.exists(chemin):
            return chemin

    return None


def _version_chrome_installee():
    """Detecte la version majeure de Chrome installee, si disponible."""
    chemin_chrome = _chemin_chrome_installe()
    if chemin_chrome:
        try:
            sortie = subprocess.check_output(
                [chemin_chrome, "--version"],
                text=True,
                stderr=subprocess.STDOUT,
            )
            version = re.search(r"(\d+)\.", sortie)
            if version:
                return int(version.group(1))
        except Exception:
            pass

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
    chemin_chrome = _chemin_chrome_installe()
    chemin_driver = os.getenv("CHROMEDRIVER_PATH")

    if chemin_chrome:
        options.binary_location = chemin_chrome

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

    arguments = {"options": options}
    version_majeure = _version_chrome_installee()
    if version_majeure:
        arguments["version_main"] = version_majeure
    if chemin_chrome:
        arguments["browser_executable_path"] = chemin_chrome
    if chemin_driver and os.path.exists(chemin_driver):
        arguments["driver_executable_path"] = chemin_driver

    navigateur = uc.Chrome(**arguments)
    navigateur.set_page_load_timeout(20)
    return navigateur


def _normaliser_url(url: str | None):
    """Transforme une URL relative Jumia en URL absolue."""
    if not url:
        return None
    if url.startswith("//"):
        return f"https:{url}"
    if url.startswith("/"):
        return f"{BASE_URL}{url}"
    return url


def _extraire_srcset(srcset: str | None):
    """Recupere la premiere URL d'un attribut srcset."""
    if not srcset:
        return None
    premiere_entree = srcset.split(",", 1)[0].strip()
    return premiere_entree.split(" ", 1)[0]


def _extraire_image(image_element):
    """Recupere l'URL d'image depuis les attributs les plus courants."""
    if not image_element:
        return None

    image = (
        image_element.get("data-src")
        or image_element.get("data-lazy-src")
        or image_element.get("src")
        or _extraire_srcset(image_element.get("data-srcset"))
        or _extraire_srcset(image_element.get("srcset"))
    )
    return _normaliser_url(image)


def _contient_verification(html: str) -> bool:
    """Indique si le HTML ressemble a une page Cloudflare."""
    contenu = html.lower()
    return (
        "verification de securite" in contenu
        or "vérification de sécurité" in contenu
        or ("cloudflare" in contenu and ("verify" in contenu or "checking" in contenu))
    )


def extraire_produits_depuis_html(html: str, max_results: int = 5):
    """Analyse un HTML de resultats Jumia et retourne les produits trouves."""
    soup = BeautifulSoup(html, "html.parser")
    cartes_produits = soup.select(PRODUCT_SELECTORS)

    resultats = []
    liens_vus = set()
    for carte in cartes_produits:
        lien_element = carte if carte.name == "a" else carte.select_one("a.core, a[href]")
        lien = _normaliser_url(lien_element.get("href", "") if lien_element else "")
        if not lien or lien in liens_vus:
            continue

        titre_element = carte.select_one("h3.name, .name, h3")
        prix_element = carte.select_one("div.prc, .prc, .price")
        image_element = carte.select_one("img")
        titre = (
            titre_element.get_text(strip=True)
            if titre_element
            else carte.get("data-ga4-item_name")
        )

        if not titre:
            continue

        produit = {
            "titre": titre,
            "prix": prix_element.get_text(strip=True) if prix_element else None,
            "lien": lien,
            "image": _extraire_image(image_element),
            "categorie": (
                carte.get("data-ga4-item_category")
                or (lien_element.get("data-ga4-item_category", "") if lien_element else "")
            ),
        }
        liens_vus.add(lien)
        resultats.append(produit)

        if len(resultats) >= max_results:
            break

    return resultats


def _search_products_http(query: str, max_results: int):
    """Tente une recuperation HTTP rapide avant de lancer Chrome."""
    url = f"{BASE_URL}/catalog/?q={quote_plus(query.strip())}"
    try:
        reponse = requests.get(url, headers=HEADERS_HTTP, timeout=20)
        reponse.raise_for_status()
    except requests.RequestException:
        return []

    if _contient_verification(reponse.text):
        return []

    return extraire_produits_depuis_html(reponse.text, max_results=max_results)


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
    return "un instant" in navigateur.title.lower() or _contient_verification(
        navigateur.page_source
    )


def search_products(query: str, max_results: int = 5):
    """Recherche des produits sur Jumia, puis analyse le HTML obtenu."""
    resultats_http = _search_products_http(query, max_results)
    if resultats_http:
        return resultats_http

    navigateur = creer_navigateur()

    try:
        url = f"{BASE_URL}/catalog/?q={quote_plus(query.strip())}"
        navigateur.get(url)

        try:
            WebDriverWait(navigateur, 12).until(
                lambda nav: _page_verification(nav)
                or len(nav.find_elements("css selector", PRODUCT_SELECTORS)) > 0
            )
        except Exception:
            pass

        if _page_verification(navigateur):
            raise JumiaVerificationError(
                "Jumia demande une verification humaine (Cloudflare). Reessayez dans quelques instants."
            )

        _fermer_popups(navigateur)
        navigateur.execute_script(
            "window.scrollTo(0, Math.min(document.body.scrollHeight, 1200));"
        )
        try:
            WebDriverWait(navigateur, 5).until(
                lambda nav: len(
                    extraire_produits_depuis_html(nav.page_source, max_results)
                )
                > 0
            )
        except Exception:
            pass

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
