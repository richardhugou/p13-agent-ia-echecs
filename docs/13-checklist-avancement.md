# 13 — Checklist d'avancement du projet (basée sur la mission officielle)

> Mise à jour : 2026-08-14. Pondération estimée sur les 80 h de la mission.
> Convention : `[x]` fait · `[~]` partiellement fait · `[ ]` à faire.

## Avancement global : ≈ 19 %

| Phase | Poids | Avancement | Contribution |
|---|---:|---:|---:|
| 0. Cadrage & conception (implicite : « lire la mission, prendre des notes, préparer ») | 15 % | 95 % | 14 % |
| 1. Poste de travail (Git, structure, compose de base) | 5 % | 0 % | 0 % |
| 2. Backend agent (FEN, Lichess, Stockfish) | 15 % | 0 % | 0 % |
| 3. RAG (ETL Wikichess, Milvus, vector-search) | 15 % | 0 % | 0 % |
| 4. Vidéos YouTube | 5 % | 0 % | 0 % |
| 5. Frontend Angular | 15 % | 0 % | 0 % |
| 6. Containerisation complète + préparation démo | 10 % | 0 % | 0 % |
| 7. Partie 2 — conception analyse vidéo (note, schéma MCP, coûts) | 15 % | 20 % | 3 % |
| 8. Autoévaluation + packaging des livrables | 5 % | 20 % | 1 % |
| **Total** | **100 %** | | **≈ 19 %** |

Lecture honnête : **la conception est quasi terminée, le développement n'a pas commencé** (0 % du code sur ~65 % du poids total).

---

## Phase 0 — Cadrage & conception ✅ (95 %)

- [x] Mission lue et reformulée (fiction, personas, périmètre) → doc 01
- [x] Fondations produit : donnée d'entrée, boucle utilisateur, interface → doc 11
- [x] Sources de données chiffrées, plan EDA/ETL, schémas de stockage → doc 04
- [x] Architecture technique (graphe LangGraph, contrats API, compose) → doc 05
- [x] Modèles choisis + métriques (D1 = Haiku 4.5, prix vérifiés) → doc 12
- [x] Présentation 14 diapos (avec `[MESURE]` à remplir) → livrables/presentation-14-slides.md
- [x] Script démo, questions jury, checklist d'interdépendances → docs 03, 07, 08
- [~] Décisions D2 (MLflow en compose) et D3 (corpus) : recos posées, à confirmer avec le mentor

## Étape 1 — Poste de travail ⬜ (0 %) ← **PROCHAINE ACTION**

- [ ] Dépôt Git initialisé avec README.md (template prêt dans livrables/)
- [ ] Structure `backend/`, `frontend/`
- [ ] Dockerfiles avec versions épinglées (Python 3.12, Node)
- [ ] `docker-compose.yml` de base : FastAPI « Hello World »
- [ ] Route `/api/v1/healthcheck` fonctionnelle dans le conteneur
- [ ] Variables d'environnement pour la config (ports, etc.) dès le début

## Étape 2 — Backend agent ⬜ (0 %)

- [ ] Endpoint coups théoriques (`/moves`, FEN — décision prise : query param, alias path documenté)
- [ ] Endpoint `/evaluate` (Stockfish, centipawns)
- [ ] Validation FEN et légalité des coups via python-chess (objectif : 0 coup illégal)
- [ ] Couche « service » séparée de la couche API (indicateur autoéval)
- [ ] Gestion erreurs + timeouts APIs externes, respect rate limit Lichess (429 → 60 s)
- [ ] Cache MongoDB (explorer 24 h, évals sans TTL)
- [ ] Graphe LangGraph structuré : routeur théorie/moteur déterministe

## Étape 3 — RAG ⬜ (0 %)

- [ ] Inventaire exact du corpus via API MediaWiki (comptes → slide data)
- [ ] Script ETL rejouable : extraction, nettoyage, chunking 300–500 tokens, dédup
- [ ] Embeddings Qwen3-Embedding-0.6B → Milvus (HNSW, cosinus, métadonnées ECO)
- [ ] Endpoint `/vector-search` avec filtre scalaire
- [ ] Connexion FastAPI ↔ Milvus dans le réseau Docker
- [ ] Gold set 25 questions + runs MLflow (Run A naïf vs Run B amélioré, recall@5 ≥ 0,8)
- [ ] RAG branché dans le workflow LangGraph

## Étape 4 — Vidéos YouTube ⬜ (0 %)

- [ ] Clé API YouTube obtenue
- [ ] Endpoint `/videos` (métadonnées, filtres pertinence, durée 4–30 min)
- [ ] Cache MongoDB TTL 7 j (~30 requêtes réelles au total, quota jamais approché)
- [ ] Gestion du cas « aucune vidéo trouvée »
- [ ] Intégré au workflow LangGraph ; liens affichés (embed si possible)

## Étape 5 — Frontend Angular ⬜ (0 %)

- [ ] Angular CLI installé (à faire sur la machine)
- [ ] Échiquier ngx-chessboard fonctionnel (repo OC `material-chessboard`)
- [ ] Panneau coach : état théorie/hors théorie, coups + stats, explication + sources, vidéos
- [ ] Services Angular → API backend ; synchronisation FEN
- [ ] États de chargement et erreurs réseau ; debounce des appels

## Étape 6 — Containerisation & démo ⬜ (0 %)

- [ ] `docker-compose.yml` complet (front, back+Stockfish, Milvus+etcd+minio, MongoDB, MLflow)
- [ ] Volumes persistants vérifiés (`docker volume ls` / `inspect`, test de recréation)
- [ ] Test installation fraîche : app utilisable < 5 min (objectif O5)
- [ ] README d'installation détaillé
- [ ] Positions de démo préparées (script doc 08 : Italienne → sortie de théorie)
- [ ] Test de bout en bout de tous les services interfacés

## Étape 7 — Partie 2 : conception analyse vidéo 🟨 (20 %)

- [~] Note bénéfices/limites **8–10 pages** — squelette créé, à rédiger
- [~] Schéma d'architecture technique MCP — squelette créé, à produire
- [~] Étude de faisabilité + coûts (build + opex) — squelette créé, à chiffrer
- [ ] Recherche technos détection d'échiquier (OpenCV, modèles de vision)
- [ ] 1–2 alternatives + roadmap de développement
- [ ] Risques techniques et business identifiés

## Étape 8 — Autoévaluation & rendu ⬜ (20 %)

- [~] Fiche d'autoévaluation — squelette créé, à cocher en fin de projet
- [ ] Tous les indicateurs de la fiche vérifiés (graphe, RAG, APIs, compose, Angular, étude)
- [ ] Zip `Titre_du_projet_nom_prenom` avec nommage des livrables (`Nom_Prenom_n_libellé_mmaaaa`)
- [ ] Session de bilan mentor réservée

---

## Écarts relevés entre nos docs et l'énoncé officiel (à assumer en soutenance)

1. **FEN en query param vs `/moves/{fen}` de l'énoncé** : choix documenté (encodage URL des `/` et espaces), alias conforme à l'énoncé gardé en option — doc 05 §3.
2. **MLflow** : non exigé par l'énoncé, ajouté comme preuve de tracking (D2) — c'est un plus, pas une dette.
3. La partie 2 dit « stocke les vidéos » : à traiter dans la note de limites (conformité CGU YouTube = pas de téléchargement dans le POC ; le système cible suppose des vidéos sous licence adaptée ou un partenariat).
