# Présentation — Agent IA d'entraînement aux ouvertures (FFE)

> **Structure finale (15 diapositives)** : Problème → Produit → Parcours → Architecture → Orchestration → Recherche sémantique → Données → Protocole de mesure → Résultats → Choix techniques → Déploiement et coûts → Perspective vidéo → Résumé du POC → Merci.
> *Aucune annexe dans le deck : les justifications et bancs détaillés vivent dans les livrables d'ingénierie joints.*

---

## Diapo 1 — Titre

**Un coach IA pour les ouvertures d'échecs**
Preuve de concept pour la Fédération Française des Échecs.
Richard Hugou, IA Engineer, Cavalier Data.
Soutenance — Août 2026.

---

## Diapo 2 — Besoin et contexte

La FFE prépare ses jeunes espoirs aux championnats d'Europe. **60 000 licenciés, ~60 % de jeunes, quelques centaines d'entraîneurs** : le goulot d'étranglement est humain.

> Exemple de Léa, 12 ans : elle prépare son tournoi et souhaite travailler ses ouvertures le soir. Son entraîneur n'est pas disponible. La mission : **un POC opérationnel** pour l'accompagner en direct pendant qu'elle joue.

**Les 4 capacités attendues de l'agent** :
1. Proposer les coups recommandés par la théorie des maîtres.
2. Expliquer les plans stratégiques en citant des sources documentaires.
3. Recommander des vidéos pédagogiques ciblées.
4. Évaluer objectivement la position dès que l'élève sort des sentiers théoriques.

---

## Diapo 3 — Démonstration

**Vidéo de démonstration en conditions réelles (~45 s)** :
- Parcours complet : choix du camp (Blancs), travail sur l'Italienne (3.Fc4), déclenchement des conseils sourcés, sortie de théorie (4.g4?!), bascule moteur Stockfish.
- *Lien vidéo Loom : https://www.loom.com/share/821b854d6676475bb82cb1830448a3c3*

Visuels :
- Capture d'écran réelle de l'application (`rendu/captures/ui-conseils-italienne.png`).
- QR Code vectoriel menant vers la démonstration en direct.

---

## Diapo 4 — Parcours utilisateur

Scénario nominal de l'élève (les Blancs sur la Partie Italienne) :

1. **Orientation du plateau** : choix du camp (« Je joue les Blancs »).
2. **Choix de l'ouverture** : sélection de l'Italienne (parmi les 8 ouvertures du manifeste FFE) ou saisie libre.
3. **Réplique adverse automatique** : l'agent joue automatiquement la réponse des maîtres Lichess la plus fréquente.
4. **Détection hors théorie** : signalement immédiat dès qu'un coup sort des parties de référence.
5. **Conseil à la demande (« Demander à Chessbot »)** : coups théoriques, flèches tactiques sur l'échiquier, synthèse sourcée, vidéo associée.
6. **Évaluation objective** : sur coup hors théorie, passage automatique au moteur Stockfish avec score chiffré.

*Principe directeur : les faits sont extraits des moteurs spécialisés, le LLM intervient uniquement pour la formulation.*

---

## Diapo 5 — Architecture

```
                                 ┌───────────────┐
                                 │   MONGODB     │  (État applicatif & cache :
                                 │ cache/mémoire │   requêtes Lichess, eval Stockfish, vidéos)
                                 └───────▲───────┘
                                         ┆ (lecture / écriture)
      Navigateur (Élève) ──► FRONT ANGULAR (Échiquier responsive & panneau coach)
                                 ↕ position FEN / réponse
                           FASTAPI + LANGGRAPH (Orchestration & routage)
                ┌────────────────────────┼────────────────────────┐
                ▼                        ▼                        ▼
        LICHESS EXPLORER             STOCKFISH               MILVUS
      (Théorie & statistiques)      (Moteur UCI)       (Base vectorielle)
                                                                  ▼
                                                      LLM LOCAL / CLOUD (Ollama)
                                                                  ▼
                                                           RÉPONSE SOURCÉE
```

