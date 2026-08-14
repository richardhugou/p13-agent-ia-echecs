# 07 — Questions probables du jury (et réponses modèles)

> Réponses volontairement courtes (2–4 phrases) : la structure est « décision → justification → limite assumée ». S'entraîner à les dire à voix haute.

## A. Données & licences

**A1. D'où viennent vos données et avez-vous le droit de les utiliser ?**
Quatre sources : référentiel d'ouvertures et statistiques de parties Lichess (CC0), corpus encyclopédique Wikibooks/Wikipédia (CC BY-SA, d'où l'attribution des sources dans chaque réponse de l'agent), métadonnées YouTube via l'API officielle (embed/liens seulement, pas de téléchargement), et Stockfish (GPLv3) comme outil d'évaluation. Le tableau licences est en annexe.

**A2. Volumétrie : vous avez indexé quoi, exactement ?**
[MESURE] pages sélectionnées sur 8–10 ouvertures cibles → [MESURE] chunks de 300–500 tokens, vecteurs 1024 d, soit [MESURE] Mo dans Milvus. J'ai volontairement un petit corpus propre plutôt qu'un gros corpus sale : la qualité du RAG dépend d'abord de la qualité d'ingestion.

**A3. Comment avez-vous vérifié la qualité des données ?**
Rapport EDA systématique à l'ingestion : comptes par source, distribution des longueurs, couverture ECO, déduplication (hash + near-dup cosinus > 0,95), pages vides éliminées. Les chiffres sont dans le slide 7 et re-générés à chaque run ETL.

**A4. Pourquoi ne pas avoir ingéré les dumps complets de Lichess (des milliards de parties) ?**
Parce que l'explorer expose déjà l'agrégat dont j'ai besoin (coups joués + stats + parties de référence par position). Ré-agréger 6 milliards de parties pour un POC de 2 semaines serait du gaspillage ; c'est une piste V1 si on veut des stats par tranche Elo fines.

**A5. Que se passe-t-il si une question sort du corpus ?**
C'est un cas testé du gold set (« questions pièges ») : le prompt impose de répondre uniquement depuis le contexte fourni et l'agent répond « je n'ai pas cette information » plutôt que d'halluciner. Taux d'abstention correcte : [MESURE].

**A6. RGPD — vos utilisateurs sont des mineurs.**
Le POC ne collecte aucune donnée personnelle : pas de compte, sessions anonymes, tout tourne en local. Pour une V1 FFE : hébergement UE, minimisation, consentement parental — c'est identifié dans la roadmap, pas traité dans le POC.

## B. RAG & embeddings

**B1. Pourquoi Qwen3-Embedding-0.6B ?**
Corpus mixte FR/EN → il me faut un modèle multilingue qui projette les deux langues dans le même espace ; 0,6 Md de paramètres tourne en CPU dans le conteneur ; 1024 dimensions restent légères (~4 Ko/vecteur). Alternative testable en un paramètre grâce à l'ETL rejouable.

**B2. Justifiez votre chunking.**
Par section, 300–500 tokens, ~15 % d'overlap, sans jamais couper une suite de coups, avec fil d'Ariane préfixé. Mesuré contre un chunking naïf 1000 tokens : recall@5 [MESURE] vs [MESURE] — c'est le run A/run B de MLflow.

**B3. Cosinus ou L2 ? Quel index ?**
Cosinus (embeddings de phrases ~normalisés, c'est la similarité sémantique standard) ; index HNSW (M=16, efConstruction=200) : rappel élevé et latence en millisecondes à notre échelle. À 600 vecteurs, même une recherche exhaustive marcherait — HNSW prépare la suite.

**B4. Comment évaluez-vous le RAG ?**
Gold set de 25 questions étiquetées (directes, par position, pièges) ; recall@5 ≥ 0,8 visé et MRR, mesurés à chaque run et loggés MLflow. L'éval est dans le pipeline, pas faite une fois à la main.

**B5. Pourquoi pas de reranker / hybrid search ?**
Périmètre 2 semaines : je maximise la valeur démontrable. Rerank cross-encoder et BM25+vecteurs sont dans le parking lot avec un protocole d'éval déjà prêt pour mesurer leur apport.

**B6. RAG vs fine-tuning : pourquoi pas spécialiser le modèle ?**
Le fine-tuning fige la connaissance dans les poids : coûteux, dur à mettre à jour, invérifiable. Le RAG met à jour par ré-indexation, cite ses sources et coûte quasi zéro — c'est le bon outil pour de la connaissance factuelle évolutive.

**B7. Votre recherche vectorielle renvoie du hors-sujet, que faites-vous ?**
D'abord le diagnostic par les données (quels chunks remontent, quel score), puis dans l'ordre : filtres scalaires par ECO quand l'ouverture est identifiée, chunking revu, requête enrichie (nom d'ouverture + question). Chaque tentative = un run MLflow comparé.

## C. Agent & LangGraph

**C1. Pourquoi LangGraph plutôt qu'une simple chaîne ?**
Parce que le besoin est un branchement d'état explicite : théorie → Lichess, hors-théorie → Stockfish, puis convergence vers RAG/vidéos/synthèse. Un graphe avec arêtes conditionnelles rend ce routage testable et lisible ; une chaîne linéaire l'aurait caché dans du code.

**C2. Le LLM décide-t-il des coups ?**
Jamais. La compétition Kaggle des LLM aux échecs l'a montré : sans outils, coups illégaux et niveau faible. Chez moi les coups viennent de la théorie (Lichess), l'évaluation de Stockfish ; le LLM orchestre la réponse pédagogique. Zéro coup illégal sur le jeu de test (validation python-chess systématique).

