# Étude de faisabilité & coûts — système d'analyse vidéo (build + opex)

> **Méthode** : hypothèses explicites × prix unitaires publics (ordres de grandeur d'août 2026), 3 scénarios de volume, analyse de sensibilité. La méthode est le livrable autant que les chiffres : tout est recalculable en changeant une hypothèse du §1.

## 1. Hypothèses de dimensionnement (le contrat de lecture)

| Hypothèse | Valeur retenue | Justification |
|---|---|---|
| Durée moyenne vidéo | 15 min | standard du format pédagogique |
| Échantillonnage frames | 1 frame / 5 s → **180 frames/vidéo** | compromis précision temporelle / coût (sensibilité §6) |
| Frames clés conservées (changement de position) | ~30/vidéo × ~100 Ko ≈ **3 Mo/vidéo** | on ne stocke jamais la vidéo, seulement les frames retenues |
| Régime de vision | **2D screencast** (MVP) : vision classique CPU ~50 ms/frame | majorité du contenu pédagogique ; le 3D est en V2 |
| Compute pipeline complet | ~3 min CPU/vidéo (extraction + détection + FEN + alignement) | ordre de grandeur — à confirmer sur le pilote de 100 vidéos |
| Transcription | sous-titres YouTube quand disponibles (hypothèse : ~70 % du corpus) ; sinon API type Whisper ≈ 0,006 $/min | poste dominant, voir sensibilité |
| Enrichissement LLM (résumé, alignement sémantique) | ~5k tokens in + 1k out par vidéo (modèle éco, tarif type Haiku : 1 $/M entrée, 5 $/M sortie) | ≈ 0,01 $/vidéo |
| Périmètre juridique MVP | vidéos **Creative Commons** uniquement + transcripts | lève le risque CGU (cf. note §4.1) |
| TJM développement | 500 € (profil junior encadré, marché France) — curseur ajustable | pour le build |

## 2. Coûts de BUILD (jours-homme × TJM)

| Phase | Contenu | Charge estimée | Coût (TJM 500 €) |
|---|---|---|---|
| **MVP** | Pipeline transcripts + vidéos CC + détection 2D, serveurs MCP srv-youtube/srv-vision/srv-connaissances, intégration à l'agent POC, pilote sur 100 vidéos + mesure de précision | **30–40 j-h** | **15–20 k€** |
| **V1** | Alignement fin transcript↔position↔timestamp, monitoring qualité, back-office de contrôle, industrialisation (CI, IaC légère) | 40–60 j-h | 20–30 k€ |
| **V2** | Plateaux 3D : dataset (annotation si nécessaire : 5–10 k€), fine-tuning vision (GPU : quelques dizaines d'heures de T4, coût GPU **marginal : < 50 €**), tracking expériences (MLflow/W&B), déploiement inference | 40–80 j-h | 20–40 k€ (+ data) |

**Message clé** : dans ce projet, le coût est dans les **jours-homme**, pas dans le GPU.

## 3. OPEX mensuel — 3 scénarios

Postes variables (par vidéo) : compute ≈ 0,007 $ ; transcription (30 % des vidéos sans sous-titres × 0,09 $) ≈ 0,03 $ ; LLM ≈ 0,01 $ ; stockage marginal ≈ 0,001 $/mois. **≈ 0,05 $/vidéo variable** (0,14 $ si transcription API à 100 %).
Postes fixes : VM pipeline + bases (Milvus/Mongo) + monitoring ≈ 50–100 $/mois (mutualisables avec l'infra de l'agent) ; à 10 k vidéos/mois : 150–300 $/mois.

| Poste | **S1 : 100 vidéos/mois** | **S2 : 1 000 vidéos/mois** | **S3 : 10 000 vidéos/mois** |
|---|---|---|---|
| Compute (extraction+vision) | ~1 $ | ~7 $ | ~70 $ |
| Transcription (30 % API) | ~3 $ | ~27 $ | ~270 $ |
| LLM enrichissement | ~1 $ | ~10 $ | ~100 $ |
| Stockage frames (cumul 1re année) | < 1 $ | ~1 $ (3 Go/mois) | ~8 $ (30 Go/mois) |
| Fixe infra | 50–100 $ | 50–100 $ | 150–300 $ |
| **Total/mois** | **~55–105 $** | **~95–145 $** | **~600–750 $** |
| **Coût complet / vidéo** | ~0,6–1,1 $ (le fixe domine) | **~0,10–0,15 $** | ~0,06–0,08 $ |

## 4. Comparaison avec l'alternative manuelle (le chiffre qui vend)
Indexation humaine : 15–30 min/vidéo × ~30 €/h chargé ≈ **7,5–15 €/vidéo**, contre **~0,10–0,15 €/vidéo** automatisé (S2) → facteur **×50 à ×100**, hors qualité/exhaustivité. (Et l'humain reste dans la boucle en contrôle qualité par échantillonnage : ≈ 2 h/mois au scénario S2, contrôle par échantillonnage de 2 %.)

## 5. Faisabilité technique — verdict par brique

| Brique | Maturité | Verdict |
|---|---|---|
| Détection échiquier 2D + FEN | Vision classique, état de l'art solide | **Faisable MVP** |
| Transcripts + extraction des coups cités | NLP simple + python-chess | **Faisable MVP, le meilleur ratio valeur/coût** |
| Alignement position↔timestamp | Croisement frames/transcript | Faisable V1, précision à mesurer sur pilote |
| Plateaux 3D filmés | Modèles publics + jeux de données publics (ChessReD, ~10 800 images) mais écart de domaine réel | **Risqué — V2 seulement, après pilote** |
| Cadre juridique hors CC | Négociation/licences | **Bloquant tant que non traité** — décision FFE |

## 6. Sensibilité (les 3 curseurs qui changent la facture)
1. **Échantillonnage** ×3 (1 frame/s au lieu de 1/5 s) → compute & stockage ×3, précision temporelle accrue : réserver aux vidéos « premium ».
2. **Transcription** : 100 % API (×3 sur le poste dominant) vs modèle local auto-hébergé (variable ≈ 0, mais + infra GPU/CPU et + maintenance) : bascule pertinente au-delà de ~5 000 vidéos/mois.
3. **Volume** : sous ~500 vidéos/mois, le fixe domine → mutualiser l'infra avec l'agent existant est la vraie économie.

## 7. Risques économiques & go/no-go
- Risques : changement CGU/quotas YouTube ; dérive du périmètre vers le 3D trop tôt ; sous-estimation du contrôle qualité humain.
- **Critères go/no-go après pilote MVP (100 vidéos)** : précision FEN ≥ 90 % sur l'échantillon annoté (~500 frames) ; coût complet ≤ 0,20 €/vidéo ; ≥ 30 % des recommandations de l'agent enrichies d'un timestamp ; validation juridique du sourcing.

## 8. Recommandation
Lancer le **MVP « CC + 2D + transcripts »** (15–20 k€, opex ~100–150 $/mois au régime S2), mesurer sur un pilote de 100 vidéos, et ne décider du V2 « 3D » (le seul qui exige un vrai entraînement de modèle) qu'au vu des métriques du pilote. Roadmap détaillée : note §9.