- **Clé pivot FEN** : la notation standard de position circule de manière uniforme entre toutes les briques.
- **Milvus (Connaissance)** : fiches documentaires vectorisées, recherche sémantique restreinte au rayon d'ouverture.
- **MongoDB (État applicatif & Cache)** : persistance transverse des requêtes Lichess, évaluations Stockfish et métadonnées vidéos.

---

## Diapo 6 — Orchestration

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

- **Routage déterministe** : aucun choix de coup n'est confié au LLM.
- **Dégradation gracieuse** : chaque nœud dispose d'un mécanisme de repli testé et validé.

---

## Diapo 7 — Recherche sémantique

**Problématique** : retrouver les concepts stratégiques sans correspondance exacte de mots-clés (ex : *« pourquoi le fou vise f7 ? »* -> fiche *Giuoco Piano*).

```
Question élève ──► Embedding (1024d) ──► Cosinus HNSW (Milvus) ──► 5 fiches pertinentes ──► LLM
```

- **Espace vectoriel unifié** : modèle multilingue (`qwen3-embedding:0.6b`, 1024 dimensions) alignant les fiches FR et EN.
- **Filtrage par rayon** : recherche restreinte strictement à l'ouverture active pour empêcher la récupération de sources hors périmètre.
- **Performances mesurées** : recherche en **7 à 11 ms** ; séparation sémantique cible / hors-sujet portée de 0,29 à **0,50**.

---

## Diapo 8 — Données

**4 sources documentaires complémentaires** :
- **Référentiel des ouvertures** : nomenclature et codes ECO officiels.
- **Lichess Explorer** : base de 2 M+ parties de maîtres et statistiques de victoires.
- **Wikipédia / Wikibooks** : corpus encyclopédique structuré en fiches de 300 à 500 mots.
- **YouTube** : métadonnées et horodatages de vidéos pédagogiques.

**Pipeline ETL rejouable et idempotent** :
`Extraction (manifeste signé) -> Nettoyage -> Fiches structurées -> Vecteurs 1024d -> Milvus`

**Corpus final validé** :
**3 251 pages disponibles -> 161 retenues -> 477 fiches** (95 positions FEN de référence, 0 échec de calcul).

---

## Diapo 9 — Protocole de mesure

**1. Scénarios évalués** :
- Ligne théorique nominale (Italienne).
- Sortie de théorie sur coup douteux (`4.g4?!`).
- Questions ouvertes posées à l'agent.

**2. Bancs d'évaluation automatisés** :
- **Validité des coups** : 56 positions testées de bout en bout via `python-chess`.
- **Qualité RAG** : Gold Set de 25 questions étalonnées sous MLflow.
- **Abstention** : 5 requêtes pièges hors domaine (ex : Défense Scandinave non signée).
- **Latence** : 12 requêtes (4 positions $\times$ 3 répétitions) avec horodatage haute précision.

**3. Environnements comparés** :
- **Local** : CPU hôte avec LLM Ollama local.
- **Cloud** : Hugging Face Space avec GPU NVIDIA T4 (16 Go VRAM) et Ollama CUDA.

*Toutes les mesures sont reproductibles via les notebooks et scripts du dépôt.*

---

## Diapo 10 — Résultats et performances

