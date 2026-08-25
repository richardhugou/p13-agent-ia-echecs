# Présentation — Coach IA pour les ouvertures d'échecs (FFE)

> **Structure en 17 diapositives** :
> 1. Titre · 2. Besoin & contexte · 3. L'application en action · 4. Parcours utilisateur · 5. Architecture logicielle · 6. Orchestration de l'agent · 7. Gisement de données · 8. Recherche sémantique · 9. Performances mesurées · 10. Déploiement · 11. Dimensionnement et montée en charge · 12. Coûts de fonctionnement · 13. La limite du POC : recommander une vidéo ne suffit pas · 14. Comment retrouver une position dans une vidéo ? · 15. Faisabilité de l'analyse vidéo · 16. Résumé du POC · 17. Merci.

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

## Diapo 3 — L'application en action

**Démonstration en conditions réelles (~4 min)** :
- Interface échiquéenne fluide (Angular 17) connectée à l'agent conversationnel.
- Parcours complet : choix du camp, répliques automatiques, conseils sourcés, bascule moteur sur sortie de théorie.
- *Lien vidéo Loom : https://www.loom.com/share/d9b9362a60d74c838f022c29f307d811*

Visuels :
- Capture réelle de l'application (`livrables/rendu/captures/ui-conseils-italienne.png`).
- QR Code vectoriel menant vers la vidéo de démonstration.

---

## Diapo 4 — Parcours utilisateur

Scénario nominal de l'élève (les Blancs sur la Partie Italienne) :

1. **Orientation du plateau** : choix du camp (« Je joue les Blancs ») et sélection de l'ouverture cible.
2. **Jeu théorique interactif** : l'élève joue ses coups ; l'agent joue automatiquement la réplique des maîtres la plus fréquente (1.e4 e5, 2.Cf3 Cc6).
3. **Conseil à la demande (« Demander à Chessbot »)** : à 3.Fc4, affichage des flèches tactiques, coups maîtres, synthèse RAG sourcée et vidéo YouTube associée.
4. **Bascule moteur sur coup hors théorie** : sur un coup hors répertoire (ex: 4.g4?!), l'agent bascule instantanément sur Stockfish avec évaluation chiffrée (-1,47 cp).

*Principe directeur : les faits sont extraits des moteurs spécialisés, le LLM intervient uniquement pour la formulation.*

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

## Diapo 10 — Déploiement

```
          DÉPLOIEMENT ACTUEL DU POC                   ÉVOLUTION : PASSAGE À L'ÉCHELLE
          
                 Utilisateur                                    Utilisateurs
                      │                                              │
                      ▼                                              ▼
           ┌─────────────────────┐                            ┌──────────────┐
           │ Hugging Face Space  │                            │ Instance API │ (Stateless)
           │ (NVIDIA GPU T4)     │                            └──────┬───────┘
           │                     │                                   │
           │ • Angular + FastAPI │                                   ▼
           │ • LangGraph         │                           Services partagés
           │ • Stockfish         │                            ┌──────┼──────┐
           │ • Milvus Lite       │                            ▼      ▼      ▼
           │ • Ollama + Qwen     │                         MongoDB Milvus  Pool GPU (LLM)
           └─────────────────────┘
```

