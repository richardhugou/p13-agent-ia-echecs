# Coach IA pour les ouvertures d'échecs (FFE × Cavalier Data)

[![CI/CD Pipeline](https://github.com/richardhugou/p13-agent-ia-echecs/actions/workflows/ci.yml/badge.svg)](https://github.com/richardhugou/p13-agent-ia-echecs/actions)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces%20GPU%20T4-blue)](https://trikwi-p13-agent-echecs.hf.space)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Angular 17](https://img.shields.io/badge/Angular-17-DD0031.svg?logo=angular&logoColor=white)](https://angular.io/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-FF6F00.svg)](https://github.com/langchain-ai/langgraph)
[![Milvus](https://img.shields.io/badge/Vector_DB-Milvus-00A4E4.svg)](https://milvus.io/)

> **Preuve de concept (POC)** d'un agent conversationnel interactif conçu pour accompagner les jeunes espoirs de la Fédération Française des Échecs (FFE) dans l'apprentissage autonome et l'entraînement de leur répertoire d'ouvertures.

---

## 1. Contexte & Problématique

La Fédération Française des Échecs compte **60 000 licenciés**, dont environ 60 % de jeunes espoirs, pour seulement quelques centaines d'entraîneurs diplômés. Le goulot d'étranglement est avant tout humain : impossible d'offrir un accompagnement individualisé quotidien à chaque élève en dehors des séances de club ou entre deux rondes de tournoi.

**Le cas d'usage cible (Léa, 12 ans)** :  
Léa prépare son prochain tournoi et souhaite travailler son répertoire sur la Partie Italienne le soir chez elle. Son entraîneur n'étant pas disponible, l'agent agit comme un répétiteur interactif 24/7 pour :
1. Proposer les coups recommandés par la théorie des maîtres.
2. Expliquer les plans stratégiques et les idées sous-jacentes en citant des sources documentaires fiables.
3. Recommander des vidéos pédagogiques ciblées adaptées à la position.
4. Évaluer objectivement la position dès que l'élève s'écarte des sentiers théoriques.

---

## 2. L'Application en Action

L'application propose une interface échiquéenne fluide (Angular 17) connectée en temps réel au graphe d'orchestration :

![Interface d'entraînement aux ouvertures](livrables/rendu/captures/ui-conseils-italienne.png)

- **Vidéo de démonstration en conditions réelles (~4 min)** : [Voir sur Loom](https://www.loom.com/share/d9b9362a60d74c838f022c29f307d811)
- **Vitrine Cloud en direct (GPU NVIDIA T4)** : https://trikwi-p13-agent-echecs.hf.space

---

## 3. Parcours Utilisateur

```
[1. Choix du camp] ──► [2. Jeu théorique] ──► [3. Conseils sourcés] ──► [4. Déviation moteur]
     (Blancs/Noirs)       (Réplique auto maîtres)    (Synthèse RAG + Vidéo)       (Évaluation Stockfish)
```

1. **Orientation du plateau** : L'élève choisit son camp (ex: les Blancs) et sélectionne une ouverture parmi les répertoires supportés (ou en saisie libre).
2. **Jeu théorique interactif** : L'élève joue sur l'échiquier ; l'agent réplique instantanément avec le coup des maîtres le plus fréquent issu de la base Lichess (2 M+ parties).
3. **Demande de conseil (« Demander à Chessbot »)** : L'agent affiche les flèches tactiques sur l'échiquier, les coups des maîtres avec leurs statistiques de victoire, une explication stratégique sourcée (Milvus) et la vidéo pédagogique associée.
4. **Bascule moteur sur coup hors théorie** : Dès que l'élève joue un coup non théorique (ex: `4.g4?!`), l'agent bascule automatiquement sur le moteur **Stockfish 16** pour fournir une évaluation objective chiffrée (en centipions / mat).

---

## 4. Architecture Logicielle

Le système garantit une stricte séparation des responsabilités : **les faits proviennent des moteurs spécialisés, le LLM intervient uniquement pour la formulation pédagogique.**

```
                                 ┌───────────────┐
                                 │   MONGODB     │  (Cache applicatif transverse :
                                 │    CACHE      │   Lichess, Stockfish, Vidéos)
                                 └───────▲───────┘
                                         ┆ (lecture / écriture)
      Navigateur (Élève) ──► FRONT ANGULAR (Échiquier responsive & panneau coach)
                                 ↕ position FEN / réponse
                           FASTAPI + LANGGRAPH (Orchestration déterministe)
                ┌────────────────────────┼────────────────────────┐
                ▼                        ▼                        ▼
        LICHESS EXPLORER             STOCKFISH               MILVUS
      (Théorie & statistiques)      (Moteur UCI)       (Base vectorielle)
                                                                  ▼
                                                      LLM LOCAL / CLOUD (Ollama)
                                                                  ▼
                                                           RÉPONSE SOURCÉE
```

- **Clé pivot FEN** : La notation standard Forsyth-Edwards Notation (`FEN`) circule de manière uniforme entre tous les composants.
- **Milvus (Connaissance)** : Stockage vectoriel HNSW (embeddings 1024d) restreint au rayon d'ouverture actif.
- **MongoDB (Cache applicatif)** : Mémorisation des requêtes Lichess, évaluations Stockfish et métadonnées vidéo pour accélérer les temps de réponse.

---

## 5. Technologies Utilisées

| Composant | Technologie | Rôle technique |
|---|---|---|
| **Frontend** | Angular 17, TypeScript, TailwindCSS | Échiquier interactif, rendu SVG des flèches, panneau coach réactif. |
| **API Backend** | FastAPI, Python 3.12, Uvicorn | Endpoints REST, validation Pydantic, gestion asynchrone. |
| **Orchestration** | LangGraph, LangChain Community | Graphe d'état déterministe avec embranchement théorie / moteur. |
| **Base Vectorielle** | Milvus Standalone (HNSW / Cosinus) | Indexation et recherche sémantique multilingue sur 477 fiches. |
| **Embeddings** | `qwen3-embedding:0.6b` (1024d) | Projection vectorielle unifiée des concepts français et anglais. |
| **LLM Synthèse** | `qwen3.5:4b` / `qwen2.5:3b` (Ollama) | Synthèse pédagogique sourcée sous contrainte stricte de prompt. |
| **Moteur Tactique** | Stockfish 16 UCI (binaire C++) | Évaluation objective et calcul des variantes tactiques hors théorie. |
| **Base de Référence** | Lichess Opening Explorer API | Statistiques de victoires sur 2 millions de parties de maîtres. |
| **Cache & Persistance** | MongoDB 7.0 | Mise en cache transverse et historisation des runs d'évaluation. |
| **Tracking & Évaluation** | MLflow 2.10 | Évaluation A/B du RAG sur le Gold Set de 25 questions. |

---

## 6. Démarrage Rapide (Local)

### Prérequis
- **Docker Desktop** (avec Docker Compose).
- Optionnel : **Ollama** installé sur la machine hôte pour la synthèse LLM locale.

### Lancement en une commande

```bash
git clone https://github.com/richardhugou/p13-agent-ia-echecs.git
cd p13-agent-ia-echecs
./demarrer.sh
```

Le script automatise l'ensemble du cycle de vie :
1. Vérification et lancement d'Ollama sur l'hôte avec téléchargement des modèles requis.
2. Initialisation du fichier de configuration `.env`.
3. Construction et démarrage des 7 conteneurs Docker (`docker compose up -d --build`).
4. Attente active des healthchecks de l'API et de la base vectorielle.

*Temps de démarrage mesuré lors d'une installation fraîche : **2 min 09**.*

### Accès aux interfaces locales
- **Application Web** : http://localhost:4200
- **Documentation API (Swagger)** : http://localhost:8000/docs
- **Serveur de Tracking MLflow** : http://localhost:5001

---

## 7. Performances Mesurées

Toutes les métriques présentées ci-dessous sont reproductibles via les bancs de tests automatisés du projet :

| Métrique | Objectif | Résultat mesuré | Preuve / Méthode |
|---|---|---|---|
| **Légalité des coups** | 0 coup illégal | **0 / 56 coups testés** | Validation de bout en bout via `python-chess` |
| **Qualité RAG (Recall@5)** | $\ge 0,80$ | **1,0** | Gold Set de 25 questions étalonné sous MLflow |
| **Abstention hors sujet** | 5 / 5 | **5 / 5 requêtes bloquées** | Filtrage par rayon d'ouverture + seuil filet 0,58 |
| **Recherche vectorielle** | $< 100\text{ ms}$ | **7 à 11 ms** (p95) | Index HNSW Milvus sur 477 fiches |
| **Latence globale (Cloud GPU T4)** | $< 8\text{ s}$ | **1,81 s (p50) · 2,41 s (p95)** | Banc haute précision sur Hugging Face Spaces |
| **Latence globale (Local CPU)** | $< 8\text{ s}$ | **2,69 s (p50) · 6,35 s (p95)** | Banc local avec Ollama CPU hôte |
| **Coût d'API LLM** | 0,00 € | **0,00 €** | Modèles open source sur GPU Cloud / local |

---

## 8. YouTube dans le POC vs Étude d'Analyse Vidéo (Partie 2)

Le projet intègre deux volets vidéo distincts :

### 1. YouTube dans le POC (Fonctionnalité Développée)
- **Principe (Position $\rightarrow$ Vidéo)** : L'agent identifie l'ouverture jouée sur l'échiquier et interroge l'API officielle YouTube Data v3 pour proposer des vidéos pédagogiques recommandées (titre, miniature, durée, lien direct).
- **Conformité** : Traitement strict des métadonnées officielles, sans aucun téléchargement illégal.

### 2. Analyse Vidéo Automatique (Étude de Faisabilité — Partie 2)
- **Principe (Vidéo $\rightarrow$ Position)** : Conception d'un pipeline d'ingénierie permettant d'extraire les images d'un cours vidéo, de détecter l'échiquier, de reconstruire la position FEN et de lier chaque position au **timestamp exact** où elle est expliquée.
- **Livrable** : Note d'ingénierie détaillée, architecture MCP, estimation de faisabilité (30–40 j-h, 15–20 k€ build) et modèle de coûts OPEX.

---

## 9. Livrables & Structure du Dépôt

```
├── backend/          # API FastAPI, moteur Stockfish, services métier, tests pytest
├── frontend/         # Application Angular 17, composant échiquier, panneau coach
├── etl/              # Pipeline ETL (manifeste corpus.yml, extraction, vectorisation Milvus)
├── evaluation/       # Gold Set 25 questions, scripts d'évaluation RAG A/B, tracking MLflow
├── notebooks/        # 7 notebooks Jupyter de recherche, d'EDA et de benchmarking
├── space/            # Configuration Docker et scripts de déploiement Hugging Face Spaces GPU T4
├── livrables/        # Présentation de soutenance (PDF/HTML), note d'analyse vidéo, scripts de build
└── README.md         # Point d'entrée officiel du projet
```

### Documents de Soutenance
- [Support de présentation officiel (PDF 18 diapos)](livrables/rendu/presentation-soutenance.pdf)
- [Note d'ingénierie — Analyse Vidéo & Architecture MCP (PDF)](livrables/rendu/Mettez_en_place_un_agent_IA_Hugou_Richard/Hugou_Richard_3_note_analyse_video_082026.pdf)

---

## 10. Auteur & Licence

- **Auteur** : Richard Hugou — *IA Engineer, Cavalier Data*
- **Partenariat** : Projet OpenClassrooms × Fédération Française des Échecs
- **Code source** : MIT License
