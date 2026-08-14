# 04 — DATA : sources chiffrées, EDA, ETL, stockage, évaluation

> **C'est le document pivot.** Tout le projet se raconte à partir d'ici : quelles données, combien, quelle qualité, comment elles circulent, comment on prouve que ça marche. Sans ces chiffres, pas de soutenance.

## 1. Vue d'ensemble : 4 familles de données + 1 outil génératif

| Famille | Source | Rôle dans l'agent | Stockage |
|---|---|---|---|
| **Théorie structurée** | Référentiel d'ouvertures nommées (repo `lichess-org/chess-openings`) | Identifier l'ouverture depuis les coups/FEN | Chargé en mémoire / MongoDB |
| **Statistiques de parties** | API Lichess Opening Explorer (masters + lichess) | « Meilleurs coups issus de la théorie » + parties historiques de référence | Appels temps réel + cache MongoDB |
| **Texte encyclopédique** | « Wikichess » = Wikibooks *Chess Opening Theory* (EN) et/ou Wikipédia FR (articles d'ouvertures) — le brief accepte « toutes sources pertinentes » | Corpus RAG : idées, plans, histoire | Milvus (vecteurs) + méta |
| **Vidéos pédagogiques** | YouTube Data API v3 (métadonnées uniquement) | Recommandation de vidéos liées à la position | Cache MongoDB |
| **Évaluation (outil)** | Stockfish local (pas une donnée : un générateur d'évaluations) | Juger les positions hors théorie | Résultats cachés MongoDB |

Données **produites** par le système : sessions/conversations, traces d'exécution, runs d'évaluation, caches. Elles font partie du modèle de données (§5).

## 2. Fiches sources (chiffres, licences, risques)

### 2.1 Référentiel d'ouvertures — `lichess-org/chess-openings`
- **Format** : 5 fichiers TSV (a.tsv → e.tsv) : code ECO, nom, suite de coups (PGN/UCI).
- **Volumétrie** : **≈ 3 500 lignes d'ouvertures nommées**, couvrant les 500 codes ECO (A00–E99). ⚠️ compter exactement à l'ingestion.
- **Licence** : libre (CC0) ⚠️ confirmer sur le repo.
- **Usage POC** : table de correspondance coups→nom d'ouverture ; source de vérité pour les métadonnées `eco`, `opening_name` des chunks.
- **Risque** : quasi nul (fichier statique, ~500 Ko).

### 2.2 API Lichess Opening Explorer (`explorer.lichess.ovh`)
- **Endpoints** : `/masters` (parties de maîtres OTB, ≈ **2 M+ parties, 1952→auj.** ⚠️), `/lichess` (parties en ligne filtrables par Elo et cadence — issues d'une base publique cumulant **> 6 milliards de parties**, ≈ 100 M/mois ⚠️).
- **Réponse** : pour un FEN → ouverture identifiée (eco, name), liste des coups joués avec effectifs victoire/nulle/défaite, top parties de référence (joueurs, année, résultat) → alimente le « contexte historique ».
- **Auth** : aucune ; **rate limit souple** : en cas de HTTP 429, attendre 60 s (règle officielle Lichess).
- **Licence données** : parties Lichess en **CC0**.
- **Décisions POC** : seuil « position en théorie » = présence dans masters avec ≥ N parties (N=5 par défaut, paramètre à ajuster) ; cache MongoDB TTL 24 h ; jamais d'appel en rafale (l'UI débounce).
- **Bonus possible** : `lichess.org/api/cloud-eval` (évaluations pré-calculées des positions populaires) pour économiser du Stockfish — parking lot.

### 2.3 Corpus RAG « Wikichess »
Le brief dit « Wikichess… toutes sources pertinentes acceptées ». Trois candidats, **décision D3 à trancher** (doc 05 §6) :

| Option | Contenu | Volumétrie estimée | Langue | Licence |
|---|---|---|---|---|
| **A. Wikibooks “Chess Opening Theory”** | Une page par position/ligne, arborescence par coups | **plusieurs milliers de sous-pages** ⚠️ à compter via l'API MediaWiki | EN | CC BY-SA |
| **B. Wikipédia FR, articles d'ouvertures** | ~1 article par ouverture (Italienne, Espagnole, Sicilienne…) | **quelques centaines d'articles** dans la catégorie « Ouverture du jeu d'échecs » ⚠️ à compter | FR | CC BY-SA |
| **C. Mix (recommandé)** | B pour le récit pédagogique FR + A pour la granularité par ligne sur les 8–10 ouvertures cibles | POC : **~100–150 pages** sélectionnées | FR+EN | CC BY-SA |

- **Méthode d'inventaire exacte (à faire en T0, sans coder « le produit »)** : l'API MediaWiki (`action=query`, `list=categorymembers` pour Wikipédia ; `list=allpages` avec préfixe pour Wikibooks) donne les comptes exacts et les listes de pages → ces chiffres remplissent le slide 7.
- **Extraction** : API MediaWiki en format wikitext/plaintext (pas de scraping HTML) ; conserver l'URL et l'horodatage de chaque page.
- **Contrainte licence CC BY-SA** : **l'agent doit citer ses sources** dans les réponses RAG (attribution) — argument qualité en soutenance, pas seulement conformité.
- **Risques qualité** : pages inégales (stubs), mélange de langues, notation des coups différente (« Fc4 » FR vs « Bc4 » EN) → à traiter au nettoyage (§4).

### 2.4 YouTube Data API v3 (métadonnées seulement)
- **Quota** : **10 000 unités/jour** (gratuit). `search.list` = **100 unités** → max ~100 recherches/j ; `videos.list` = 1 unité.
- **Stratégie POC** : ~8–10 ouvertures × 2–3 requêtes = **~30 recherches réelles**, tout le reste servi par le cache MongoDB (TTL 7 j) → on ne touche jamais le quota.
- **Champs conservés** : videoId, titre, chaîne, durée, date, vignette, `embeddable`, langue.
- **Filtres pertinence** : durée 4–30 min, titre contenant le nom d'ouverture, option `videoLicense=creativeCommon` documentée (utile partie 2).
- **Conformité** : l'API ne fournit **pas** les fichiers vidéo ; on affiche des liens/embeds (iframe autorisée). **Aucun téléchargement** dans le POC — et c'est LA limite business de la partie 2 (voir livrables).

### 2.5 Stockfish (outil, pas donnée)
- Moteur open source **GPLv3**, force estimée **> 3600 Elo** ; sortie : évaluation en **centipawns** (ou mat en N), meilleure variante.
- Paramètres POC : profondeur fixe (ex. 15–18) ou temps borné (ex. 1 s/position) pour une latence prévisible — valeur exacte = paramètre mesuré en T2.
- Vigilance : binaire **arm64** dans l'image Docker (paquet distribution), version épinglée et citée dans le README (reproductibilité des évals).

## 3. Plan d'EDA (à exécuter en É3, résultats → slides 7–8)

### 3.1 Inventaire (T0)
Comptes exacts par source : nb pages/lignes disponibles vs retenues, répartition par ouverture cible et par code ECO, langues, dates de dernière édition.

### 3.2 Métriques de corpus (après extraction)
| Métrique | Pourquoi | Figure cible |
|---|---|---|
| Nb documents par source | Montrer la composition du corpus | Bar chart (slide 7) |
| Distribution des longueurs (tokens) avant chunking | Justifier la taille de chunk | Histogramme |
| Nb chunks, longueur moyenne/médiane après chunking | Dimensionner Milvus | Tableau |
| Couverture ECO des chunks | Prouver qu'on couvre les 8–10 ouvertures annoncées | Heatmap A–E (slide 7) |
| Taux de doublons/near-dup (similarité > 0,95) | Qualité d'index | Chiffre + exemples |
| % pages vides/stubs éliminées | Traçabilité du nettoyage | Chiffre |
| Top-20 ouvertures par fréquence et taux de victoire (explorer masters vs lichess) | Le « contexte data » métier du projet | Bar chart croisé |
| Profondeur théorique moyenne des lignes cibles (nb de coups dans masters) | Où finit la théorie → où commence Stockfish | Chiffre |

### 3.3 Qualité d'embedding/retrieval (fin É3, rejoué en T2)
recall@5 et MRR sur le gold set (§6), comparé entre run baseline et run amélioré ; latence de recherche Milvus (ms, p50/p95).

## 4. Pipeline ETL (règles de gestion — pas de code ici)

**Extract** → **Transform** → **Load**, script rejouable, **idempotent** (upsert par hash de contenu), avec un rapport chiffré à chaque exécution.

1. **Extract** : API MediaWiki (wikitext) + TSV ouvertures + rien d'autre. Chaque document brut archivé avec `source_url`, `retrieved_at`, `licence`.
2. **Transform** :
   - Nettoyage wikitext : suppression modèles/infobox/refs, conservation titres de sections et listes.
   - Normalisation échecs : détection des suites de coups, normalisation de la notation (SAN anglaise interne : K,Q,R,B,N), calcul du **FEN de référence** de la ligne via python-chess ; le FEN validé est la clé de jointure de tout le système.
   - **Chunking** : par section, cible **300–500 tokens**, overlap **~15 %** ; jamais couper une suite de coups en deux ; préfixer chaque chunk de son fil d'Ariane (« Sicilienne > Najdorf > 6.Fg5 »).
   - Métadonnées obligatoires par chunk : `{eco, opening_name, fen_ref, moves_san, source, source_url, lang, licence, section, ingested_at, content_hash}`.
   - Déduplication : hash exact + near-dup par similarité cosinus > 0,95.
3. **Load** :
   - **Embeddings** : Qwen3-Embedding-0.6B (sentence-transformers) — **1024 dimensions**, multilingue (FR+EN dans le même espace vectoriel : c'est l'argument décisif pour l'option C du corpus), contexte 32k. ≈ 4 Ko/vecteur → 600 chunks ≈ **2,4 Mo** de vecteurs : trivial.
   - Insertion Milvus + création index ; contrôle post-load : `count == nb chunks`, échantillon de 5 requêtes sanity-check.
4. **Rafraîchissement** : POC = ingestion unique documentée ; cible prod = re-run hebdo (delta par `content_hash`).

## 5. Schémas de stockage

### 5.1 Milvus — collection `openings_kb`
| Champ | Type | Note |
|---|---|---|
| `pk` | int64 auto | clé |
| `vector` | float_vector(1024) | **métrique cosinus**, index **HNSW** (M=16, efConstruction=200 — défauts raisonnables, à citer si question) |
| `text` | varchar | le chunk |
| `eco`, `opening_name`, `fen_ref`, `lang`, `source_url`, `section` | varchar | filtres scalaires + attribution |
| `content_hash`, `ingested_at` | varchar/int64 | idempotence, fraîcheur |

### 5.2 MongoDB — base `chessagent`
| Collection | Contenu | Particularité |
|---|---|---|
| `explorer_cache` | réponses Lichess par FEN normalisé | index TTL 24 h |
| `videos_cache` | résultats YouTube par ouverture | index TTL 7 j |
| `eval_cache` | évals Stockfish par FEN+profondeur | pas de TTL (déterministe) |
| `sessions` | historique conversation/positions par session | (option : checkpointer LangGraph) |
| `eval_runs` | résultats du gold set par run (miroir MLflow) | traçabilité |

## 6. Jeu d'évaluation « gold set » (25 questions) + protocole

- **Construction (T0, à la main)** : 25 questions FR dont ~15 « directes » (« Quelles sont les idées principales de la défense sicilienne ? »), ~5 « par position » (un FEN d'Italienne → attend des chunks Italienne), ~5 « pièges » (ouverture hors corpus, question hors sujet → attend une abstention propre).
- Pour chaque question : le(s) `opening_name`/section attendus (labels de pertinence au niveau document, pas de la phrase).
- **Métriques** : recall@5 (cible ≥ 0,8), MRR, et taux d'abstention correcte sur les pièges.
- **Baselines du récit avant/après (T2)** :
  - Run A « naïf » : chunks 1000 tokens sans overlap, top-3.
  - Run B « amélioré » : chunks 300–500 + overlap 15 %, top-5, filtres scalaires par ECO quand l'ouverture est identifiée.
  - (Annexe si temps : recherche plein-texte simple comme point de comparaison non-vectoriel.)
- Tout est loggé dans MLflow : params (modèle, chunk_size, overlap, k), métriques, figures. **Aucun chiffre de slide ne sort d'ailleurs que de ces runs.**

## 7. Chiffres récapitulatifs cibles du POC (à remplir en T0/É3 — c'est le slide 7)

| Indicateur | Attendu (ordre de grandeur) | Mesuré |
|---|---|---|
| Ouvertures couvertes | 8–10 (liste ECO figée en T0) | [MESURE] |
| Pages sources retenues | ~100–150 | [MESURE] |
| Chunks indexés | ~300–600 | [MESURE] |
| Longueur moyenne chunk | 300–500 tokens | [MESURE] |
| Dimensions vecteur | 1024 | 1024 |
| Taille index Milvus | < 10 Mo | [MESURE] |
| Doublons éliminés | à mesurer | [MESURE] |
| recall@5 gold set | ≥ 0,8 | [MESURE] |
| Latence recherche vectorielle p95 | < 100 ms | [MESURE] |
| Recherches YouTube réelles (total) | ~30 | [MESURE] |

## 8. Conformité & licences (slide annexe A5)
- **Lichess (parties, explorer)** : CC0 — aucun problème.
- **Wikibooks/Wikipédia** : CC BY-SA → **attribution obligatoire** : l'agent affiche ses sources (URL) sous chaque réponse RAG.
- **YouTube** : métadonnées via API + embed/lien uniquement ; pas de téléchargement (CGU).
- **Stockfish** : GPLv3 — usage serveur OK ; citer la version.
- **RGPD** : POC sans compte ni donnée personnelle ; sessions anonymes locales. Public cible mineur → argument pour héberger en UE et minimiser les données en V1 (question jury probable, doc 07).
