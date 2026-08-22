# Présentation — Agent IA d'entraînement aux ouvertures (FFE)

> 14 diapositives, format Markdown (une diapo par section `---`).
> Convention : `[MESURE]` = chiffre à remplacer par la valeur réellement mesurée (runs MLflow) avant soutenance.

---

## Diapo 1 — Qui nous sommes

**Cavalier Data** — cabinet de conseil IA & data, 25 collaborateurs.

- **Moi** : IA Engineer **junior**, missionné chez le client, encadré par Alan (responsable technique, sponsor interne).
- **Le client** : Fédération Française des Échecs (FFE) — direction technique nationale (DTN) jeunes.
- **Le déclencheur** : les championnats d'Europe jeunes approchent ; la FFE veut outiller l'entraînement aux **ouvertures** de ses jeunes espoirs.
- **La commande** : un **POC en 2 semaines** qui démontre la faisabilité et la valeur d'un agent IA d'entraînement.

---

## Diapo 2 — Le contexte et la solution à apporter

**Le problème** : > 60 000 licenciés (~60 % de jeunes), quelques **centaines** d'entraîneurs diplômés, cours particulier à 30–60 €/h. Le goulot d'étranglement, c'est l'humain.

> « Comment permettre à chaque jeune espoir de travailler ses ouvertures avec un retour de niveau "entraîneur", à la demande, sans multiplier les entraîneurs humains ? »

**La solution** : une IA qui accompagne l'élève **pendant qu'il joue** —
1. propose les meilleurs coups reconnus par la théorie ;
2. explique l'ouverture (idées, sources citées) ;
3. recommande des vidéos pédagogiques adaptées à la position ;
4. évalue objectivement quand l'élève sort des sentiers battus.

**La boucle produit** : jouer → comprendre → dévier → évaluer. Un seul écran : échiquier + panneau coach + vidéos.

---

## Diapo 3 — La donnée : quatre sources, toutes ouvertes

| Source | Contenu | Volumétrie | Licence |
|---|---|---|---|
| Référentiel `chess-openings` (Lichess) | ~3 500 ouvertures nommées, 500 codes ECO | ~500 Ko | CC0 |
| API Lichess Opening Explorer | Stats masters (2 M+ parties) et en ligne (> 6 Md cumulées) par position | temps réel + cache | CC0 |
| Corpus « Wikichess » | Mix Wikipédia FR (récit pédagogique) + Wikibooks EN (granularité par ligne) | ~100–150 pages retenues → `[MESURE]` | CC BY-SA |
| YouTube Data API v3 | Métadonnées vidéos (jamais les fichiers) | ~30 requêtes réelles, cache 7 j | CGU respectées |

**La clé de jointure de tout le système : le FEN** (position encodée en une ligne de texte) — la seule donnée d'entrée fournie par l'élève.

---

## Diapo 4 — Le traitement de la donnée

**Pipeline ETL rejouable et idempotent** (upsert par hash de contenu), avec rapport chiffré à chaque exécution :

1. **Extract** — API MediaWiki (wikitext, jamais de scraping HTML) ; chaque document archivé avec URL source, horodatage, licence.
2. **Transform** — nettoyage wikitext ; normalisation de la notation (« Fc4 » FR ↔ « Bc4 » EN) ; calcul du FEN de référence via python-chess ; **chunking par section 300–500 tokens, overlap 15 %**, jamais de suite de coups coupée en deux ; déduplication (hash + similarité > 0,95).
3. **Load** — embeddings **Qwen3-Embedding-0.6B** (1024 d, multilingue FR+EN dans le même espace vectoriel) → Milvus (index HNSW, métrique cosinus) ; métadonnées de filtrage (ECO, ouverture, langue, source).

**Chiffres** : `[MESURE]` pages retenues → `[MESURE]` chunks → index Milvus < 10 Mo. Caches applicatifs (Lichess 24 h, YouTube 7 j, évals sans TTL) dans MongoDB.

---

## Diapo 5 — L'acquisition des vidéos

**Contrainte** : quota YouTube Data API = 10 000 unités/jour, et une recherche coûte 100 unités.

