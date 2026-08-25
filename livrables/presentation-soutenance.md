# Présentation — Coach IA pour les ouvertures d'échecs (FFE)

> **Structure en 19 diapositives** :
> 1. Titre · 2. Besoin & contexte · 3. Parcours utilisateur (Le service proposé) · 4. L'application en action · 5. Architecture logicielle · 6. Orchestration de l'agent · 7. Gisement de données · 8. Recherche sémantique · 9. Performances mesurées · 10. Limites de l'architecture actuelle · 11. Architecture de déploiement cible · 12. Dimensionnement et montée en charge · 13. Coûts de fonctionnement · 14. La limite du POC : recommander une vidéo ne suffit pas · 15. Analyse vidéo : fonctionnement & double flux · 16. Technologies Computer Vision & Arbitrages · 17. Faisabilité et coûts de l'analyse vidéo · 18. Résumé du POC · 19. Merci.

---

## Diapo 1 — Titre

**Un coach IA pour les ouvertures d'échecs**
Preuve de concept pour la Fédération Française des Échecs.
Richard Hugou, IA Engineer, Cavalier Data.
Soutenance — Août 2026.

---

## Diapo 2 — Besoin et contexte

La FFE compte **60 000 licenciés**, dont ~60 % de jeunes espoirs, pour seulement quelques centaines d'entraîneurs qualifiés. Le goulot d'étranglement est humain.

> **Le cas d'usage cible : Léa, 12 ans**  
> Elle prépare son prochain tournoi et souhaite travailler son répertoire sur la Partie Italienne le soir. Son entraîneur n'étant pas disponible, elle a besoin d'un répétiteur interactif 24/7.

**Les 4 capacités attendues de l'agent** :
1. **Jouer** : proposer les coups recommandés par la théorie des maîtres.
2. **Expliquer** : justifier les plans stratégiques en citant des sources documentaires fiables.
3. **Conseiller** : recommander des vidéos pédagogiques ciblées.
4. **Évaluer** : analyser objectivement toute sortie de théorie via un moteur d'échecs.

---

## Diapo 3 — Parcours utilisateur (Le service proposé)

Scénario nominal de l'élève (les Blancs sur la Partie Italienne) appuyé par les captures réelles :

1. **Orientation & Choix** : L'élève sélectionne son camp (les Blancs). L'échiquier s'oriente immédiatement et l'ouverture cible (Partie Italienne) est activée. *(Capture : `step-1-orientation.png`)*
2. **Jeu théorique interactif** : L'élève joue ses coups sur l'échiquier ; l'agent réplique automatiquement avec le coup des maîtres le plus fréquent (1.e4 e5, 2.Cf3 Cc6). *(Capture : `step-2-jeu.png`)*
3. **Conseil à la demande (« Demander à Chessbot »)** : À 3.Fc4, affichage des flèches tactiques, coups maîtres, synthèse RAG sourcée et vidéo YouTube associée. *(Capture : `step-3-conseils.png`)*
4. **Déviation moteur sur coup hors théorie** : Sur un coup hors répertoire (ex: 4.g4?!), l'agent bascule instantanément sur Stockfish avec évaluation chiffrée (-1,47 cp).

*Principe directeur : les faits sont extraits des moteurs spécialisés, le LLM intervient uniquement pour la formulation.*

---

## Diapo 4 — L'application en action : Frontend & API Backend

**Preuves d'implémentation réelles** :
- **Frontend Angular 17** : interface échiquéenne fluide connectée en temps réel au backend.
- **Backend FastAPI (`/docs`)** : endpoints REST documentés sous OpenAPI 3.1 (`/api/v1/moves`, `/evaluate`, `/videos`, `/vector-search`, `/agent/ask`).
- **Démonstration en vidéo (~4 min)** : scénario complet filmé en conditions réelles (QR code Loom).

Visuels :
- Capture réelle de l'échiquier et du panneau coach (`livrables/rendu/captures/ui-conseils-italienne.png`).
- Capture réelle de la documentation Swagger UI FastAPI (`livrables/rendu/captures/swagger-api-docs.png`).
- QR Code vectoriel menant vers la vidéo de démonstration Loom.

---

## Diapo 5 — Architecture logicielle

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

- **Clé pivot FEN** : notation standardisée circulant sans ambiguïté entre tous les composants.
- **Milvus (Connaissance)** : fiches documentaires vectorisées (embeddings 1024d).
- **MongoDB (Cache & État)** : persistance transverse des requêtes Lichess, évaluations Stockfish et métadonnées.

---

## Diapo 6 — Orchestration de l'agent

Graphe d'exécution déterministe LangGraph (`backend/graph/`) :

