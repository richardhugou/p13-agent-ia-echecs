# Agent IA — Apprentissage des ouvertures d'échecs (POC FFE)

POC d'un agent conversationnel qui accompagne de jeunes joueurs dans l'apprentissage des ouvertures : coups théoriques (Lichess), contexte pédagogique (RAG Milvus), vidéos (YouTube), évaluation moteur (Stockfish) — orchestrés par LangGraph, servis par FastAPI, avec un échiquier Angular.

## Démarrage rapide

Prérequis : **Docker Desktop** ; en option **Ollama** sur la machine hôte (synthèse LLM locale — sans lui, mettre `LLM_PROVIDER=none` : l'agent répond par gabarit déterministe).

```bash
./demarrer.sh
```

Le script fait tout : Ollama vérifié/démarré + modèles téléchargés, `.env` créé depuis l'exemple, `docker compose up -d --build`, attente des healthchecks et de la bibliothèque vectorielle.

Équivalent manuel : copier `.env.example` en `.env` (remplir `LICHESS_API_TOKEN`, requis pour la théorie ; `YOUTUBE_API_KEY`, optionnel) puis `docker compose up -d --build`.

- **Application** : http://localhost:4200 · **API (Swagger)** : http://localhost:8000/docs · **MLflow** : http://localhost:5001
- **Démo en ligne** (vitrine mono-conteneur, gabarit sans LLM, auto-déployée par GitHub Actions) : https://trikwi-p13-agent-echecs.hf.space
- Test d'installation fraîche (`./tester-installation.sh`, images construites et cache de build supprimés) : app utilisable en **2 min 09**, bibliothèque vectorielle prête à **2 min 28** — critère < 5 min tenu.

### Remplir la bibliothèque (une fois, ~10 min)

Le corpus (161 pages wiki → 477 fiches vectorisées) se charge par l'ETL, depuis l'hôte :

```bash
cd etl && uv run extraire.py && uv run transformer.py && uv run charger.py
```

Règle du projet : **pas de manifeste signé, pas d'extraction** — le périmètre exact vit dans `etl/corpus.yml` (signé, versionné).

## Architecture

| Service | Port hôte | Rôle |
|---|---|---|
| frontend | 4200 | Angular + ngx-chess-board, servi par nginx (image 78 Mo) |
| api | 8000 | FastAPI + graphe LangGraph + Stockfish embarqué |
| milvus (+ etcd, minio) | 19530 | recherche vectorielle (exposé pour le job ETL local) |
| mongodb | — | caches (explorer 24 h, évals, vidéos 7 j) |
| mlflow | 5001 | tracking des runs d'évaluation (5000 hôte squatté par AirPlay macOS) |

Le LLM n'est **jamais la source de vérité** : coups = stats Lichess filtrées par python-chess (0 coup illégal), évaluations = Stockfish, sources = ajoutées par le code. Schémas détaillés : `docs/05-architecture-technique.md`.

## Variables d'environnement (`.env.example`)

| Variable | Rôle | Défaut |
|---|---|---|
| `LLM_PROVIDER` / `LLM_MODEL` | synthèse : `ollama` (local, défaut) · `none` (gabarit) · `anthropic` (option) | ollama / qwen3.5:4b |
| `OLLAMA_BASE_URL` | Ollama sur l'hôte (LLM + embeddings) | http://localhost:11434 |
| `LICHESS_API_TOKEN` | explorer masters (401 sans jeton) | — |
| `YOUTUBE_API_KEY` | YouTube Data API v3 (métadonnées seules) | — |
| `EMBEDDING_MODEL` | tag Ollama du modèle d'embeddings | qwen3-embedding:0.6b |
| `STOCKFISH_DEPTH` / `STOCKFISH_TIME_MS` | budget moteur | 16 / 1000 |
| `THEORY_MIN_GAMES` | seuil du routeur théorie/moteur | 5 |
| `RAG_TOP_K` | fiches remontées par recherche | 5 |
| `MILVUS_HOST` / `MILVUS_PORT` · `MONGO_URI` | connexions internes | milvus:19530 · mongodb |
| `CORS_ORIGINS` · `API_PORT` | front autorisé · port API | localhost:4200 · 8000 |
| `MLFLOW_TRACKING_URI` | tracking (dans le réseau compose) | http://mlflow:5000 |

## Arborescence

```
backend/     # FastAPI, graphe LangGraph, services (lichess, stockfish, rag, youtube) + tests
frontend/    # Angular + ngx-chess-board + panneau coach (Dockerfile nginx)
etl/         # manifeste signé corpus.yml, extraction, transformation, chargement Milvus
evaluation/  # gold set 25 questions (figé) + évaluateur A/B → MLflow
notebooks/   # mesures exécutées et rejouables (inventaire, embeddings, EDA, éval, agent)
docs/        # conception, architecture, script de démo
livrables/   # présentation, étude partie 2 (analyse vidéo), autoévaluation
```

## Workflow Git

Gitflow simplifié : `main` (stable, démo) ← `develop` (intégration) ← `feature/<Nom>`. CI GitHub Actions : lint + tests backend, build frontend.

## Données & licences

- Parties et explorer **Lichess** : CC0. Référentiel d'ouvertures `lichess-org/chess-openings`.
- Corpus encyclopédique **Wikipédia FR / Wikibooks EN** : CC BY-SA — les réponses de l'agent citent leurs sources.
- **YouTube** : métadonnées via l'API officielle ; liens uniquement, aucun téléchargement.
- **Stockfish** : GPLv3 (version épinglée, voir Dockerfile backend).

## Évaluation & reproductibilité

- Gold set de 25 questions **figé** : `evaluation/gold_set.yml` ; runs A/B (chunking naïf vs soigné) loggés dans MLflow.
- Règle de labo : **aucune mesure ne vit uniquement dans une discussion** — chaque chiffre des slides sort d'un notebook exécuté (`notebooks/`) ou d'un run MLflow.

## Limites connues du POC

8 ouvertures couvertes (manifeste signé) ; pas d'authentification ; la vitrine en ligne est une variante dégradée assumée (gabarit sans LLM, sans cache) — la version complète s'exécute en local ; l'abstention tient par la **règle des rayons signés** + seuil filet `RAG_SCORE_MIN=0.58` (5/5 pièges par construction, notebooks 05/07) ; le système d'analyse vidéo (partie 2) est une étude, non implémentée — voir `livrables/`.