**Stratégie** :
- ~8–10 ouvertures cibles × 2–3 requêtes = **~30 recherches réelles** sur toute la vie du POC ;
- tout le reste servi par le **cache MongoDB (TTL 7 jours)** → le quota n'est jamais approché (`[MESURE]` requêtes réellement consommées) ;
- filtres de pertinence : durée 4–30 min, titre contenant le nom de l'ouverture, langue.

**Conformité** : métadonnées uniquement — affichage en embed/lien, **aucun téléchargement** (CGU YouTube). C'est aussi la limite structurante de la partie 2 (étude du système d'analyse vidéo → FEN).

---

## Diapo 6 — Le modèle : pas un, mais trois — chacun à sa place

**Règle de conception : le LLM n'est jamais la source de vérité.**

| Modèle | Rôle | Vérité sur |
|---|---|---|
| API Lichess (données, pas un modèle) | Coups théoriques + stats | Les coups |
| **Stockfish** (local, > 3600 Elo) | Évaluation hors théorie | La position |
| **Qwen3-Embedding-0.6B** (local) | Recherche sémantique FR+EN | L'accès aux faits |
| **LLM de synthèse** (API) | Rédige, pédagogise, cite | — (jamais) |

Le routeur théorie/moteur est **déterministe** (seuil de parties masters), pas un choix LLM : testable à 100 %, défendable. Justification : les LLM seuls produisent des coups illégaux et des blunders — validation python-chess sur 100 % des sorties.

---

## Diapo 7 — Le choix du LLM de synthèse, justifié

| Option | Prix (entrée/sortie par M tokens) | Verdict |
|---|---|---|
| **Claude Haiku 4.5** ✅ | 1 $ / 5 $ | Rapide (latence = critère produit), FR correct, budget tenu |
| Claude Sonnet 5 | 3 $ / 15 $ (lancement : 2 $/10 $) | Plan B si le FR de Haiku déçoit sur le gold set |
| LLM local (Ollama) | 0 € | Écarté : 16 Go de RAM partagés avec Milvus + Mongo → risque démo |

**Budget mesurable** : ~500 requêtes dev+démo × (2 000 tokens entrée + 500 sortie) ≈ **2,3 $** → objectif < 5 € tenu avec marge (`[MESURE]` au compteur de tokens).

Le choix est **réversible** : changer de LLM = changer une variable d'environnement, car le LLM ne fait que la mise en forme finale.

---

## Diapo 8 — Le fonctionnement : l'agent LangGraph

**État partagé** : `fen`, ouverture identifiée, `in_theory`, coups théoriques, éval moteur, chunks RAG, vidéos, réponse.

**Séquence type** (démo, 30 s) :
1. L'élève joue 3.Fc4 → le front envoie le FEN à `/agent/ask`.
2. `valider_fen` (python-chess) → `identifier_ouverture` : Partie italienne (C50).
3. **Routeur** : ≥ N parties masters → branche **théorie** : Fc5/Cf6 avec stats. (Sinon → branche **Stockfish**.)
4. RAG Milvus (filtre ECO=C50) : idées du Giuoco Piano, sources.
5. Vidéos depuis le cache → **synthèse LLM** : réponse structurée + sources citées → panneau Angular.

**Chaque nœud a un fallback** (Lichess KO → RAG+Stockfish ; YouTube KO → sans vidéos ; Milvus KO → théorie seule + avertissement) : l'agent dégrade, ne plante pas. Tout passage est tracé (nœud, durée, tokens) → MLflow.

---

## Diapo 9 — Les résultats

| Métrique | Cible | Mesuré |
|---|---|---|
| Coups illégaux proposés | **0** | `[MESURE]` |
| recall@5 (gold set 25 questions) | ≥ 0,8 | `[MESURE]` |
| MRR | — | `[MESURE]` |
| Abstention correcte sur questions pièges | 5/5 | `[MESURE]` |
| Citation des sources (réponses RAG) | 100 % | `[MESURE]` |
| Latence recherche vectorielle p95 | < 100 ms | `[MESURE]` |
| Latence agent p95 | < 8 s | `[MESURE]` |
| Coût LLM total dev+démo | < 5 € | `[MESURE]` |

Tous les chiffres sortent des **runs MLflow** (params, métriques, figures) — aucun chiffre de slide n'a d'autre origine.

---

