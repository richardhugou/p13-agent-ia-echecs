# 06 — Matériel, contraintes, « soucis d'entraînement », tracking (MLflow / W&B)

## 1. Audit réel du poste (relevé du 2026-07-25)

| Ressource | Valeur relevée | Verdict pour le projet |
|---|---|---|
| Machine | **Apple M5, 10 cœurs, arm64** | Large pour le POC ; attention images Docker **arm64** |
| RAM | **16 Go** | **La contrainte n°1** — voir §2 |
| Disque | **624 Go libres** / 926 | Aucun souci (stack ≈ 10–15 Go images+volumes) |
| OS | macOS 26.5.1 | — |
| Docker / Compose | **29.5.2 / v5.1.4** ✅ installés | OK |
| Python système | **3.9.6** ⚠️ | Trop vieux pour LangGraph 1.x (≥ 3.10) → **Python 3.12 épinglé dans les Dockerfiles**, et 3.12 via uv/pyenv pour l'EDA locale |
| Node / npm | v24.14.1 / 11.11.0 ✅ | Compatible Angular récent |
| Angular CLI | **absent** ⚠️ | À installer en É5 |
| Git | 2.50.1 ✅ | OK |

## 2. Contraintes structurantes (à connaître avant de coder)

1. **Pas de GPU dans Docker sur macOS** (pas de passthrough Metal). Conséquences :
   - les embeddings en conteneur tournent **CPU-only** → acceptable pour ~600 chunks (minutes), mais l'ETL peut aussi s'exécuter **sur l'hôte** (Apple Silicon/MPS) et ne pousser que les vecteurs — décision de confort, pas bloquante ;
   - aucun LLM local sérieux en conteneur → renforce le choix LLM via API (D1).
