# EcoSort-Search - Docker

Ce projet lance deux services dans un seul conteneur :

- l'API FastAPI sur `127.0.0.1:8000` a l'interieur du conteneur ;
- l'interface Streamlit sur `0.0.0.0:8501`, exposee au navigateur.

## Lancement avec Docker

```bash
docker build -t ecosort .
docker run --rm -p 8501:8501 ecosort
```

Ouvrir ensuite :

```text
http://localhost:8501
```

## Lancement avec Docker Compose

```bash
docker compose up -d --build
```

Puis ouvrir :

```text
http://localhost:8501
```

Pour arreter :

```bash
docker compose down
```

## Verification rapide

Dans l'application, chercher un produit comme `bouteille eau`, choisir un resultat Jumia, puis verifier que la consigne de tri apparait avec la couleur de poubelle correspondante.
