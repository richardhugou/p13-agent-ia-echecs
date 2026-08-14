# 12 — Modèles à appliquer et métriques associées

> Suite directe du doc 11 (fondations). Question : pour réaliser la boucle jouer → comprendre → dévier → évaluer, quels modèles faut-il, pourquoi, et comment prouve-t-on qu'ils marchent ?

## 1. Vue d'ensemble : trois « modèles », chacun à sa place

Le système n'a **pas un modèle mais trois**, chacun assigné à une étape de la boucle. Règle de conception centrale (à défendre au jury) : **le LLM n'est jamais la source de vérité** — coups = Lichess, évaluation = Stockfish, faits = corpus RAG ; le LLM met en forme et pédagogise.

| Modèle | Type | Étape de la boucle | Rôle |
|---|---|---|---|
| **Qwen3-Embedding-0.6B** | Embeddings (local, sentence-transformers) | « comprendre » | Encoder corpus FR+EN et questions dans le même espace vectoriel (1024 d) pour la recherche Milvus |
| **LLM de synthèse** (décision D1 → §3) | LLM génératif via API | « comprendre » | Rédiger la réponse pédagogique à partir des blocs factuels, citer les sources, adapter le ton à l'élève |
| **Stockfish** | Moteur d'échecs (local, GPLv3) | « dévier → évaluer » | Évaluation objective (centipawns, meilleure ligne) hors théorie |

Et un **non-modèle** décisif : le routeur théorie/moteur est **déterministe** (seuil de N parties dans la base masters), pas un choix LLM. Plus testable, plus défendable.

## 2. Justification par brique

### 2.1 Embeddings — Qwen3-Embedding-0.6B (décidé)
- **Pourquoi lui** : multilingue (corpus mixte Wikipédia FR + Wikibooks EN dans le même espace — l'argument décisif pour l'option C du corpus), léger (~0,6 Md params, tourne sur la machine 16 Go), 1024 dimensions, suggéré par le brief.
- **Écartés** : MiniLM-L6 (anglais surtout, 384 d), e5-small multilingue (moins bon), embeddings API payants (dépendance + coût inutile pour ~600 chunks ≈ 2,4 Mo de vecteurs).
- **Coût** : 0 € (local, inference CPU/MPS ponctuelle à l'ingestion + par requête).

### 2.2 LLM de synthèse — décision D1 : **Claude Haiku 4.5** (recommandé, prix vérifiés le 2026-08-14)
- **Prix confirmés** : 1 $/M tokens entrée, 5 $/M tokens sortie (le ⚠️ du doc 05 est levé).
- **Budget estimé POC** : ~500 requêtes de dev+démo × (~2 000 tokens entrée + ~500 sortie) ≈ 1 M entrée + 0,25 M sortie ≈ **2,3 $** → objectif O6 (< 5 €) tenu avec marge.
- **Pourquoi lui** : rapide (latence = critère produit, cf. doc 11 §4), bon marché, qualité FR suffisante pour de la mise en forme pédagogique (le LLM ne raisonne pas sur les échecs, il rédige à partir de faits fournis).
- **Plan B qualité** : Claude Sonnet 5 (3 $/10 $ — tarif de lancement 2 $/10 $ jusqu'au 2026-08-31) si le français de Haiku déçoit sur le gold set ; toujours dans le budget à l'échelle démo.
- **Écarté** : LLM local via Ollama (0 € mais 16 Go de RAM partagés avec Milvus+Mongo+Angular = risque démo, qualité FR moindre).

### 2.3 Moteur — Stockfish (décidé)
- Force > 3600 Elo, local, gratuit, GPLv3 (version épinglée dans le README).
- Paramètre POC : profondeur fixe (15–18) ou temps borné (~1 s/position) pour une latence prévisible — valeur exacte = paramètre mesuré.
- **Pas de fine-tuning, pas d'entraînement** : choix assumé (un POC de 2 semaines n'entraîne pas un modèle qui battrait Stockfish ni n'écrirait mieux que Wikipédia).

## 3. Les métriques, rattachées à la boucle

Chaque métrique prouve une étape de la boucle produit — c'est comme ça qu'on les raconte en soutenance.

### 3.1 Qualité du retrieval (étape « comprendre »)
| Métrique | Cible | Protocole |
|---|---|---|
| recall@5 sur gold set (25 questions) | ≥ 0,8 | Labels de pertinence au niveau ouverture/section ; runs MLflow |
| MRR | à mesurer, comparé Run A vs Run B | idem |
| Taux d'abstention correcte sur les 5 questions pièges | 100 % visé | L'agent doit dire « je ne sais pas » proprement hors corpus |
| Latence recherche vectorielle p95 | < 100 ms | Traces Milvus |

### 3.2 Fiabilité de l'agent (étapes « jouer » et « dévier ») 
| Métrique | Cible | Protocole |
|---|---|---|
| Coups illégaux proposés | **0** | Validation python-chess sur 100 % des sorties du jeu de test |
| Exactitude du routeur théorie/moteur | 100 % (déterministe) | Tests unitaires sur positions étiquetées en/hors théorie |
| Taux de citation des sources sur les réponses RAG | 100 % | Vérification automatique de la présence d'URL source |
| Latence de réponse agent p95 | < 8 s (hors 1er démarrage) | Traces LangGraph/MLflow, décomposées par nœud |

### 3.3 Coût et exploitation
| Métrique | Cible | Protocole |
|---|---|---|
| Coût LLM total (dev + démo) | < 5 € | Compteur de tokens par appel, agrégé MLflow |
| Tokens moyens par réponse | à mesurer | idem — nourrit l'étude de coûts d'industrialisation (livrable) |
| `docker compose up` → app utilisable | < 5 min machine vierge | Test d'installation fraîche |
| Recherches YouTube réelles | ~30 (quota 10 000 unités/j jamais approché) | Compteur cache MongoDB |

### 3.4 Le récit avant/après (itérations)
Deux runs MLflow comparés — **aucun chiffre de slide ne sort d'ailleurs** :
- **Run A « naïf »** : chunks 1000 tokens sans overlap, top-3.
- **Run B « amélioré »** : chunks 300–500 + overlap 15 %, top-5, filtre scalaire ECO quand l'ouverture est identifiée.
- Comparaison sur recall@5, MRR, latence → le delta constitue le slide « itérations ».

## 4. Ce qui reste ouvert
- **D1 tranché en pratique** : Haiku 4.5 par défaut, bascule Sonnet 5 si le gold set révèle des faiblesses FR — la bascule est un changement d'une variable d'environnement.
- **D2** : MLflow en service compose (reco maintenue — capture d'écran pour le slide résultats).
- **D3** : corpus mixte FR+EN (option C) — verrouillé par le choix d'embeddings multilingues.