```
Position FEN ──► Validation ──► Identification de l'ouverture ──► En théorie ?
                      │                                               │
             [Oui: parties >= 5]                             [Non: hors théorie]
                      ▼                                               ▼
          Lichess Opening Explorer                               Stockfish UCI
         (Coups des maîtres & stats)                         (Évaluation chiffrée)
                      ▼                                               │
             Recherche RAG Milvus                                     │
           (Rayon d'ouverture signé)                                  │
                      ▼                                               │
              Vidéos YouTube                                          │
                      ▼                                               │
               Synthèse LLM ◄─────────────────────────────────────────┘
         (Formulation pédagogique sourcée)
```

- **Routage déterministe** : aucun choix de coup n'est délégué au LLM.
- **Dégradation gracieuse** : mécanismes de repli sur chaque nœud en cas d'indisponibilité.

---

## Diapo 7 — Gisement de données

**4 sources documentaires complémentaires** :
- **Référentiel des ouvertures** : nomenclature et codes ECO officiels.
- **Lichess Explorer** : base de 2 M+ parties et statistiques de victoires des maîtres.
- **Wikipédia / Wikibooks** : corpus encyclopédique structuré en fiches de 300 à 500 mots.
- **YouTube** : métadonnées et horodatages de vidéos pédagogiques.

**Pipeline ETL rejouable et idempotent** :
`Extraction (manifeste signé) -> Nettoyage -> Fiches structurées -> Vecteurs 1024d -> Milvus`

**Corpus final validé** :
**3 251 pages disponibles -> 161 retenues -> 477 fiches** (95 positions FEN de référence, 0 échec de calcul).

---

## Diapo 8 — Recherche sémantique

**Problématique** : retrouver les concepts stratégiques sans correspondance exacte de mots-clés (ex : *« pourquoi le fou vise f7 ? »* -> fiches *Giuoco Piano* et *Attaque f7*).

```
Question élève ──► Embedding (1024d) ──► Cosinus HNSW (Milvus) ──► Fiches pertinentes ──► LLM
```

- **Espace vectoriel unifié** : modèle multilingue (`qwen3-embedding:0.6b`, 1024 dimensions).
- **Filtrage par rayon d'ouverture** : recherche restreinte au rayon actif pour empêcher la récupération de sources hors périmètre.
- **Performances mesurées** : recherche en **7 à 11 ms** ; séparation sémantique portée de 0,29 à **0,50**.

---

## Diapo 9 — Performances mesurées

| Indicateur clé | Objectif | Résultat mesuré | Preuve / Méthode |
|---|---|---|---|
| **Coups illégaux en sortie** | 0 | **0 sur 56 testés** | Validation de bout en bout via `python-chess` |
| **Recall@5 (Gold Set 25 questions)** | >= 0,80 | **1,0** | Runs tracés sous MLflow |
| **Abstention sur les pièges** | 5 / 5 | **5 / 5 requêtes bloquées** | Filtrage par rayon d'ouverture + seuil filet à 0,58 |
| **Réponses avec sources valides** | 100 % | **100 %** | Garanti par construction du pipeline |
| **Recherche vectorielle Milvus** | < 100 ms | **7 à 11 ms** (p95) | Index HNSW Milvus |
| **Latence globale (Cloud GPU T4)** | p95 < 8 s | **1,81 s (p50) · 2,41 s (p95)** | Banc mesuré sur Hugging Face Spaces |
| **Latence globale (Local CPU)** | p95 < 8 s | **2,69 s (p50) · 6,35 s (p95)** | Banc local avec Ollama CPU hôte |
| **Coût d'API LLM** | 0 € | **0,00 €** | Modèles open source sur GPU Cloud / local |

---

## Diapo 10 — Limites de l'architecture actuelle

**Constat sur le déploiement POC mono-conteneur** :
- **Mono-conteneur** : Front + API + Stockfish + Milvus + LLM (Ollama) colocalisés sur la même machine hôte.
- **Goulot d'étranglement GPU / LLM** : 1 requête = nominal (2,41 s T4) ; *N* requêtes simultanées = collision sur la VRAM et file d'inférence saturée.
- **Couplage fort** : Impossible de scaler le serveur web FastAPI sans dupliquer inutilement l'instance LLM.

| Périmètre | Mitigation appliquée |
|---|---|
| **Dépendances externes (Lichess, YouTube)** | Cache transverse MongoDB (TTL 24h / 7j) + mode dégradé gracieux |
| **Hallucinations LLM (Tactique)** | 0 coup délégué au LLM : coups imposés par les moteurs de règles |
| **Périmètre des répertoires** | Corpus extensible via l'ETL rejouable (`etl/corpus.yml`) |
| **Montée en charge (Concurrence)** | Séparation de tiers : API stateless réplicable + Pool GPU dédié |

*Conclusion : Le POC valide le fonctionnement. La production impose de séparer le compute HTTP stateless de l'inférence GPU.*

