# Vérification des livrables — contre la liste officielle de la plateforme

> Dernier contrôle avant dépôt (demande mentor : « recheck bien les livrables »). Chaque exigence officielle → où elle est → preuve. **Résultat : rien d'absent.**

## 1. « Système développé avec LangGraph, FastAPI, Milvus et MongoDB »

| Exigence | Où | Preuve |
|---|---|---|
| LangGraph | `backend/graph/` (graphe : valider → identifier → routeur → théorie/moteur → RAG → vidéos → synthèse) | 65 tests verts, notebook 05 |
| FastAPI | `backend/api.py` + `main.py` (6 endpoints, Swagger) | healthcheck + e2e en conteneurs |
| Milvus | collection `openings_kb` (477 fiches, HNSW/cosinus) + règle des rayons | `/vector-search`, recall 1,0 (MLflow) |
| MongoDB | caches explorer/évals/vidéos + eval_runs | vérifié en conteneurs (cached=true) |
| **Code accessible via un dépôt Git** | https://github.com/richardhugou/p13-agent-ia-echecs (public, `main` = version de rendu, CI verte) | + archive dans le zip (`Hugou_Richard_1_code_082026.zip`) |
| **Démonstration, exécution locale avec docker compose** | `docker compose up` / `./demarrer.sh` — 7 conteneurs ; installation fraîche mesurée 2 min 09 | `tester-installation.sh` + vidéo Loom + démo live |

## 2. « Note détaillée sur les bénéfices et limites du système »

| Exigence | Où | Preuve |
|---|---|---|
| La note (bénéfices ET limites) | `note-benefices-limites.md` → PDF 8 pages dans le zip (n° 3) | bénéfices chiffrés §3 ; limites §4 (juridique en premier, chaque limite avec mitigation) |
| **incluant : un schéma d'architecture technique** | dans la note §5 (composants + décisions) **et** document dédié `schema-architecture-mcp.md` (zip n° 5) | 4 serveurs MCP + pipeline batch + flux type |
| **incluant : une étude de faisabilité avec estimation des coûts** | dans la note §6-7 **et** document dédié `etude-faisabilite-couts.md` (zip n° 4) | build 15-20 k€ MVP · opex 3 scénarios · sensibilité · comparaison ×50-100 |
| Alternatives + roadmap (grille d'autoéval) | note §8-9 | 2 alternatives · roadmap MVP/V1/V2 avec go/no-go chiffrés |
| Chaîne demandée couverte : stockage vidéos / frames / détection échiquier / FEN | note §2 (chaîne fonctionnelle) + §4.1 (requalification CGU du « stockage ») | présentée comme **étude**, rien de développé (volontaire) |

## 3. « La fiche d'autoévaluation pour les sessions avec le mentor »

| Exigence | Où | Preuve |
|---|---|---|
| Fiche cochée | `fiche-autoevaluation.md` → PDF dans le zip (n° 6) | **toutes les cases cochées, chacune avec sa preuve** (test, notebook exécuté, mesure) — transcription fidèle de la grille officielle |
| Notes pour la session mentor | section finale de la fiche (D1/D2/D3, leçon gold set, écart FEN query param) | + mémo privé de session |

## Compléments au zip (non exigés, joints en bonus)

Présentation (PDF 18 pages) · documentation technique · vidéo de démonstration (lien Loom). Zip : `Mettez_en_place_un_agent_IA_Hugou_Richard.zip`, nommage interne `Hugou_Richard_<n>_<libellé>_082026`, régénérable par `./livrables/generer-rendu.sh`.

## Verdict

**Aucun livrable manquant.** Deux choix à savoir défendre : le schéma et l'étude existent en documents séparés *en plus* d'être intégrés à la note (confort de lecture) ; l'écart « FEN en query param » vs l'énoncé est documenté (docs/05 §3).