2. **Budget RAM 16 Go partagé** : macOS + navigateur + IDE ≈ 6–8 Go ; il reste ~8 Go pour Docker. Allouer **8 Go à Docker Desktop**, et compter : Milvus+etcd+minio ≈ 2–4 Go, Mongo ≈ 0,5–1 Go, backend (torch CPU + sentence-transformers) ≈ 1,5–2,5 Go, front dev ≈ 0,5–1 Go, MLflow ≈ 0,3 Go. **Ça passe, sans Ollama.** Fermer les applis lourdes pendant les tests e2e.
3. **Taille des images** : torch CPU + sentence-transformers ≈ 2–3 Go d'image backend ; Milvus ≈ 1 Go ; prévoir 10–15 Go de disque Docker (OK ici).
4. **Téléchargement des modèles HF au premier run (~1,2 Go)** : monter un volume cache (HF_HOME) ou télécharger au build de l'image → sinon la démo « installation fraîche » prend un quart d'heure de plus au premier lancement.
5. **arm64 partout** : vérifier que chaque image du compose a un tag arm64 (Milvus, Mongo, MLflow : OK aujourd'hui ⚠️ re-vérifier les tags exacts) ; Stockfish installé via paquet de la distro dans l'image backend.
6. **Ports à réserver** : 4200, 8000, 19530, 9091, 27017, 5000 — vérifier les conflits locaux avant É1.

## 3. « Soucis d'entraînement » anticipés — et le discours à tenir

### 3.1 Ce POC ne comporte AUCUN entraînement — c'est un choix à assumer
Phrase pour le jury : *« Le projet ne fine-tune aucun modèle : les connaissances viennent de sources de vérité externes (théorie Lichess, Stockfish, corpus wiki via RAG). Le RAG est précisément l'alternative économique et maintenable au fine-tuning pour injecter de la connaissance métier : coût quasi nul, mise à jour = ré-indexation, zéro risque d'oubli catastrophique, traçabilité des sources. »*

### 3.2 Les vrais risques « ML » du POC (même sans entraînement)
| Risque | Impact | Mitigation |
|---|---|---|
| Modèle d'embedding inadapté au FR | recall faible | Modèle multilingue (Qwen3) + gold set mesuré AVANT d'optimiser |
| Chunking naïf | contexte hors-sujet | Comparaison run A/run B tracée MLflow (doc 04 §6) |
| Dérive de versions (transformers, torch) | résultats non reproductibles | Versions épinglées + hash du modèle loggé dans chaque run |
| Cold start (download modèle, chargement en RAM) | démo qui rame | Warm-up au démarrage du conteneur + cache HF |
| Hallucinations du LLM de synthèse | réponses fausses | Le LLM ne produit ni coups ni évals ; prompt « réponds uniquement depuis le contexte fourni, cite tes sources » ; question piège dans le gold set |
| Non-déterminisme LLM | métriques instables | temperature basse, seeds où c'est possible, éval sur 25 questions (moyenne) |

### 3.3 Là où un VRAI entraînement apparaîtrait (partie 2 — à dire si on nous pousse)
La détection d'échiquier dans les frames vidéo peut nécessiter un fine-tuning vision (YOLO/CNN par case) : dataset public type **ChessReD (~10 800 images annotées)** ⚠️ à sourcer, GPU cloud (T4 ≈ 0,35 $/h ⚠️), quelques heures de fine-tuning, tracking W&B ou MLflow, risque principal = **domain gap** (échiquiers 2D de screencast ≠ plateaux 3D filmés). Chiffré dans l'étude de faisabilité — mais **hors périmètre POC**, et la majorité des vidéos pédagogiques montrent des échiquiers 2D où le classique OpenCV suffit.

## 4. Tracking des expériences : MLflow vs W&B (décision)

| Critère | **MLflow (reco)** | Weights & Biases | Langfuse / LangSmith |
|---|---|---|---|
| Hébergement | **Local/compose, gratuit, aucune donnée qui sort** | Cloud (compte, données externes) | Self-host possible / SaaS |
| Traces LLM/agents | Autolog LangChain/LangGraph (traces par nœud) | Weave (bien mais cloud) | Excellent mais spécialisé traces uniquement |
| Runs params/métriques (notre récit avant/après) | ✅ cœur du produit | ✅ | ❌ partiel |
| Coût / friction pour un POC école | Zéro | Compte + quota gratuit | Setup en plus |

**Décision** : **MLflow en service compose (D2)** — un seul outil pour (a) les runs d'éval RAG (params/métriques/figures) et (b) les traces d'exécution du graphe. W&B cité en alternative « équipe distribuée » ; Langfuse cité en « si on ne voulait que de l'observabilité LLM ».

**Ce qu'on loggue systématiquement** :
- *Params* : modèle d'embedding + hash, chunk_size, overlap, k, seuil théorie N, profondeur Stockfish, modèle LLM, température.
- *Métriques* : recall@5, MRR, taux d'abstention correcte, latence p50/p95 par nœud, tokens in/out, coût €/interaction.
- *Artefacts* : figures EDA, rapport d'ingestion, gold set versionné, captures pour slides.

## 5. Top 10 des risques projet (mitigations concrètes)

| # | Risque | Prob. | Impact | Mitigation |
|---|---|---|---|---|
| 1 | RAM saturée pendant e2e (16 Go) | Moy | Démo qui rame | Docker 8 Go, pas d'Ollama, fermer applis, warm-up |
| 2 | Quota YouTube épuisé un jour de test | Moy | Feature morte | Cache 7 j + fixtures de secours servies si quota → la démo ne dépend jamais du quota |
| 3 | HTTP 429 Lichess | Moy | Latence/erreurs | Cache 24 h + backoff 60 s + débounce UI |
| 4 | Milvus lent à démarrer → API plante au boot | Haute | `compose up` cassé | healthcheck + `depends_on: condition: service_healthy` + retry connexion |
| 5 | Python système 3.9 utilisé par erreur en local | Moy | Incompatibilités LangGraph | Tout en conteneur ; uv/pyenv 3.12 pour l'EDA |
| 6 | Image sans variante arm64 | Faible | Build cassé | Vérifier les tags en É1, alternatives notées |
| 7 | FEN mal encodé dans les URLs | Haute si path param | Bugs sournois | Query param décidé (doc 05 §3) |
| 8 | CORS front↔API | Haute | Intégration bloquée | Middleware CORS dès É1, origines par env var |
| 9 | Démo dépendante du réseau | Moy | Soutenance ratée | Caches chauds + mode fixtures + vidéo de secours (doc 08) |
| 10 | Chiffres de slides invérifiables | Moy | Crédibilité | Convention [MESURE]/⚠️ : tout chiffre est soit mesuré soit sourcé |