---

## Diapo 11 — Architecture de déploiement cible

```
                 UTILISATEURS (Web / Mobile)
                              │
                              ▼
                       LOAD BALANCER
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
              API #1       API #2       API #N
             FastAPI      FastAPI      FastAPI (Stateless sur CPU)
                 │            │            │
                 └────────────┼────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
      MongoDB              Milvus             Stockfish 16
       Cache             Vector DB             Moteur CPU
                              │
                              ▼ (Requêtes de génération)
                   POOL D'INFÉRENCE GPU (LLM)
           ⚠️ Goulot dimensionnant (vLLM / Triton / Ollama)
```

- **Principe architectural** : Les instances API FastAPI stateless scalent horizontalement sur CPU à coût minimal ; le pool GPU d'inférence est isolé et ajusté selon la charge.

---

## Diapo 12 — Dimensionnement et montée en charge

### 1. Facteurs dimensionnants par composant

| Composant | Facteur limitant | Stratégie de passage à l'échelle |
|---|---|---|
| **API Backend (FastAPI)** | Nombre de requêtes HTTP | Réplication horizontale stateless derrière répartiteur de charge |
| **Moteur Stockfish** | CPU | Parallélisation multi-cœurs (0,8 s / coup) |
| **Base Milvus** | Volume documentaire & index | Service mutualisé (recherche 7–11 ms) |
| **Base MongoDB** | Volume de cache | Instance partagée avec TTL |
| **Inférence LLM** | VRAM & compute GPU | **Goulot principal** : dimensionnement du pool d'instances GPU |

### 2. Modélisation de volume (Base FFE : 60 000 licenciés)

*Hypothèse d'utilisation : 30 analyses / utilisateur / mois.*

| Scénario d'adoption | Utilisateurs actifs | Volume mensuel estimé | Débit moyen estimé | Dimensionnement GPU cible |
|---|---|---|---|---|
| **Scénario 1 %** | 600 utilisateurs | 18 000 requêtes / mois | ~0,25 req / min | Pool GPU partagé |
| **Scénario 5 %** | 3 000 utilisateurs | 90 000 requêtes / mois | ~1,25 req / min | Pool GPU dimensionné sur trafic de pointe |
| **Scénario 10 %** | 6 000 utilisateurs | 180 000 requêtes / mois | ~2,50 req / min | Pool GPU avec politique d'autoscaling |

---

## Diapo 13 — Coûts de fonctionnement

> *Estimation budgétaire — Architecture cible de production (Scénario 5 % / 3 000 utilisateurs actifs)*

### 1. Postes de dépenses opérationnelles (OPEX mensuel estimé)