| Indicateur clé | Objectif | Résultat mesuré |
|---|---|---|
| Coups illégaux en sortie | 0 | **0 sur 56 coups testés** |
| Recall@5 (Gold Set 25 questions) | >= 0,80 | **1,0** (runs tracés sous MLflow) |
| Abstention sur questions pièges | 5 / 5 | **5 / 5** (filtrage par rayon d'ouverture) |
| Réponses avec sources valides | 100 % | **100 %** (garanti par le pipeline) |
| Recherche vectorielle Milvus | < 100 ms | **7 à 11 ms** (p95) |
| Latence avec LLM (Cloud GPU T4) | p95 < 8 s | **1,81 s** (p50) / **2,41 s** (p95) |
| Latence avec LLM (Local CPU) | p95 < 8 s | **2,69 s** (p50) / **6,35 s** (p95) |
| Coût d'API LLM | 0 € | **0,00 €** (modèles open source sur GPU T4 / local) |

Visuel : graphique des latences réelles (`notebooks/figures/06-latences-agent.png`).

---

## Diapo 11 — Choix techniques

| Choix d'architecture | Alternative évaluée | Décision et justification technique |
|---|---|---|
| **Modèle LLM open source** | API managée payante | Modèle Qwen open source : 0 € d'API, p95 2,41 s sur T4 GPU, souveraineté des données |
| **Structure documentaire** | Chunks bruts 1 000 tokens | Fiches 300–500 tokens avec fil d'Ariane, section et métadonnées scalaires (ECO, FEN) |
| **Gestion du hors-sujet** | Seuil de similarité seul | Filtrage déterministe par rayon d'ouverture + seuil filet à 0,58 (5/5 pièges bloqués) |

*Chaque choix technique repose sur une comparaison objective et des mesures reproductibles.*

---

## Diapo 12 — Déploiement et coûts

### 1. Environnement Local (POC complet)
- **Socle** : 7 conteneurs Docker (`docker compose up` / `./demarrer.sh`).
- **Initialisation** : Démarrage complet mesuré en **2 min 09**.
- **Coût d'infrastructure** : **0,00 €** (exécution locale sur l'hôte).

### 2. Environnement Cloud (Déploiement complet GPU T4)
- **Plateforme** : Hugging Face Spaces (mono-conteneur Docker avec Ollama CUDA + T4 16 Go).
- **Intégration continue** : CI/CD GitHub Actions (`git push main -> déploiement automatique`).
- **Coût d'infrastructure** : **0,40 $/h** (facturé à l'usage pendant l'exécution).
- **Accès public** : https://trikwi-p13-agent-echecs.hf.space

---

## Diapo 13 — Perspective vidéo

**Objectif** : enrichir la recommandation en pointant directement vers le **timestamp exact** où la position de l'élève est expliquée dans la vidéo.

```
Flux vidéo ──► Extraction d'images ──► Détection échiquier ──► Position FEN ──► Agent existant
```

- **Valeur ajoutée** : recommandation vidéo à la position d'échiquier près, au lieu d'une recommandation globale par nom d'ouverture.
- **Statut** : Étude d'ingénierie formalisée (faisabilité, architecture MCP, modèle de coûts) ; développement hors périmètre du POC.

---

## Diapo 14 — Résumé du POC

- **Agent fonctionnel** : Reconnaissance théorique immédiate, bascule moteur sur sortie de théorie, explications sourcées.
- **Architecture maîtrisée** : Orchestration déterministe LangGraph, Stockfish UCI, Milvus vectoriel, cache MongoDB.
- **Performances validées** : Zéro coup illégal sur 56 positions, latence sous 2,5 s sur GPU T4 (p95 = 2,41 s).
- **Déploiement éprouvé** : Conteneurisation locale reproductible (2 min 09) et déploiement cloud GPU sur Hugging Face Spaces.
- **Dépassement du périmètre (Bonus)** : Mode Robot Stockfish avec Elo réglable (1200 à 2200) et mode saisie libre avec relais.

**-> Place à la démonstration en direct et aux échanges.**

---

## Diapo 15 — Merci

**Merci pour votre attention.**

**Richard Hugou**  
IA Engineer — Cavalier Data  
*Projet OpenClassrooms × Fédération Française des Échecs*  
Dépôt : https://github.com/richardhugou/p13-agent-ia-echecs  
Vitrine : https://trikwi-p13-agent-echecs.hf.space