## Diapo 10 — Les itérations : ce qu'on a amélioré, preuve à l'appui

**Run A « naïf »** : chunks 1 000 tokens sans overlap, top-3, pas de filtre.
**Run B « amélioré »** : chunks 300–500 + overlap 15 %, top-5, filtre scalaire ECO quand l'ouverture est identifiée.

| | Run A | Run B | Δ |
|---|---|---|---|
| recall@5 | `[MESURE]` | `[MESURE]` | `[MESURE]` |
| MRR | `[MESURE]` | `[MESURE]` | `[MESURE]` |
| Latence p95 | `[MESURE]` | `[MESURE]` | `[MESURE]` |

Autres itérations issues des tests : ajustement du seuil N du routeur théorie/moteur (`[MESURE]` valeur retenue), calibrage profondeur/temps Stockfish pour tenir la latence, prompt de synthèse (abstention propre sur les pièges).

---

## Diapo 11 — Déploiement (1/2) : le POC, reproductible en une commande

```
docker compose up
```

| Service | Port | Rôle |
|---|---|---|
| frontend Angular (ngx-chessboard) | 4200 | Échiquier + panneau coach |
| backend FastAPI + LangGraph + Stockfish embarqué | 8000 | L'agent (Swagger auto pour la démo) |
| Milvus standalone (+ etcd, minio) | 19530 | Vecteurs |
| MongoDB | 27017 | Caches, sessions, runs |
| MLflow | 5000 | Tracking |

- Seuls 4200 et 8000 exposés à l'hôte ; volumes persistants pour les données.
- Binaire Stockfish arm64 dans l'image backend : pas de service séparé.
- **Testé sur machine vierge : app utilisable en < 5 min** (`[MESURE]`).

---

## Diapo 12 — Déploiement (2/2) : la trajectoire d'industrialisation

Du POC local au service FFE :

- **Hébergement UE** (public mineur → minimisation des données, RGPD) ; conteneurs identiques, orchestration managée (Kubernetes ou PaaS).
- **Ce qui change d'échelle** : Milvus en cluster (le corpus complet ~3 500 ouvertures reste petit), cache Lichess partagé, file de requêtes Stockfish (CPU-bound → pool de workers).
- **Ce qui ne change pas** : le FEN comme clé, le routeur déterministe, le LLM via API (coût projeté : `[MESURE]` €/élève/mois à partir des tokens mesurés au POC).
- **Comptes utilisateurs et suivi de progression** = V1, hors POC (assumé).
- Ingestion du corpus re-jouée en batch hebdomadaire (delta par hash de contenu).

---

## Diapo 13 — Pistes d'améliorations

- **Répertoire personnalisé** : l'agent apprend les ouvertures que l'élève travaille et adapte ses recommandations (mémoire par profil).
- **Mode entraînement actif** : l'agent joue la ligne théorique contre l'élève et le corrige en direct (au lieu de commenter passivement).
- **Corpus enrichi** : passer de 8–10 ouvertures aux 500 codes ECO ; ajouter les parties commentées de la base FFE.
- **Analyse vidéo → FEN** (partie 2 de l'étude) : indexer les vidéos par position réelle et non par titre — architecture MCP conçue, coûts chiffrés dans l'étude jointe.
- **Évaluation continue** : élargir le gold set avec les vraies questions des élèves ; boucle de feedback entraîneurs.
- **Qualité LLM** : A/B Haiku 4.5 vs Sonnet 5 sur les explications FR, juge automatique sur le gold set.

---

## Diapo 14 — Conclusion & démo

**Ce que le POC démontre** :
- La boucle produit fonctionne : jouer → comprendre → dévier → évaluer, en moins de 8 s.
- Zéro coup illégal, sources citées, coût marginal (< 5 € de LLM pour tout le POC).
- Reproductible en une commande, mesurable de bout en bout (MLflow).

**Ce qu'on recommande à la FFE** : valider le POC avec un groupe d'élèves pilote avant les championnats d'Europe, puis industrialiser selon la trajectoire de la diapo 12.

→ **Démo en direct** : Léa joue l'Italienne… et sort de la théorie au 5e coup.

*Questions bienvenues — annexes : conformité licences, schéma d'architecture détaillé, étude de faisabilité analyse vidéo.*
