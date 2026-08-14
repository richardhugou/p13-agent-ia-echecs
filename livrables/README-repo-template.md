# [TEMPLATE] README du futur dépôt de code

> À copier en racine du dépôt Git au démarrage d'É1, puis à tenir à jour (le README se finalise en É6 avec le test d'installation fraîche).

---

# Agent IA — Apprentissage des ouvertures d'échecs (POC FFE)

POC d'un agent conversationnel qui accompagne de jeunes joueurs dans l'apprentissage des ouvertures : coups théoriques (Lichess), contexte pédagogique (RAG Milvus), vidéos (YouTube), évaluation moteur (Stockfish) — orchestrés par LangGraph, servis par FastAPI, avec un échiquier Angular.

## Démarrage rapide

Prérequis : Docker + Docker Compose, un fichier `.env` (copier `.env.example`).
Lancement : une seule commande compose ; l'application est disponible sur le port du front, l'API expose sa documentation Swagger, MLflow son tableau de bord.
Premier lancement : prévoir le téléchargement des images et du modèle d'embeddings (~quelques minutes).

## Architecture

*(insérer ici le schéma services + le schéma du graphe LangGraph — sources dans `docs/`)*

| Service | Rôle | Port hôte |
|---|---|---|
| frontend | Angular + ngx-chessboard | 4200 |
| api | FastAPI + LangGraph + Stockfish embarqué | 8000 |
| milvus (+ etcd, minio) | recherche vectorielle | 19530 / 9091 |
| mongodb | caches, sessions, runs | 27017 |
| mlflow *(optionnel)* | tracking & traces | 5000 |

## Variables d'environnement (`.env.example`)

| Variable | Rôle | Exemple/défaut |
|---|---|---|
| `LLM_PROVIDER` / `LLM_MODEL` / `LLM_API_KEY` | LLM de synthèse | *(décision D1)* |
| `YOUTUBE_API_KEY` | YouTube Data API v3 | — |
| `MILVUS_HOST` / `MILVUS_PORT` | connexion Milvus | milvus / 19530 |
| `MONGO_URI` | connexion MongoDB | mongodb://mongodb:27017 |
| `STOCKFISH_DEPTH` / `STOCKFISH_TIME_MS` | budget moteur | 16 / 1000 |
| `THEORY_MIN_GAMES` | seuil « position en théorie » | 5 |
| `EMBEDDING_MODEL` | modèle sentence-transformers | Qwen3-Embedding-0.6B |
| `RAG_TOP_K` | nb de chunks remontés | 5 |
| `CORS_ORIGINS` | origines front autorisées | http://localhost:4200 |
| `MLFLOW_TRACKING_URI` | tracking | http://mlflow:5000 |

## Arborescence

```
backend/    # FastAPI, graphe LangGraph, services (lichess, stockfish, rag, youtube)
frontend/   # Angular + ngx-chessboard
etl/        # ingestion corpus → Milvus + rapport EDA
docs/       # schémas, décisions, éval (gold set)
docker-compose.yml
.env.example
```

## Données & licences
- Parties et explorer **Lichess** : CC0. Référentiel d'ouvertures `lichess-org/chess-openings`.
- Corpus encyclopédique **Wikibooks/Wikipédia** : CC BY-SA — les réponses de l'agent citent leurs sources.
- **YouTube** : métadonnées via l'API officielle ; liens/embeds uniquement, aucun téléchargement.
- **Stockfish** : GPLv3 (version épinglée, voir Dockerfile backend).

## Évaluation & reproductibilité
- Gold set de 25 questions versionné dans `docs/`.
- Chaque run d'éval (params, recall@5, MRR, latences, coûts) est loggé dans MLflow ; les chiffres du rapport/slides proviennent exclusivement de ces runs.

## Démo
Scénario pas-à-pas et positions FEN de test : voir `docs/` (script de démo). Mode dégradé sans réseau : caches MongoDB pré-chauffés + fixtures.

## Limites connues du POC
8–10 ouvertures couvertes ; pas d'authentification ; exécution locale uniquement ; le système d'analyse vidéo (partie 2) est une étude, non implémentée — voir `livrables/`.
