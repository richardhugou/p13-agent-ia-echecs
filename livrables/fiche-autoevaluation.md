# Fiche d'autoévaluation — « Mettez en place un agent IA »

> Cochée **uniquement sur le démontrable** (test, capture, trace). Chaque case renvoie à sa preuve dans le dépôt : code, tests, notebooks exécutés, mesures. Rendu : août 2026 — Richard Hugou.

## Compétence : Étudier un modèle d'apprentissage en lien avec des besoins identifiés

### Livrable 1 — Système développé avec LangGraph, FastAPI, Milvus et MongoDB

**Agent & code**
- [x] J'ai correctement structuré le graphe LangGraph — *preuve : `backend/graph/` (valider → identifier → routeur déterministe → théorie/moteur → RAG → vidéos → synthèse) + schéma diapo 8 + doc technique §2*
- [x] Mon agent peut traiter une position FEN et déterminer la source d'information appropriée — *preuve : notebook 05 (scénario rejoué : en théorie → Lichess ; 4.g4?! → Stockfish −1,47) + tests e2e des 4 trajets*
- [x] Mon code respecte les bonnes pratiques Python — *ruff lint + format en CI, typage, 65 tests verts*
- [x] J'ai séparé la logique métier de la logique d'API — *`backend/services/` vs `backend/api.py` (item vérifié par la structure du dépôt)*

**Données & RAG**
- [x] Mes données Wikichess sont preprocessées et chunkées sans erreur — *preuve : rapport ETL (156 pages → 477 fiches, 95 FEN / 0 échec, 1 doublon écarté) + notebook 03*
- [x] Mes embeddings sont générés avec un modèle approprié et stockés dans Milvus — *modèle multilingue FR+EN mesuré (notebook 02 : séparation 0,29 → 0,50 avec préfixe d'instruction), collection HNSW/cosinus*
- [x] Ma recherche vectorielle retourne des résultats pertinents pour les ouvertures — *preuve : recall@5 = 1,0 · MRR = 1,0 sur gold set figé (runs MLflow) · p95 7–11 ms*
- [x] Ma base vectorielle est connectée au workflow LangGraph — *nœud `contexte_rag` + règle des rayons signés (5/5 pièges bloqués, tests garde-fous)*
- [x] Je suis satisfait de la pertinence des réponses de l'agent — *Notes : cas limites documentés (gold set v1 trop grossier → v2 en axe ; abstention honnête vérifiée de bout en bout)*

**Intégrations externes**
- [x] Mon intégration avec l'API Lichess fonctionne et retourne les coups théoriques — *cache 24 h + backoff 429 + erreurs typées, vérifié en réel (C50, 48 726 parties)*
- [x] J'ai correctement intégré Stockfish : il évalue les positions — *profondeur/temps par variables d'env, cache par FEN sans TTL, embarqué arm64*
- [x] Mon API YouTube retourne des vidéos pertinentes — *filtres durée/titre + cache 7 j + cas « aucune vidéo » géré, vérifié en réel (3 vidéos FR)*
- [x] Mon agent choisit des outils pertinents — *preuve : routeur déterministe testé aux bornes (4/5/6 parties) + traces notebook 05*
- [x] J'ai géré les timeouts et erreurs d'API — *erreurs typées (429 → Retry-After, 401 actionnable), plan B par nœud observé en conditions réelles (Milvus en recharge)*

**Docker**
- [x] Mon docker-compose est fonctionnel : tous les services démarrent — *7 conteneurs, healthchecks, `./demarrer.sh`*
- [x] La communication entre les services fonctionne — *vérifié e2e en conteneurs (agent/ask complet : 5 fiches + 3 vidéos + 0 erreur)*
- [x] J'ai configuré les volumes persistants — *preuve : conteneurs et images détruits/recréés pendant le test d'installation, données intactes*
- [x] J'ai intégré les variables d'environnement dans la configuration — *`.env.example` complet, secrets jamais commités*
- [x] Mon application est accessible depuis l'extérieur — *4200 (app), 8000 (API/Swagger), 5001 (MLflow) — installation fraîche mesurée : 2 min 09 (`tester-installation.sh`)*

**Interface Angular**
- [x] Mon échiquier est intégré (ngx-chessboard) — *starter OC + lib locale compilée en CI*
- [x] Les positions FEN sont synchronisées — *board → backend (Lancer l'IA) et backend → board (sélecteur d'ouverture : setFEN)*
- [x] Les recommandations de l'agent sont pertinentes — *panneau coups avec stats et notation FR « Fc5 (fou f8) », explication sourcée, vidéos, éval moteur*
- [x] Elle gère les états de chargement et les erreurs — *spinner, message backend injoignable, notes d'incident en mode dégradé*
- [x] Je suis satisfait de l'expérience utilisateur — *Notes : retours d'un testeur externe (le mentor) intégrés — choix du camp, coups adverses corrigeables, bouton « Lancer l'IA », sélecteur d'ouverture*

### Livrable 2 — Note détaillée sur les bénéfices et limites

- [x] J'ai identifié les bénéfices du système d'analyse vidéo — *note §3, chacun avec un indicateur chiffrable (×50-100 vs indexation humaine)*
- [x] J'ai évalué les limites techniques et business — *note §4, la juridique en premier (CGU) avec requalification et mitigations ; 2 régimes de vision 2D/3D*
- [x] Mon architecture est cohérente et réalisable — *schéma MCP (4 serveurs + pipeline batch assumé) + décisions d'architecture défendues*
- [x] Mes estimations de coûts sont pertinentes — *hypothèses × prix unitaires, build 15-20 k€ MVP, opex 3 scénarios, sensibilité (étude jointe)*
- [x] J'ai identifié des alternatives et réfléchi à une roadmap de développement — *2 alternatives (transcripts d'abord ; corpus fermé FFE) + roadmap MVP/V1/V2 avec critères go/no-go chiffrés*

### Soutenance
- [x] Je suis en capacité de présenter mes livrables et d'en démontrer la pertinence — *deck v3 (13 diapos + annexes) + notes minutées + vidéo de démo enregistrée + démo live répétée (caches chauds) + Q&A préparé (docs/07)*

## Notes libres pour la session mentor
- **Décisions prises sur mesures, à présenter** : D1 (LLM local — révisée par la campagne du 22/08), D2 (MLflow en compose — réalisée), D3 (corpus mixte FR+EN — faite de facto, à confirmer formellement).
- **La leçon gold set v1** (recall 1,0 partout = étalon trop grossier) présentée comme démarche : savoir ce que sa mesure mesure ; v2 à labels fins en axe.
- **Écart assumé** : FEN en query param (vs `/moves/{fen}` de l'énoncé) — documenté doc 05 §3.
