# [SQUELETTE] Note — Bénéfices attendus et limites du système d'analyse vidéo

> **Livrable final : 8–10 pages.** Ce squelette fixe le plan, les points à couvrir et les chiffres à insérer.
> **Comment compléter** : rédiger dans l'ordre 1→2→4→6→5→7→8→9 (le schéma §5 et les coûts §7 sont produits dans les deux autres livrables puis intégrés ici). Chaque [MESURE]/[CHIFFRE] doit être remplacé par une valeur mesurée ou une hypothèse posée explicitement. Relecture finale : chaque limite citée a une mitigation ou une alternative.

---

## 1. Contexte et objet de la note (≈ 0,5 page)
- Rappel mission FFE + POC livré (une phrase sur ce que le POC fait déjà).
- La demande d'Alan : concevoir (sans développer) un système qui **stocke les vidéos pertinentes, en extrait des frames, détecte l'échiquier et convertit chaque position en FEN**.
- Objet : bénéfices, limites, architecture (MCP), faisabilité et coûts, alternatives, roadmap.

## 2. Le système envisagé en une page (≈ 1 page)
- Chaîne fonctionnelle : sélection vidéos → acquisition → échantillonnage frames → détection échiquier → reconnaissance des pièces → FEN → validation (python-chess) → indexation (les FEN rejoignent la même clé pivot que le POC).
- Ce que ça change pour l'utilisateur final : *« montre-moi le moment exact de la vidéo où cette position est expliquée »* — le lien position↔timestamp vidéo.
- Encadré : ce qui existe déjà dans le POC et qui est réutilisé (Milvus, MongoDB, FEN pivot, agent LangGraph).

## 3. Bénéfices attendus (≈ 1,5 page) — chacun avec un chiffre
| Bénéfice | Pour qui | Indicateur chiffrable |
|---|---|---|
| Recommandation vidéo **à la position près** (timestamp), pas au titre près | élèves | % de recommandations avec timestamp exact [CIBLE] |
| Indexation automatique d'un corpus vidéo massif sans travail éditorial | FFE | coût/vidéo indexée [CHIFFRE de l'étude] vs indexation manuelle (~15–30 min humaine/vidéo) |
| Contrôle qualité du contenu recommandé (positions réellement traitées dans la vidéo) | entraîneurs | précision de la détection [CHIFFRE sourcé] |
| Effet réseau de données : chaque vidéo indexée enrichit l'agent existant | produit | nb positions FEN uniques ajoutées/mois [HYPOTHÈSE] |

## 4. Limites et risques (≈ 2 pages — la section la plus importante)
### 4.1 Limite juridique (à traiter EN PREMIER — c'est la plus dure)
- CGU YouTube : l'API ne fournit pas les fichiers vidéo ; le téléchargement hors API viole les conditions d'utilisation → risque juridique et de blocage.
- Mitigations : filtrer `videoLicense=creativeCommon` (sous-ensemble réutilisable avec attribution), accords avec créateurs, contenus produits par la FFE, ou pipeline « transcripts + métadonnées » sans toucher aux fichiers (voir alternatives §8).
### 4.2 Limites techniques de la vision
- Deux régimes très différents : échiquiers **2D de screencast** (majorité du contenu pédagogique, détection quasi résolue en vision classique) vs **plateaux 3D filmés** (angles, occlusions des mains, éclairage → modèle entraîné requis, erreurs résiduelles par case qui se cumulent : une erreur sur 64 cases fausse le FEN entier).
- Chiffres à sourcer : précision par case et par plateau des travaux publics (chesscog, LiveChess2FEN, dataset ChessReD ~10 800 images ⚠️).
- Cas dégradés : flèches/surlignages dessinés sur l'échiquier, thèmes de pièces exotiques, zooms/transitions, positions partielles.
### 4.3 Limites de qualité de la chaîne
- Détecter une position ≠ comprendre l'explication : sans alignement audio/transcript, on indexe des positions muettes.
- Échantillonnage : trop espacé → positions ratées ; trop dense → coûts ×10 (chiffrer avec l'hypothèse retenue : 1 frame/5 s → 180 frames pour 15 min).
- Déduplication : une même position apparaît des dizaines de fois par vidéo → règle « nouvelle position seulement ».
### 4.4 Risques business
- Dépendance à un tiers (YouTube) ; instabilité des quotas/CGU.
- Coût récurrent proportionnel au volume (voir étude) ; ROI dépendant de l'usage réel des recommandations.
- RGPD/mineurs si on trace les visionnages (à éviter en V1).

## 5. Architecture technique MCP (≈ 1,5 page)
- Intégrer ici le schéma et le tableau des composants de **`schema-architecture-mcp.md`**.
- Justifier MCP (standard ouvert, serveurs d'outils réutilisables par tout agent) ET assumer la nuance : l'ingestion de masse reste un pipeline batch ; MCP expose l'interrogation et le pilotage.

## 6. Faisabilité (≈ 1 page)
- Synthèse de l'étude (`etude-faisabilite-couts.md`) : ce qui est mûr (détection 2D, transcription, indexation), ce qui est risqué (3D, juridique), ce qui est cher (GPU inutile en 2D, transcription API à volume).
- Verdict : faisable en MVP restreint (vidéos CC + échiquiers 2D + transcripts), risqué en général.

## 7. Coûts (≈ 1 page)
- Reprendre les tableaux build + opex et les 3 scénarios de l'étude ; donner le coût unitaire €/vidéo et les 2 postes dominants.

## 8. Alternatives (≈ 0,5–1 page — en proposer 2, exigence OC)
1. **Pipeline « transcripts d'abord »** (recommandée en MVP) : transcription + détection des coups cités dans le texte (« et ici cavalier f3 ») → reconstruction des positions par python-chess sans toucher à la vidéo. ~10× moins cher, zéro risque CGU, précision moindre sur l'alignement exact.
2. **Corpus fermé FFE** : la fédération fait produire/licencie ses vidéos → pipeline vision complet légitime, qualité contrôlée, coût de contenu à la place du risque juridique.

## 9. Roadmap de développement (≈ 0,5 page)
- **MVP (X semaines)** : vidéos CC + 2D + transcripts, [CHIFFRE] vidéos pilotes, mesure de précision sur un échantillon annoté à la main (~[CHIFFRE] frames).
- **V1** : alignement audio↔position, intégration complète à l'agent du POC, monitoring qualité.
- **V2** : plateaux 3D (fine-tuning vision, dataset, GPU — c'est ICI qu'apparaît le vrai entraînement, avec tracking W&B/MLflow).
- Critères go/no-go entre chaque étape (précision plancher, coût/vidéo plafond, validation juridique).

## 10. Conclusion (≈ 0,25 page)
Reprendre : bénéfice principal (recommandation à la position près), limite principale (juridique), recommandation (MVP transcripts + CC), et le lien avec le POC démontré.