- **Déploiement actuel (POC)** : Instance autonome sur Hugging Face Spaces avec GPU NVIDIA T4 (16 Go VRAM) et Ollama CUDA (coût : 0,40 $/h à l'usage).
- **Principe de montée en charge** : L'API FastAPI est stateless et réplicable horizontalement ; l'inférence LLM constitue le principal poste de calcul dimensionnant. Bases et moteurs sont mutualisés.

---

## Diapo 11 — Dimensionnement et montée en charge

### 1. Facteurs dimensionnants par composant

| Composant | Facteur limitant | Stratégie de passage à l'échelle |
|---|---|---|
| **API Backend (FastAPI)** | Nombre de requêtes HTTP | Réplication horizontale stateless derrière répartiteur de charge |
| **Moteur Stockfish** | CPU | Parallélisation multi-cœurs (0,8 s / coup) |
| **Base Milvus** | Volume documentaire & index | Service mutualisé (recherche 7–11 ms) |
| **Base MongoDB** | Volume de cache | Instance partagée avec TTL |
| **Inférence LLM** | VRAM & compute GPU | **Goulot principal** : dimensionnement du pool d'instances GPU |

### 2. Scénarios d'hypothèses de charge (Base FFE : 60 000 licenciés)

*Hypothèse d'utilisation : 30 analyses / utilisateur / mois.*

| Scénario d'adoption | Utilisateurs actifs | Volume estimé / mois | Débit moyen estimé | Dimensionnement GPU cible |
|---|---|---|---|---|
| **Scénario 1 %** | 600 utilisateurs | 18 000 requêtes / mois | ~0,25 req / min | 1 instance GPU partagée |
| **Scénario 5 %** | 3 000 utilisateurs | 90 000 requêtes / mois | ~1,25 req / min | 1 à 2 instances GPU |
| **Scénario 10 %** | 6 000 utilisateurs | 180 000 requêtes / mois | ~2,50 req / min | 2 à 3 instances GPU (avec autoscaling) |

---

## Diapo 12 — Coûts de fonctionnement

> *Estimation budgétaire — Architecture cible de production (Scénario 5 % / 3 000 utilisateurs)*

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

---

## Diapo 13 — La limite du POC : recommander une vidéo ne suffit pas

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

## Diapo 14 — Comment retrouver une position dans une vidéo ?

> *Construire un index : position FEN ↔ vidéo ↔ timestamp*

```
VIDÉO PÉDAGOGIQUE ──► Images clés (1/5s) ──► Détection échiquier ──► Reconnaissance pièces
                                                                             │
                                                                             ▼
FEN ↔ vidéo ↔ timestamp ◄── Validation python-chess ◄── Reconstruction FEN ◄┘
```

**Exemple d'indexation d'un cours (Vidéo « La Partie Italienne »)** :
- `04:12` $\rightarrow$ FEN A
- `04:32` $\rightarrow$ **FEN B (position exacte de l'élève)**
- `05:07` $\rightarrow$ FEN C
- `06:21` $\rightarrow$ FEN D

*Le FEN reste la clé pivot commune pour relier directement la vidéo à l'agent existant.*

---

## Diapo 15 — Faisabilité de l'analyse vidéo

> *Une extension techniquement faisable et articulée autour d'un MVP maîtrisé*

### 1. Approche MVP : Transcripts-first + Vision 2D
- Récupérer les transcripts textuels et reconstruire les coups cités avec `python-chess`.
- Utiliser la vision par ordinateur 2D uniquement pour confirmer la position et caler l'horodatage exact (~3 min CPU / vidéo).

### 2. Ce qu'on peut viser (Pilote de 100 vidéos)
- **Délai & Effort** : 6 à 8 semaines · **30 à 40 jours-homme** (budget : **15 à 20 k€**).
- **Indicateurs clés** : Précision FEN $\ge 90\%$ · Coût unitaire $\le 0,20\text{ € / vidéo}$ · $\ge 30\%$ des recommandations enrichies d'un timestamp exact.

### 3. Ce qu'on ne fait pas maintenant (Exclusions MVP)
- Pas de vision 3D généralisée ni d'angles de caméra inclinés en MVP $\rightarrow$ repoussés en V2 après mesure du pilote.

---

## Diapo 16 — Résumé du POC

1. **Agent fonctionnel** : Reconnaissance théorique immédiate, explications pédagogiques sourcées, bascule moteur Stockfish.
2. **Architecture maîtrisée** : Orchestration déterministe LangGraph, Stockfish UCI, base vectorielle Milvus, cache MongoDB.
3. **Gisement de données validé** : Pipeline ETL rejouable (4 sources, 477 fiches structurées, 95 FEN de référence).
4. **Performances prouvées** : 0 coup illégal sur 56 positions, latence sous 2,5 s sur GPU T4 (p95 = 2,41 s).
5. **Déploiement éprouvé** : Conteneurisation locale reproductible (2 min 09) et vitrine cloud GPU sur Hugging Face Spaces.
6. **Étude d'ingénierie livrée** : Note de cadrage, architecture MCP, faisabilité technique et modèle de coûts formalisés.

---

## Diapo 17 — Merci

**Merci pour votre attention.**

**Richard Hugou**  
IA Engineer — Cavalier Data  
*Projet OpenClassrooms × Fédération Française des Échecs*  

- **Dépôt GitHub public** : https://github.com/richardhugou/p13-agent-ia-echecs
