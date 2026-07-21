# ♻️ EcoSort-Search

Application web d'aide au tri sélectif : l'utilisateur recherche un produit, l'application interroge Jumia en direct, puis une IA de Deep Learning (entrainé ou adapté par nous même et basé sur du transfert learning EfficientNetB3) détermine la poubelle exacte à utiliser, avec un retour visuel coloré et une consigne de tri claire.

Projet réalisé dans le cadre du module de Machine Learning 2 des élève en ISE 2B à l'ENSEA Abidjan, année 2025/2026

##Nom des particpants :
1- N'DRI N'guessan Marion
2- SAWADOGO Souleymane
3- YABRE Jacques

---

## Sommaire

- [Fonctionnement général](#fonctionnement-général)
- [Catégories de tri](#catégories-de-tri)
- [Architecture technique](#architecture-technique)
- [Lancer le projet avec Docker](#lancer-le-projet-avec-docker)
- [Répartition du travail](#répartition-du-travail)
- [Limites connues](#limites-connues)

---

## Fonctionnement général

1. L'utilisateur tape le nom d'un produit (ex : *"bouteille d'eau"*).
2. L'application scrape en direct la plateforme **Jumia** et affiche jusqu'à 6 résultats pertinents (image, titre, prix) classés par ordre d'apparition sur jumia, sans doublons.
3. L'utilisateur peut, pour chaque produit :
   - Soit **le trier** : un modèle de Deep Learning analyse le produit et détermine sa consigne de tri et donne le pourcentage de confiance ;
   - Soit **le consulter sur Jumia** : un lien ouvre la fiche d'origine du produit dans un nouvel onglet.
4. Après un tri, l'écran affiche la poubelle correspondante avec sa couleur officielle, une consigne rédigée pour l'usager, et une courte animation illustrant le geste de tri.

## Catégories de tri

| Poubelle | Couleur | Matières concernées |
|---|---|---|
| JAUNE | 🟡 | plastic, metal, cardboard |
| VERTE | 🟢 | glass |
| BLEUE | 🔵 | paper |
| D3E (électronique) | ⚪ Gris | détecté via la catégorie Jumia ou des mots-clés (le dataset d'entraînement ne contient pas d'électronique) |
| MARRON/NOIRE | ⚫ | trash (déchets résiduels) |

## Architecture technique

```
EcoSort-Search/
├── app/
│   ├── api.py          # API FastAPI : endpoints /search et /classify
│   ├── scraper.py      # Scraping Jumia (requête HTTP directe, secours navigateur si nécessaire)
│   ├── mapping.py      # Traduction classes du modèle → poubelles officielles + détection D3E
│   ├── cache.py        # Cache mémoire pour éviter de rescraper inutilement ce qui a déjà été scrapé ya pas longtemps
│   └── main.py         # Interface utilisateur (Streamlit)
├── models/
│   ├── modele_eco_sort_best.keras       # Meilleur modèle sauvegardé (EarlyStopping)
│   └── modele_eco_sort_finetuned.h5     # Modèle fine-tuné, chargé par l'API
├── notebooks/
│   └── training_complet.ipynb           # Notebook d'entraînement du modèle
├── tests/
│   └── test_scraper.py                  # Tests unitaires (extraction HTML, sans navigateur)
├── .streamlit/                          # Configuration Streamlit
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── start.sh                             # Démarre l'API et l'interface ensemble
```

**Architecture d'exécution** — L'application tourne dans un conteneur unique. Au démarrage, `start.sh` lance l'API FastAPI (en interne, port 8000), attend qu'elle réponde, puis lance l'interface Streamlit (port 8501, seul port exposé). L'interface communique avec l'API en local dans le conteneur.

**Modèle IA** — Transfer Learning EfficientNetB3, entraîné sur le dataset *Garbage Classification* (Kaggle), 6 classes (`cardboard`, `glass`, `metal`, `paper`, `plastic`, `trash`). Précision de validation : **90 %**. EarlyStopping et ReduceLROnPlateau utilisés pendant l'entraînement.

**Scraping** — Le scraper tente d'abord une requête HTTP simple pour aller vite ; si Jumia bloque (protection Cloudflare), il bascule automatiquement sur un navigateur automatisé pour contourner la vérification anti-robot. Les résultats sont dédoublonnés : les faux liens (renvoyant vers la page de connexion Jumia) sont ignorés, et un même produit n'apparaît qu'une fois.

**Détection D3E** — Comme le dataset Kaggle ne contient aucune image d'appareil électronique, cette catégorie est détectée autrement : d'abord via la catégorie officielle du produit fournie par Jumia (la plus fiable), puis par une liste de mots-clés sur le nom du produit en filet de sécurité (téléphone, chargeur, écouteurs, montre, etc.).

**Interface** — Développée avec Streamlit. Chaque produit propose deux actions indépendantes : trier le produit, ou l'ouvrir sur Jumia. Le résultat de tri affiche la consigne dans un langage adressé à l'usager plutôt qu'en vocabulaire technique.

## Lancer le projet avec Docker

Prérequis : [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et lancé.

```bash
docker compose up -d --build
```

Puis ouvrir :

```
http://localhost:8501
```

Pour arrêter :

```bash
docker compose down
```

Le projet fonctionne aussi avec un unique conteneur, sans docker-compose :

```bash
docker build -t ecosort .
docker run -p 8501:8501 ecosort
```

## Répartition du travail

| Rôle | Responsabilités |
|---|---|
| Architecte IA & Data | Entraînement du modèle, notebook, choix d'architecture |
| Scraping & Backend | Scraper Jumia, API FastAPI, cache, mapping vers les poubelles |
| Interface & DevOps | Interface Streamlit, design, containerisation Docker |

L'historique des Pull Requests sur GitHub (onglet *Pull requests*, fermées) retrace le détail des contributions, chaque fonctionnalité ayant fait l'objet d'une branche dédiée relue par au moins un autre membre de l'équipe avant fusion.

## Limites connues

- **Blocage Cloudflare possible** : Jumia peut occasionnellement demander une vérification humaine, en particulier en cas d'usage intensif dans un court laps de temps ou sur un réseau partagé. Un cache d'une heure limite ce risque en usage normal. Si ça survient, l'application affiche un message clair plutôt que de planter, et il suffit de réessayer quelques instants après.
- **Précision du modèle inégale selon les classes** : le modèle atteint 90 % de précision globale, mais la classe `trash` reste plus fragile (68 % de rappel), en partie à cause du plus faible nombre d'images disponibles pour cette catégorie dans le dataset d'origine.
- **Détection D3E imparfaite** : reposant sur la catégorie Jumia et des mots-clés plutôt que sur une reconnaissance visuelle (impossible avec le dataset disponible), certains appareils électroniques atypiques peuvent ne pas être détectés correctement.
- **Classification sur photos marketing** : le modèle a été entraîné sur des photos de déchets réels, alors qu'il analyse ici des photos de produits neufs issues de Jumia. C'est pourquoi la détection par catégorie et mots-clés prime sur le modèle image pour les cas où elle s'applique. 