| Poste d'infrastructure | Rôle technique | Estimation mensuelle (Scénario 5 %) |
|---|---|---|
| **Compute Inférence GPU** | Pool GPU pour le modèle Qwen (ex: instances T4 / L4 à l'usage) | ~150 à 280 € / mois |
| **Compute API Backend** | Conteneurs API FastAPI stateless (CPU / RAM) | ~30 à 50 € / mois |
| **Bases de données** | Instances managées Milvus + MongoDB | ~50 à 80 € / mois |
| **Stockage & Monitoring** | Logs, métriques, sauvegardes | ~20 € / mois |
| **APIs Externes (LLM / YouTube)** | Modèles open source + quotas YouTube Data API officiels | **0,00 €** |
| **TOTAL OPEX ESTIMÉ** | **Infrastructure de production dimensionnée pour 3 000 users** | **~250 à 430 € / mois** |

### 2. Investissement de développement (Build)
- **Développement initial du POC** : ~25 à 30 jours-homme.
- **Stack 100 % open source** : aucune licence propriétaire.

---

## Diapo 14 — La limite du POC : recommander une vidéo ne suffit pas

> *Aujourd'hui, l'agent trouve une vidéo par ouverture. L'objectif est de retrouver le passage pertinent.*

```
       AUJOURD'HUI (POC)                                 OBJECTIF VISÉ
       
       Position de l'élève                             Position de l'élève
               │                                               │
               ▼                                               ▼
        Partie Italienne                                      FEN
               │                                               │
               ▼                                               ▼
            YouTube                                Index des positions vidéo
               │                                               │
               ▼                                               ▼
       3 vidéos proposées                              Vidéo X — 04:32
       
 ❌ Mais où est ma position ?                   « Cette position est expliquée
 ❌ À quel moment est-elle expliquée ?                      à 4:32 »
```

**Le problème à résoudre** : passer d'une recommandation globale par ouverture à une recommandation précise à la position et au timestamp près.

---

## Diapo 15 — Analyse vidéo : fonctionnement & double flux

```
                            VIDÉO DU COURS
                           /              \
                          ▼                ▼
              [FLUX COMPUTER VISION]    [FLUX TRANSCRIPTS]
              Échantillonnage (1/5s)    Whisper / Sous-titres CC
                      │                            │
                      ▼                            ▼
              Détection échiquier       Coups cités extraits
              (OpenCV, Hough, coins)       (python-chess)
                      │                            │
                      ▼                            │
              Rectification perspective                    │
              (Homographie 8x8 -> 64 cases)                │
                      │                            │
                      ▼                            │
              Reconnaissance des pièces                    │
              (CNN 2D 13 classes)                          │
                      │                            │
                      ▼                            │
              Reconstruction FEN & validation              │
              (python-chess : règles & roques)             │
                      │                            │
                      └─────────────┬──────────────┘
                                    ▼
                        ALIGNEMENT MULTIMODAL
                                    │
                                    ▼
                   FEN ↔ Vidéo ↔ Timestamp (04:32)
```

*Principe : La vision identifie la position montrée, le transcript extrait ce qui est expliqué, l'alignement crée la ressource pédagogique exacte.*

---

## Diapo 16 — Technologies Computer Vision & Arbitrages (2D vs 3D)

1. **Échiquier 2D (MVP — Écrans logiciels)** :
   - **OpenCV** : Localisation des coins et rectification par homographie projective pour obtenir un carré parfait 8×8 (64 cases).
   - **CNN léger (13 classes)** : Classification rapide case par case (vide + 6 blanches + 6 noires).
   - **Inférence CPU (< 3 min / vidéo)** : Problème de vision classique quasi résolu (*LiveChess2FEN, Chesscog*).

2. **Plateau 3D (V2 — Parties physiques)** :
   - **Détecteur d'objets (YOLO)** : Nécessite un dataset lourd comme *ChessReD* (10 800 images réelles).
   - **Complexités majeures** : Angles de caméra variables, ombres, occlusions et mains masquant les pièces.
   - **Arbitrage d'ingénierie** : Exclu du MVP, repoussé en V2 après retour d'expérience du pilote.

3. **Clé pivot FEN commune** :
   - **Validation légale** : `python-chess` rejette automatiquement tout FEN non conforme.
   - **Jointure directe** : Les FEN indexés rejoignent immédiatement la base vectorielle Milvus et Stockfish sans réentraînement de l'agent.

---

## Diapo 17 — Faisabilité et coûts de l'analyse vidéo

### 1. Approche MVP : Transcripts-first + Vision 2D
- Traitement prioritaire des cours avec échiquier 2D numérique (90 % du catalogue FFE / YouTube).
- Coût de calcul ultra-léger : ~3 min CPU / vidéo (20 vidéos / heure / worker CPU).

### 2. Chiffrage du pilote (100 vidéos de cours)
- **Délai & Effort** : 6 à 8 semaines · **30 à 40 jours-homme** (budget : **15 à 20 k€**).
- **Coût d'exécution Run** : **~0,10 à 0,15 € / vidéo traitée** (compute CPU + stockage).
- **Indicateurs clés** : Précision FEN $\ge 90\%$ · $\ge 30\%$ des requêtes enrichies d'un timestamp exact.

### 3. Arbitrages d'ingénierie & Juridique
- **Exclusion de la 3D en V1** : focalisation sur la 2D pour maximiser le ROI et la fiabilité.
- **Périmètre juridique maîtrisé** : licences Creative Commons et partenariats chaînes officielles FFE (zéro stockage de vidéos).

*Message clé : Le coût du système réside dans le développement initial (jours-homme), pas dans le GPU (le MVP 2D tourne sur CPU).*

---

## Diapo 18 — Résumé du POC

1. **Agent fonctionnel** : Reconnaissance théorique immédiate, explications pédagogiques sourcées, bascule moteur Stockfish.
2. **Architecture maîtrisée** : Orchestration déterministe LangGraph, Stockfish UCI, base vectorielle Milvus, cache MongoDB.
3. **Gisement de données validé** : Pipeline ETL rejouable (4 sources, 477 fiches structurées, 95 FEN de référence).
4. **Performances prouvées** : 0 coup illégal sur 56 positions, latence sous 2,5 s sur GPU T4 (p95 = 2,41 s).
5. **Déploiement éprouvé** : Conteneurisation locale reproductible (2 min 09) et déploiement GPU validé sur Hugging Face Spaces.
6. **Étude d'ingénierie livrée** : Note de cadrage, architecture MCP, faisabilité technique et modèle de coûts formalisés.

---

## Diapo 19 — Merci

**Merci pour votre attention.**

**Richard Hugou**  
IA Engineer — Cavalier Data  
*Projet OpenClassrooms × Fédération Française des Échecs*  

- **Dépôt GitHub public** : https://github.com/richardhugou/p13-agent-ia-echecs
