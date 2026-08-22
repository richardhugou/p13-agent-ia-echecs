# Présentation — Agent IA d'entraînement aux ouvertures (FFE)

> 19 diapositives, format Markdown (une diapo par section `---`). **Un tiers du deck porte sur la donnée, l'évaluation et les coûts — c'est voulu.**
> Convention : `[MESURE]` = chiffre à remplacer par la valeur réellement mesurée (runs MLflow) avant soutenance.

---

## Diapo 1 — Qui nous sommes

**Cavalier Data** — cabinet de conseil IA & data, 25 collaborateurs.

- **Moi** : IA Engineer **junior**, missionné chez le client, encadré par Alan (responsable technique, sponsor interne).
- **Le client** : Fédération Française des Échecs (FFE) — direction technique nationale (DTN) jeunes.
- **Le déclencheur** : les championnats d'Europe jeunes approchent ; la FFE veut outiller l'entraînement aux **ouvertures** de ses jeunes espoirs.
- **La commande** : un **POC en 2 semaines** qui démontre la faisabilité et la valeur d'un agent IA d'entraînement.

---

## Diapo 2 — Le contexte et le besoin

**Le problème** : > 60 000 licenciés (~60 % de jeunes), quelques **centaines** d'entraîneurs diplômés, cours particulier à 30–60 €/h. Le goulot d'étranglement, c'est l'humain.

> « Comment permettre à chaque jeune espoir de travailler ses ouvertures avec un retour de niveau "entraîneur", à la demande, sans multiplier les entraîneurs humains ? »

**Ce que l'outil devrait savoir faire — une IA qui accompagne l'élève *pendant qu'il joue* :**
1. proposer les meilleurs coups reconnus par la théorie ;
2. expliquer l'ouverture (idées, sources citées) ;
3. recommander des vidéos pédagogiques adaptées à la position ;
4. évaluer objectivement quand l'élève sort des sentiers battus.

Quatre capacités — chacune pose une question technique. La diapo suivante y répond.

---

## Diapo 3 — Le parcours d'un coup

Chaque capacité de la diapo précédente appelle une brique :

| La question qu'on se pose | La brique qu'elle appelle |
|---|---|
| « Où en est la partie ? » | Une position lisible par la machine — **le FEN**, validé à chaque coup |
| « Que jouent les grands maîtres ici, et comment ça s'appelle ? » | Une **base de parties de maîtres** — Lichess, 2 M+ parties, ouvertures nommées |
| « Et si l'élève joue un coup que la base n'a jamais vu ? » | Une **fonction d'évaluation** — Stockfish, un score pour toute position, même inédite |
| « Et pour l'expliquer à une enfant de 12 ans ? » | Des **textes sourcés + un rédacteur** — RAG et LLM |

**Les trois sources à la fois ? Oui — et à chaque coup, dans cet ordre**, parce que chaque étape fabrique l'entrée de la suivante : sans position validée, rien à chercher ; sans la réponse de la base, impossible de savoir s'il faut évaluer ; sans les faits, rien à expliquer. **Ce déroulé conditionnel répété à chaque coup, c'est ça, un agent.**

La boucle produit : jouer → comprendre → dévier → évaluer. Un seul écran : échiquier + panneau coach + vidéos.

---

## Diapo 4 — Les sources de données

| Source | Contenu | Volumétrie | Licence |
|---|---|---|---|
| Référentiel `chess-openings` (Lichess) | **3 810 ouvertures nommées** (compté le 22/08), 500 codes ECO | ~500 Ko | CC0 |
| API Lichess Opening Explorer | Stats masters (2 M+ parties) et en ligne (> 6 Md cumulées) par position | temps réel + cache | CC0 |
| Corpus « Wikichess » | **225 articles Wikipédia FR + 3 026 pages Wikibooks EN disponibles** (comptés le 22/08) → **161 retenues** (47 FR + 114 EN, manifeste signé) | sélection par ouvertures cibles | CC BY-SA |
| YouTube Data API v3 | Métadonnées vidéos (jamais les fichiers) | ~30 requêtes réelles, cache 7 j | CGU respectées |

**La clé de jointure de tout le système : le FEN** (position encodée en une ligne de texte) — la seule donnée d'entrée fournie par l'élève.

