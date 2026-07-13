"""Cache simple en mémoire, avec expiration, pour éviter de rescraper Jumia inutilement."""

import time
from threading import Lock


class SimpleCache:
    """Cache clé/valeur en mémoire, avec durée de vie (TTL) par entrée."""

    def __init__(self, ttl_secondes: int = 3600):
        self._ttl = ttl_secondes
        self._donnees = {}
        self._verrou = Lock()

    def get(self, cle: str):
        """Retourne la valeur en cache si elle existe et n'a pas expiré, sinon None."""
        with self._verrou:
            entree = self._donnees.get(cle)
            if entree is None:
                return None

            valeur, horodatage = entree
            if time.time() - horodatage > self._ttl:
                del self._donnees[cle]
                return None

            return valeur

    def set(self, cle: str, valeur):
        """Enregistre une valeur en cache avec l'horodatage actuel."""
        with self._verrou:
            self._donnees[cle] = (valeur, time.time())

    def clear(self):
        """Vide entièrement le cache."""
        with self._verrou:
            self._donnees.clear()