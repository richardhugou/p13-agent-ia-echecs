# [LIVRABLE] Fiche d'autoévaluation — « Mettez en place un agent IA »

> Transcription fidèle de la fiche OC en cases à cocher. **À cocher uniquement quand c'est démontrable** (test, capture, trace). La colonne Notes = points à discuter avec le mentor. Les renvois indiquent où la preuve sera produite.

## Compétence : Étudier un modèle d'apprentissage en lien avec des besoins identifiés

### Livrable 1 — Système développé avec LangGraph, FastAPI, Milvus et MongoDB

**Agent & code**
- [ ] J'ai correctement structuré le graphe LangGraph — *preuve : schéma doc 05 §2 + traces d'exécution*
- [ ] Mon agent peut traiter une position FEN et déterminer la source d'information appropriée — *preuve : 5 positions de test, chemins vérifiés (gate T1)*
- [ ] Mon code respecte les bonnes pratiques Python — *Notes : lint/format/typage, structure services*
- [ ] J'ai séparé la logique métier de la logique d'API — *modules services vs routes*

**Données & RAG**
- [ ] Mes données Wikichess sont preprocessées et chunkées sans erreur — *preuve : rapport ETL chiffré (doc 04 §4)*
- [ ] Mes embeddings sont générés avec un modèle approprié et stockés dans Milvus — *modèle multilingue justifié (doc 05 §5)*
- [ ] Ma recherche vectorielle retourne des résultats pertinents pour les ouvertures — *preuve : recall@5 = [MESURE] sur gold set*
- [ ] Ma base vectorielle est connectée au workflow LangGraph — *nœud contexte_rag tracé*
- [ ] Je suis satisfait de la pertinence des réponses de l'agent — *Notes : cas limites observés*

**Intégrations externes**
- [ ] Mon intégration avec l'API Lichess fonctionne et retourne les coups théoriques — *+ cache 24 h + backoff 429*
- [ ] J'ai correctement intégré Stockfish : il évalue les positions — *profondeur/temps documentés, cache par FEN*
- [ ] Mon API YouTube retourne des vidéos pertinentes — *filtres + cache 7 j + cas « aucune vidéo »*
- [ ] Mon agent choisit des outils pertinents — *preuve : traces des chemins théorie vs moteur*
- [ ] J'ai géré les timeouts et erreurs d'API — *preuve : test en coupant chaque service (doc 07 C4)*

**Docker**
- [ ] Mon docker-compose est fonctionnel : tous les services démarrent — *healthchecks + depends_on*
- [ ] La communication entre les services fonctionne — *test e2e*
- [ ] J'ai configuré les volumes persistants — *preuve : down/up sans perte (gate É6)*
- [ ] J'ai intégré les variables d'environnement dans la configuration — *.env.example complet*
- [ ] Mon application est accessible depuis l'extérieur — *ports exposés documentés*

**Interface Angular**
- [ ] Mon échiquier est intégré (ngx-chessboard)
- [ ] Les positions FEN sont synchronisées — *board ↔ backend dans les deux sens*
- [ ] Les recommandations de l'agent sont pertinentes — *panneau coups/contexte/vidéos/éval*
- [ ] Elle gère les états de chargement et les erreurs
- [ ] Je suis satisfait de l'expérience utilisateur — *Notes : retours d'un testeur externe si possible*

### Livrable 2 — Note détaillée sur les bénéfices et limites

- [ ] J'ai identifié les bénéfices du système d'analyse vidéo — *note §3, chiffrés*
- [ ] J'ai évalué les limites techniques et business — *note §4, juridique en premier*
- [ ] Mon architecture est cohérente et réalisable — *schéma MCP + décisions assumées*
- [ ] Mes estimations de coûts sont pertinentes — *hypothèses × prix unitaires, 3 scénarios, sensibilité*
- [ ] J'ai identifié des alternatives et réfléchi à une roadmap de développement — *2 alternatives + go/no-go*

### Soutenance
- [ ] Je suis en capacité de présenter mes livrables et d'en démontrer la pertinence — *démo répétée ×2, plan B enregistré, Q&A doc 07 relu*

## Notes libres pour la session mentor
- Décisions à valider : D1 (LLM), D2 (MLflow), D3 (corpus) — doc 05 §6.
- Écarts éventuels aux gates (doc 03) et arbitrages faits :
- Questions ouvertes :