**C3. Votre routeur est un seuil, pas un LLM. Pourquoi ?**
Déterminisme : même position → même chemin → testable et explicable au client. Je réserve le LLM aux tâches où il est irremplaçable (comprendre une question libre, rédiger).

**C4. Que se passe-t-il si Lichess/YouTube/Milvus tombe ?**
Chaque nœud a un fallback : l'agent dégrade sa réponse (sans vidéos, ou théorie seule) et le signale, il ne plante pas. Timeouts explicites, backoff 60 s sur 429, caches MongoDB — testé en coupant les services un par un.

**C5. Gérez-vous la mémoire de conversation ?**
Sessions dans MongoDB (historique de positions/questions) ; le checkpointing natif LangGraph→MongoDB est identifié comme évolution directe.

**C6. Comment déboguez-vous l'agent ?**
Traces par nœud (durée, entrées/sorties, tokens) via autolog vers MLflow : pour toute réponse je peux rejouer le chemin exact emprunté dans le graphe.

## D. APIs & robustesse

**D1. Les limites de l'API Lichess ?**
Pas de quota publié pour l'explorer mais une règle : si 429, attendre 60 s. D'où cache 24 h par FEN, débounce côté UI, et jamais d'appels en rafale.

**D2. Le quota YouTube (10 000 unités/j, 100/recherche) ?**
~30 recherches réelles pour tout le POC grâce au cache 7 j par ouverture ; en cas de quota mort, des fixtures prennent le relais — la démo ne dépend jamais du quota.

**D3. Pourquoi le FEN en query param et pas en path comme dans l'énoncé ?**
Un FEN contient espaces et slashs : en path il faut du double-encodage fragile. Je documente l'alias path pour coller à l'énoncé, mais le contrat propre est en query/body.

**D4. Stockfish : quelle profondeur, quel compromis ?**
Temps borné (~1 s/position, profondeur ~15–18 [MESURE]) : latence prévisible pour l'UX, précision largement suffisante pour du pédagogique. Paramètre exposé en variable d'environnement, valeurs mesurées en annexe.

**D5. Combien coûte une interaction ?**
[MESURE] € (tokens comptés dans les traces) ; ordre de grandeur attendu ~0,005 €. Budget LLM total du POC < 5 €.

## E. Infra & Docker

**E1. Racontez votre docker compose.**
Six services (front, API+Stockfish, Milvus+etcd+minio, Mongo, MLflow), réseau interne, volumes persistants testés par destruction/recréation, healthchecks avec `depends_on: service_healthy` — indispensable, Milvus démarre lentement. Installation fraîche chronométrée : < 5 min.

**E2. Pourquoi pas de GPU ?**
Docker sur macOS n'expose pas le GPU. Conséquence assumée : embeddings CPU (corpus minuscule) et LLM via API. C'est documenté comme contrainte matérielle, avec l'option ETL sur l'hôte si besoin.

**E3. Où sont vos secrets ?**
`.env` non commité + `.env.example` complet ; aucune clé en dur ; les conteneurs lisent l'environnement. (Réponse à donner en montrant le `.gitignore`.)

**E4. Votre machine tient-elle la stack ?**
16 Go RAM : Docker plafonné à 8 Go, stack mesurée à [MESURE] Go en e2e. C'est la contrainte n°1 identifiée dès le cadrage — et la raison du LLM API plutôt que local.

## F. Résultats & partie 2

**F1. Vos résultats en une phrase ?**
Sur le gold set : recall@5 [MESURE] (baseline [MESURE]), 0 coup illégal, latence p95 [MESURE] s, coût [MESURE] €/interaction — tout est reproductible via MLflow.

**F2. Pourquoi MCP dans la partie 2 alors qu'une API REST suffirait ?**
MCP standardise l'exposition d'outils aux agents : les serveurs (vision, chess-tools, base de connaissances) deviennent réutilisables par n'importe quel agent de la fédération, indépendamment du framework. Et j'assume la nuance : l'ingestion vidéo massive reste un pipeline batch classique ; MCP sert l'interrogation et le pilotage par l'agent.

**F3. La plus grosse limite de votre système d'analyse vidéo ?**
Juridique avant d'être technique : les CGU YouTube interdisent le téléchargement des vidéos. D'où les alternatives chiffrées : vidéos sous licence Creative Commons, transcripts plutôt que frames, ou contenus produits/licenciés par la FFE.

**F4. Détection d'échiquier : quelle précision espérer ?**
Deux mondes : échiquiers 2D de screencast (majorité des vidéos pédagogiques) → vision classique, précision très élevée ; plateaux 3D filmés → il faut un modèle entraîné (datasets type ChessReD), précision par case élevée mais erreurs plateau non négligeables ⚠️ chiffres exacts sourcés dans la note. Le POC d'analyse commencerait par le cas 2D.

**F5. Vos coûts partie 2 sont-ils crédibles ?**
Ce sont des hypothèses posées (volume, durée, échantillonnage) × des prix unitaires publics (stockage, CPU/GPU, transcription, LLM), avec 3 scénarios et une analyse de sensibilité. La méthode est plus importante que le chiffre : tout est recalculable en changeant une hypothèse.

## G. Méthode & recul

**G1. Qu'est-ce qui a été le plus dur ?**
Réponse honnête à préparer après coup — bons candidats : orchestration des healthchecks compose, qualité du corpus, jonglage quotas.

**G2. Avec 2 mois de plus ?**
Hybrid search + reranker mesurés, checkpointing MongoDB, mode quiz pédagogique, éval continue automatisée, déploiement cloud UE + auth, et le MVP transcripts de la partie 2.

**G3. Qu'avez-vous appris sur les agents ?**
Que la fiabilité vient de la répartition des rôles : sources de vérité externes, routage déterministe, LLM confiné à la compréhension et à la rédaction — et que sans éval chiffrée, on ne sait rien.