**Périmètre signé** : manifeste versionné `etl/corpus.yml` — **47 pages FR + 114 EN = 161 retenues** sur 3 251 disponibles (génération assistée, arbitrages tracés, signé le 23/08 ; règle : pas de manifeste signé, pas d'extraction).

**L'EDA (exploration des données) — chaque figure sortira d'un run rejouable** :

| Figure montrée | Ce qu'elle prouve au jury |
|---|---|
| Composition du corpus par source (bar chart) | **3 251 disponibles → 161 retenues → 477 fiches** (notebook 03, figure 01) |
| Couverture des ouvertures cibles (heatmap ECO A–E) | les 8–10 ouvertures annoncées sont réellement couvertes |
| Distribution des longueurs avant chunking (histogramme) | la taille de chunk n'est pas sortie du chapeau |
| Top-20 ouvertures : fréquence et taux de victoire, masters vs amateurs | le contexte métier — ce que les jeunes joueront vraiment |
| Profondeur théorique moyenne des lignes cibles | où finit la théorie → où Stockfish prend le relais |
| Taux de doublons / near-dup éliminés | **0 doublon exact, 1 quasi-doublon écarté (~0,2 %)** — la qualité de l'index se mesure |

---

## Diapo 5 — Les formats bruts

Ce que chaque source renvoie réellement — un extrait par source :

| Source | Format | Extrait |
|---|---|---|
| Référentiel d'ouvertures | **TSV** | `C50 ⇥ Italian Game ⇥ 1. e4 e5 2. Nf3 Nc6 3. Bc4` |
| Lichess Explorer | **JSON** | `{"opening":{"eco":"C50"},"moves":[{"uci":"e2e4","san":"e4","white":213045,…}]}` |
| Wiki d'ouvertures | **wikitext** (texte balisé) | `== Idées principales ==` · `Le fou en c4 vise le point faible f7…` |
| YouTube Data | **JSON** | `{"videoId":"a1B2c3","title":"L'Italienne expliquée","duration":"PT12M4S"}` |
| Stockfish | **texte UCI** | `info depth 16 score cp 34 pv e2e4 e7e5 g1f3` |

**Cinq formats hétérogènes → la normalisation est obligatoire.** Pivots retenus : positions en **FEN**, coups en **SAN**, textes découpés en chunks à métadonnées uniformes ; **JSON** comme format d'échange interne de l'API.

---

## Diapo 6 — Le traitement des données

**Pipeline ETL rejouable et idempotent** (upsert par hash de contenu), rapport chiffré à chaque exécution :

1. **Extract** — API MediaWiki (wikitext, jamais de scraping HTML) ; chaque document archivé avec URL source, horodatage, licence.
2. **Transform** — nettoyage wikitext ; normalisation de la notation (« Fc4 » FR ↔ « Bc4 » EN) ; calcul du FEN de référence via python-chess ; **chunking par section 300–500 tokens, overlap 15 %**, jamais une suite de coups coupée en deux ; déduplication (hash exact + similarité > 0,95).
3. **Load** — embeddings **Qwen3-Embedding-0.6B** (1024 d, multilingue FR+EN dans le même espace vectoriel — l'argument décisif du corpus mixte) → Milvus (HNSW, cosinus) ; métadonnées par chunk `{eco, opening_name, fen_ref, source_url, lang, licence…}` → filtres scalaires + attribution des sources.

**Rapport chiffré à chaque exécution** : **156 pages extraites → 477 fiches** (longueur moyenne **244 tokens** — sous-cible mesurée et assumée, notebook 03), **1 doublon écarté**.

---

## Diapo 7 — Le modèle de données

**Milvus — collection `openings_kb`** (recherche sémantique) :

| Champ | Type | Rôle |
|---|---|---|
| `pk` | int64 (auto) | clé |
| `vector` | float_vector(1024) | embedding du chunk — cosinus, index HNSW |
| `text` | varchar | le passage |
| `eco`, `opening_name`, `fen_ref`, `lang` | varchar | filtres scalaires |
| `source_url`, `licence` | varchar | attribution des sources |
| `content_hash`, `ingested_at` | varchar / int64 | idempotence, fraîcheur |

**MongoDB — base `chessagent`** (application) :

| Collection | Contenu | Particularité |
|---|---|---|
| `explorer_cache` | réponse explorer par FEN normalisé | TTL 24 h |
| `videos_cache` | métadonnées vidéos par ouverture | TTL 7 j |
| `eval_cache` | évaluation par FEN + profondeur | sans TTL (déterministe) |
| `sessions` | conversations par session | — |
| `eval_runs` | résultats du gold set par run | traçabilité |

**Clé de jointure transverse : le FEN normalisé** (+ `eco` pour l'agrégat par ouverture). Cibles : index < 10 Mo, recherche p95 < 100 ms.

---

## Diapo 8 — Les vidéos pédagogiques

**D'où elles viennent** : l'API officielle YouTube Data — uniquement des métadonnées (titre, chaîne, durée, langue), jamais les fichiers.

**Comment on les choisit** : recherche par nom d'ouverture, filtres de pertinence (durée 4–30 min, titre contenant l'ouverture, langue) ; les résultats sont conservés en base pour répondre instantanément aux positions déjà vues ; le cas « aucune vidéo trouvée » est géré proprement.

**Conformité** : affichage en lien/lecteur intégré, **aucun téléchargement** (CGU YouTube). Cette règle est aussi la limite structurante de la partie 2 (étude du système d'analyse vidéo → FEN).

---

## Diapo 9 — Les briques du système

**Règle de conception : le LLM n'est jamais la source de vérité.**

| Brique | Rôle | Entraînée par nous ? | On l'évalue par… |
|---|---|---|---|
| API Lichess (données, pas un modèle) | Coups théoriques + stats | Non — parties réelles CC0 | seuil « en théorie » testé, 0 coup illégal en sortie |
| **Stockfish** (local, > 3600 Elo) | Évaluation hors théorie | Non — moteur éprouvé | latence/profondeur mesurées, évals cachées |
| **Qwen3-Embedding-0.6B** (local) | Recherche sémantique FR+EN | Non — pré-entraîné | recall@5 ≥ 0,8 et MRR sur gold set (25 questions) |
| **LLM de synthèse** (API) | Rédige, pédagogise, cite | Non — API | sources citées 100 %, abstention sur pièges, coût |

**Nous n'entraînons aucun modèle — choix assumé** pour un POC de 2 semaines : on assemble des briques éprouvées, et notre valeur ajoutée est dans **l'orchestration** (le graphe, le routeur déterministe) et **l'évaluation systématique** de bout en bout. Ce qu'on ajuste, ce sont les paramètres du système (chunking, top-k, seuil N) — et chaque ajustement est mesuré (diapos 12–14).

Le routeur théorie/moteur est **déterministe** (seuil de parties masters), pas un choix LLM : testable à 100 %, défendable. Justification : les LLM seuls produisent des coups illégaux et des blunders — validation python-chess sur 100 % des sorties.

---

## Diapo 10 — Le choix du LLM de synthèse

| Option | Prix (entrée/sortie par M tokens) | Verdict |
|---|---|---|
| **Claude Haiku 4.5** ✅ | 1 $ / 5 $ | Rapide (latence = critère produit), FR correct, budget tenu |
| Claude Sonnet 5 | 3 $ / 15 $ (lancement : 2 $/10 $) | Plan B si le FR de Haiku déçoit sur le gold set |
| LLM local (Ollama) | 0 € | Écarté : 16 Go de RAM partagés avec Milvus + Mongo → risque démo |

Le choix est **réversible** : changer de LLM = changer une variable d'environnement, car le LLM ne fait que la mise en forme finale.

---

## Diapo 11 — L'orchestration de l'agent (LangGraph)

**État partagé** : `fen`, ouverture identifiée, `in_theory`, coups théoriques, éval moteur, chunks RAG, vidéos, réponse.

**Séquence type** (démo, 30 s) :
1. L'élève joue 3.Fc4 → le front envoie le FEN à `/agent/ask`.
2. `valider_fen` (python-chess) → `identifier_ouverture` : Partie italienne (C50).
3. **Routeur** : ≥ N parties masters → branche **théorie** : Fc5/Cf6 avec stats. (Sinon → branche **Stockfish**.)
4. RAG Milvus (filtre ECO=C50) : idées du Giuoco Piano, sources.
5. Vidéos depuis le cache → **synthèse LLM** : réponse structurée + sources citées → panneau Angular.

**Chaque nœud a un fallback** (Lichess KO → RAG+Stockfish ; YouTube KO → sans vidéos ; Milvus KO → théorie seule + avertissement) : l'agent dégrade, ne plante pas. Tout passage est tracé (nœud, durée, tokens) → MLflow.

---

## Diapo 12 — Le protocole d'évaluation

**Le gold set — un jeu d'évaluation construit à la main, versionné dans le dépôt** : 25 questions FR étiquetées —
~15 **directes** (« quelles sont les idées principales de la Sicilienne ? »), ~5 **par position** (un FEN d'Italienne → les chunks Italienne sont attendus), ~5 **pièges** (ouverture hors corpus, question hors sujet → l'agent doit s'abstenir proprement, pas inventer).

**Les métriques, définies avant de mesurer** : recall@5 (cible ≥ 0,8), MRR, taux d'abstention correcte sur les pièges, latence p95 — et les métriques système : **0 coup illégal** (validation python-chess sur 100 % des sorties), **100 % des réponses RAG sourcées**, coût par réponse.

**La discipline** : chaque run (paramètres, métriques, figures) est loggé dans MLflow — **aucun chiffre des diapos suivantes n'a d'autre origine**. Et on compare toujours à une baseline : Run A « naïf » vs Run B « amélioré » (diapo 14).

**Les mesures d'adoption** : aucune brique modèle n'entre dans le système sans son banc de mesure **versionné et rejouable** (notebook exécuté + test). Méthode : similarité cosinus entre vecteurs d'embedding, sur des paires étalonnées dont la réponse est connue (cible / lié / hors-sujet, FR et EN). Exemple mesuré : le préfixe d'instruction sur les requêtes fait passer la séparation cible/hors-sujet de 0,29 à **0,50** (notebook 02).

---

## Diapo 13 — Mesure de la performance

| Métrique | Cible | Mesuré |
|---|---|---|
| Coups illégaux proposés | **0** | **0 sur 56 coups affichés** (scénario de démo rejoué, notebook 05) |
| recall@5 (gold set 25 questions) | ≥ 0,8 | **1,0** (runs MLflow du 24/08) |
| MRR | — | **1,0** (runs MLflow du 24/08) |
| Abstention correcte sur questions pièges | 5/5 | **4/5** — le piège adjacent passe le seuil, d'où la défense en profondeur (diapo 14) |
| Citation des sources (réponses RAG) | 100 % | **100 % — garanti par construction** (les sources sont ajoutées par le code, pas par le LLM) |
| Latence recherche vectorielle p95 | < 100 ms | **7–11 ms** (à chaud) |
| Latence agent p95 | < 8 s | **6,3 s** (p50 4,2 s — synthèse LLM locale comprise ; notebook 05, figure 06) |
| Coût LLM total dev+démo | < 5 € | **0,00 € facturé** (qwen3.5:4b local ; équivalent cloud Haiku du banc complet ≈ 0,03 $) |

Tous les chiffres sortent des **runs MLflow** (params, métriques, figures) — aucun chiffre de slide n'a d'autre origine. **Capture du cahier d'expériences : `notebooks/figures/04-mlflow-runs.png`** (expérience gold-set-rag, runs A_naif / B_soigne).

---

## Diapo 14 — Les itérations

**Run A « naïf »** : chunks 1 000 tokens sans overlap, top-3, pas de filtre.
**Run B « amélioré »** : chunks 300–500 + overlap 15 %, top-5, filtre scalaire ECO quand l'ouverture est identifiée.

| | Run A « naïf » | Run B « soigné » | Lecture |
|---|---|---|---|
| recall@k | 1,0 (k=3) | 1,0 (k=5) | égalité — le gold set v1 mesure le **routage** vers la bonne ouverture, les deux le réussissent |
| MRR | 1,0 | 1,0 | idem |
| Marge d'abstention (score légitime min − piège max) | −0,10 (chevauchement) | **−0,04** (chevauchement réduit) | B sépare mieux, mais le piège « adjacent » reste dur pour un seuil seul |
| Latence recherche p50 | ~4 ms | ~5 ms | équivalentes à chaud |
| Ce que reçoit le rédacteur | fenêtres brutes de 1 000 tokens | fiches ciblées avec fil d'Ariane et sections | **la vraie différence** — qualitative, à éprouver au gold set v2 (labels fins) |

Enseignement honnête des runs : au niveau « rayon d'ouverture », les deux configurations réussissent — la mesure a montré que le gold set v1 était trop grossier pour les départager, et c'est une découverte en soi. Axes ouverts : gold set v2 à labels fins (page/section), et **défense en profondeur pour l'abstention** (seuil de score + règle d'honnêteté du prompt), le piège « domaine adjacent » ne cédant pas à un seuil seul.

---

## Diapo 15 — Déploiement du POC

```
docker compose up
```

| Service | Port | Rôle |
|---|---|---|
| frontend Angular (ngx-chessboard) | 4200 | Échiquier + panneau coach |
| backend FastAPI + LangGraph + Stockfish embarqué | 8000 | L'agent (Swagger auto pour la démo) |
| Milvus standalone (+ etcd, minio) | 19530 | Vecteurs |
| MongoDB | 27017 | Caches, sessions, runs |
| MLflow | 5001 (hôte) | Tracking — 5000 hôte squatté par AirPlay macOS |

- Exposés à l'hôte : 4200 (app), 8000 (API), 19530 (Milvus, pour le job ETL local) et 5001 (MLflow) ; volumes persistants pour les données.
- Binaire Stockfish arm64 dans l'image backend : pas de service séparé.
- **Test d'installation fraîche mesuré : app utilisable en 2 min 09** (reconstruction complète, cache de build vidé ; bibliothèque vectorielle prête à 2 min 28) — critère < 5 min tenu, protocole rejouable `tester-installation.sh`.

---

## Diapo 16 — La trajectoire d'industrialisation

Du POC local au service FFE :

- **À l'échelle du POC** : exécution locale, un utilisateur, services en conteneurs sur une machine — le FEN comme clé, le routeur déterministe, le LLM via API.
- **À l'échelle industrielle** : mêmes conteneurs sur une orchestration managée, hébergement UE (public mineur → minimisation des données, RGPD) ; Milvus en cluster, cache Lichess partagé, pool de workers Stockfish. L'architecture ne change pas, elle se redimensionne.
- **Comptes utilisateurs et suivi de progression** = V1, hors POC (assumé).
- Ingestion du corpus re-jouée en batch hebdomadaire (delta par hash de contenu).

---

## Diapo 17 — Structure de coûts

**Coût du POC** :

| Poste | Coût | Pourquoi |
|---|---|---|
| Données (Lichess, wikis, référentiel) | **0 €** | licences libres (CC0, CC BY-SA) |
| Moteur Stockfish + embeddings | **0 €** | open source, exécution locale |
| Recherche vidéos | **0 €** | quota gratuit YouTube — **~3 recherches réelles ≈ 300 unités** sur 10 000/jour, le cache 7 j absorbe le reste |
| LLM (dev + démo) | **0,00 €** — D1 révisée : qwen3.5:4b local | le poste payant a été supprimé par la mesure (campagne LLM du 22/08) |

**Coût du passage à l'échelle** : le coût marginal d'une réponse est **nul en local** ; si LLM cloud (Haiku 4.5), ≈ **0,25 centime/réponse** (≈ 1 200 tokens entrée + 250 sortie, notebook 05) → **< 0,10 €/élève/mois** à 30 questions/mois. Postes additionnels : hébergement (UE), supervision — détail dans l'étude de faisabilité jointe.

---

## Diapo 18 — Pistes d'améliorations

- **Répertoire personnalisé** : l'agent apprend les ouvertures que l'élève travaille et adapte ses recommandations (mémoire par profil).
- **Mode entraînement actif** : l'agent joue la ligne théorique contre l'élève et le corrige en direct (au lieu de commenter passivement).
- **Corpus enrichi** : passer des 8 ouvertures aux 500 codes ECO ; ajouter les parties commentées de la base FFE et les variantes absentes du wiki FR (Winawer, Partie hongroise… — périmètre réduit assumé au manifeste).
- **Analyse vidéo → FEN** (partie 2 de l'étude) : indexer les vidéos par position réelle et non par titre — architecture MCP conçue, coûts chiffrés dans l'étude jointe.
- **Évaluation continue** : élargir le gold set avec les vraies questions des élèves ; boucle de feedback entraîneurs.
- **Qualité LLM** : A/B Haiku 4.5 vs Sonnet 5 sur les explications FR, juge automatique sur le gold set.

---

## Diapo 19 — Conclusion & démo

**Ce que le POC démontre** :
- La boucle produit fonctionne : jouer → comprendre → dévier → évaluer, en moins de 8 s.
- Zéro coup illégal, sources citées, coût marginal (< 5 € de LLM pour tout le POC).
- Reproductible en une commande, mesurable de bout en bout (MLflow).

**Ce qu'on recommande à la FFE** : valider le POC avec un groupe d'élèves pilote avant les championnats d'Europe, puis industrialiser selon la trajectoire de la diapo 12.

→ **Démo en direct** : Léa joue l'Italienne… et sort de la théorie au 5e coup.

*Questions bienvenues — annexes : conformité licences, schéma d'architecture détaillé, étude de faisabilité analyse vidéo.*
