# Note — Bénéfices attendus et limites du système d'analyse vidéo

**Projet** : agent IA d'entraînement aux ouvertures d'échecs — FFE / Cavalier Data
**Objet** : étude de la partie 2 de la mission — un système qui analyse les vidéos pédagogiques pour les indexer par position d'échecs (FEN)
**Auteur** : Richard Hugou, IA Engineer — **Destinataire** : Alan (responsable technique), DTN jeunes FFE
**Statut** : étude de conception — aucune ligne de code de ce système n'est développée à ce stade, c'est volontaire et conforme à la commande.

---

## 1. Contexte et objet de la note

La première partie de la mission est livrée : un POC d'agent d'entraînement aux ouvertures fonctionne de bout en bout — l'élève joue, l'agent identifie l'ouverture, propose les coups de la théorie avec leurs statistiques, explique les idées à partir d'un corpus documentaire sourcé, recommande des vidéos et évalue objectivement les positions hors théorie. Le tout est conteneurisé, mesuré (latence agent p95 : 6,1 s ; 0 coup illégal sur les sorties contrôlées ; 100 % des réponses sourcées) et démontrable en une commande.

La recommandation vidéo actuelle a cependant une limite de conception : elle se fonde sur les **métadonnées** (titre, chaîne, durée). Une vidéo intitulée « La partie italienne expliquée » est recommandée pour l'Italienne en général — pas pour la position précise que l'élève a sur son échiquier, ni pour l'instant précis de la vidéo où cette position est traitée.

D'où la demande d'Alan pour cette seconde partie : **concevoir — sans le développer — un système qui sélectionne les vidéos pertinentes, en extrait des images, détecte l'échiquier, reconstruit chaque position en FEN**, et relie ainsi chaque position au moment exact de chaque vidéo où elle est expliquée.

La présente note couvre : le système envisagé (§2), ses bénéfices (§3), ses limites et risques (§4 — la plus importante), son architecture technique fondée sur MCP (§5), sa faisabilité (§6), ses coûts (§7), deux alternatives (§8) et une feuille de route avec critères d'arrêt (§9).

## 2. Le système envisagé en une page

### 2.1 La chaîne fonctionnelle

```
sélection des vidéos  →  acquisition (métadonnées, transcripts)
→  échantillonnage d'images (1 image / 5 s)
→  détection de l'échiquier dans l'image
→  reconnaissance des pièces case par case
→  reconstruction de la position en FEN
→  validation (python-chess : position légale ?)
→  déduplication (nouvelle position seulement)
→  indexation : FEN ↔ vidéo ↔ timestamp
```

Chaque étape produit l'entrée de la suivante, et chaque position reconstruite est **validée par le même arbitre que le POC** (python-chess) : une position illégale est rejetée, jamais indexée.

### 2.2 Ce que ça change pour l'utilisateur final

Aujourd'hui l'agent répond : « voici trois vidéos sur l'Italienne ». Demain il répondrait : **« cette position exacte est expliquée à 4 min 32 de cette vidéo »** — un lien horodaté, au coup près. Pour un élève de 12 ans, c'est la différence entre « va regarder une vidéo de 20 minutes » et « regarde ces 90 secondes ».

### 2.3 Ce qui existe déjà et qui est réutilisé

Le système ne part pas de zéro — il se branche sur l'infrastructure du POC :

| Existant (POC livré) | Réutilisation dans le système d'analyse vidéo |
|---|---|
| **Le FEN comme clé pivot** de tout le système | Les positions extraites des vidéos rejoignent la même clé — jointure immédiate avec la théorie, le corpus et le moteur |
| Milvus (recherche vectorielle, 477 fiches) | Indexation des transcripts et descriptions de positions |
| MongoDB (caches, métadonnées) | Jobs d'analyse, positions↔timestamps, métadonnées vidéos |
| Service YouTube conforme CGU (métadonnées seules) | Devient le serveur de découverte de contenus |
| Validation python-chess (0 coup illégal) | Filtre de qualité des FEN reconstruits |
| Agent LangGraph | Devient l'« hôte » qui consomme les nouveaux outils (§5) |

## 3. Bénéfices attendus

Chaque bénéfice est associé à un indicateur chiffrable — c'est ainsi qu'on saura si le système tient ses promesses.

| Bénéfice | Pour qui | Indicateur chiffrable |
|---|---|---|
| **Recommandation à la position près** (lien horodaté), et non au titre près | les élèves | cible : ≥ 30 % des recommandations de l'agent enrichies d'un timestamp exact après le pilote (critère go/no-go, §9) |
| **Indexation automatique** d'un corpus vidéo massif, sans travail éditorial | la FFE | coût complet ≈ 0,10–0,15 € par vidéo indexée (étude §7) contre 7,50–15 € en indexation manuelle (15–30 min humaines par vidéo à ~30 €/h chargé) — un facteur ×50 à ×100 |
| **Contrôle qualité du contenu recommandé** : on sait quelles positions une vidéo traite réellement | les entraîneurs | précision de la reconstruction FEN mesurée sur un échantillon annoté à la main (plancher exigé : 90 %, §9) |
| **Effet réseau de données** : chaque vidéo indexée enrichit l'agent existant, sans réentraînement | le produit | nombre de positions FEN uniques ajoutées par mois (hypothèse de travail : ~30 positions clés/vidéo × 1 000 vidéos/mois au scénario S2 = ~30 000 liens position↔vidéo/mois) |

Un bénéfice secondaire mérite mention : le système produit en sous-produit une **cartographie du corpus vidéo francophone** (quelles ouvertures sont bien couvertes, lesquelles sont orphelines) — un outil éditorial pour la FFE si elle veut commander des contenus.

## 4. Limites et risques

C'est la section la plus importante de cette note : chaque limite est énoncée franchement, avec sa mitigation ou son alternative.

### 4.1 La limite juridique — à traiter en premier, c'est la plus dure

La demande initiale parle de « stocker les vidéos pertinentes ». Or **les CGU de YouTube ne le permettent pas** : l'API officielle ne fournit jamais les fichiers vidéo, et le téléchargement par un autre moyen viole les conditions d'utilisation — risque juridique réel pour une fédération, et risque opérationnel (blocage de clé API, donc panne du service).

**La requalification que nous proposons** — et qu'il faut assumer explicitement auprès du commanditaire : le système ne stockera **jamais les fichiers vidéo**, mais **les références et les produits d'analyse** : métadonnées, transcripts, images clés retenues (quelques dizaines par vidéo), positions FEN et timestamps. C'est ce qui a de la valeur, et c'est défendable.

**Mitigations par ordre de robustesse :**
1. **Filtrer sur les vidéos sous licence Creative Commons** (paramètre `videoLicense=creativeCommon` de l'API) : sous-ensemble légalement réutilisable avec attribution — c'est le périmètre retenu pour le MVP.
2. **Pipeline « transcripts + métadonnées »** sans jamais toucher aux fichiers (alternative 1, §8) : zéro risque CGU.
3. **Accords directs avec les créateurs** francophones (quelques chaînes couvrent l'essentiel du besoin pédagogique).
4. **Contenus produits ou licenciés par la FFE** (alternative 2, §8).

### 4.2 Les limites techniques de la vision

Il existe **deux régimes très différents**, et les confondre est le principal risque de sur-promesse :

- **Échiquiers 2D d'enregistrement d'écran** (la grande majorité du contenu pédagogique : l'écran du présentateur montre un échiquier logiciel, plat, aux cases régulières). La détection est un problème de vision classique quasi résolu : géométrie fixe, contraste fort, pièces standardisées. CPU seul, ~50 ms par image.
- **Plateaux physiques filmés en 3D** (parties réelles, angles variables, mains qui masquent des pièces, éclairages changeants). Là, il faut un modèle de vision entraîné, et les erreurs résiduelles se cumulent : **une seule case mal lue sur 64 fausse le FEN entier**. Les travaux publics (chesscog, LiveChess2FEN ; jeu de données ChessReD, ~10 800 images annotées) montrent que c'est faisable mais avec un écart de domaine réel entre leurs conditions de laboratoire et le tout-venant de YouTube.

**Décision de conception** : le MVP se limite au régime 2D. Le 3D est explicitement repoussé en V2, après un pilote mesuré — c'est d'ailleurs le seul endroit du projet où un **véritable entraînement de modèle** apparaîtrait (jeu de données, fine-tuning, GPU, suivi d'expériences MLflow), et il n'est engagé que si les métriques du pilote le justifient.

**Cas dégradés connus du régime 2D** (à tester au pilote) : flèches et surlignages dessinés sur l'échiquier par le présentateur, thèmes de pièces exotiques, zooms et transitions, échiquiers partiellement visibles. Chacun se détecte (score de confiance par case) : en dessous d'un seuil, l'image est écartée plutôt que mal indexée — le même principe d'abstention que le POC.

### 4.3 Les limites de qualité de la chaîne

- **Détecter une position n'est pas comprendre l'explication.** Sans alignement avec l'audio, on indexe des positions muettes : on sait que la position apparaît à 4 min 32, pas que le présentateur y explique le clouage. La parade est le croisement avec le **transcript** (sous-titres) — c'est le rôle de l'étape d'alignement (V1) et l'argument central de l'alternative « transcripts d'abord ».
- **L'échantillonnage est un curseur de coût.** Trop espacé (1 image/10 s) : des positions ratées entre deux prélèvements. Trop dense (1 image/s) : coûts ×5 sans gain pédagogique. L'hypothèse retenue : **1 image / 5 s, soit 180 images pour une vidéo de 15 minutes**, ajustable vidéo par vidéo (sensibilité, étude §6).
- **La déduplication est indispensable** : une même position reste affichée des dizaines de secondes ; la règle est « n'indexer que les *changements* de position », soit ~30 positions clés par vidéo de 15 min.

### 4.4 Les risques business

- **Dépendance à un tiers** : quotas, CGU et API YouTube évoluent unilatéralement. Mitigation : le pipeline est agnostique de la source (le serveur de découverte est isolé, §5) ; le jour où la FFE héberge ses contenus, seul ce serveur change.
- **Coût récurrent proportionnel au volume** (étude §7) : maîtrisé par le fait que l'indexation d'une vidéo est un coût *unique* (idempotence par hash), pas mensuel.
- **ROI dépendant de l'usage réel** : si les élèves ne cliquent pas les liens horodatés, l'investissement ne vaut rien — d'où l'indicateur d'usage dans les critères go/no-go (§9).
- **RGPD et mineurs** : le système n'a *pas besoin* de tracer les visionnages individuels des élèves ; la V1 s'interdit toute donnée personnelle au-delà de ce que fait déjà le POC (aucun compte). Si un suivi de progression arrive un jour (V2+ produit), il passera par une analyse d'impact dédiée, hébergement UE.

## 5. Architecture technique — la solution MCP

### 5.1 MCP en cinq lignes

Le **Model Context Protocol** (standard ouvert initié par Anthropic fin 2024, depuis largement adopté dans l'écosystème des agents) normalise la façon dont un agent — l'« hôte » — découvre et appelle des capacités externes exposées par des **serveurs MCP** : des **outils** (actions), des **ressources** (données lisibles), des **gabarits de prompts**. Transport local en stdio, distant en HTTP ; implémentation Python de référence : FastMCP.

**L'argument d'architecture** : chaque serveur MCP est réutilisable par n'importe quel agent futur de la FFE, indépendamment du framework d'orchestration. On ne construit pas des fonctionnalités enfermées dans notre agent — on construit un outillage fédéral.

### 5.2 Le schéma

*(schéma complet et tableau des composants : document joint `schema-architecture-mcp.md` ; version image dans les slides)*

L'architecture distingue **quatre serveurs MCP** et **un pipeline batch** — et cette distinction est une décision d'honnêteté architecturale :

| Composant | Rôle | Point clé |
|---|---|---|
| **Hôte : l'agent du POC** (LangGraph) | Orchestration, dialogue élève | Devient client MCP — aucun couplage aux implémentations |
| **srv-youtube** | Découverte de contenus, métadonnées, transcripts | Respect CGU ; filtre licence CC |
| **srv-vision** | Pilotage des analyses | `lancer_analyse` retourne un `job_id` : **MCP pilote, le batch exécute** |
| **srv-chess-tools** | Validation FEN, évaluation, théorie | Encapsule les services du POC — réutilisation directe |
| **srv-connaissances** | Recherche sémantique, jointure position↔vidéo | La clé pivot reste le FEN normalisé |
| **File + workers** (hors MCP) | Ingestion de masse : ffmpeg → vision → alignement | ~3 min CPU/vidéo, soit ~20 vidéos/heure/worker |
| **Stockage** | minio (images clés, ~3 Mo/vidéo), MongoDB (jobs, positions), Milvus (vecteurs) | on ne stocke **jamais** les fichiers vidéo |

**Pourquoi le pipeline d'ingestion n'est pas « dans » MCP** : un agent conversationnel ne doit pas attendre 3 minutes qu'une analyse se termine. Il *déclenche* (`lancer_analyse`) et *consulte* (`etat_analyse`) ; la masse est traitée par une file de jobs et des workers dimensionnés indépendamment. Prétendre que MCP « fait » l'analyse serait une sur-vente ; dire qu'il l'*expose* est exact.

### 5.3 Le flux type, raconté

L'élève est sur la position de l'Italienne. L'agent appelle `positions_video(fen)` → « cette position est expliquée à 4 min 32 dans la vidéo X (licence CC) » → lien horodaté dans l'interface. Position inconnue de l'index ? L'agent peut déclencher `lancer_analyse` sur les meilleures candidates trouvées par `srv-youtube` — disponibles quelques minutes plus tard, et définitivement (idempotence par hash de vidéo).

## 6. Faisabilité — verdict par brique

Synthèse de l'étude jointe (`etude-faisabilite-couts.md`) :

| Brique | Maturité | Verdict |
|---|---|---|
| Détection échiquier 2D + reconstruction FEN | vision classique, état de l'art solide | **Faisable dès le MVP** |
| Transcripts + extraction des coups cités | NLP simple + python-chess | **Faisable dès le MVP — le meilleur ratio valeur/coût** |
| Alignement position ↔ timestamp ↔ explication | croisement images/transcript | Faisable en V1, précision à mesurer au pilote |
| Plateaux 3D filmés | modèles et datasets publics, mais écart de domaine réel | **Risqué — V2 seulement, sur décision post-pilote** |
| Cadre juridique hors Creative Commons | négociation, licences | **Bloquant tant que non traité — décision FFE, pas décision technique** |

**Verdict global** : faisable en MVP restreint (vidéos CC + échiquiers 2D + transcripts) avec un risque technique faible ; risqué si on vise d'emblée le cas général (3D + tout YouTube). Ce qui est mûr est bon marché (CPU) ; ce qui est cher (GPU, annotation) n'est justifié qu'en V2.

## 7. Coûts

Méthode : hypothèses explicites × prix unitaires publics, trois scénarios de volume, sensibilité. Tout est recalculable en changeant une hypothèse (détail : étude jointe).

**Build (jours-homme × TJM 500 €)** :

| Phase | Charge | Coût |
|---|---|---|
| **MVP** — pipeline transcripts + CC + 2D, serveurs MCP, intégration à l'agent, pilote 100 vidéos mesuré | 30–40 j-h | **15–20 k€** |
| **V1** — alignement fin, monitoring qualité, industrialisation | 40–60 j-h | 20–30 k€ |
| **V2** — plateaux 3D : dataset, fine-tuning vision, inference | 40–80 j-h | 20–40 k€ (+ données) |

**Opex mensuel (variable ≈ 0,05 $/vidéo + fixe mutualisé avec l'infra de l'agent)** :

| Scénario | Volume | Total/mois | Coût complet par vidéo |
|---|---|---|---|
| S1 | 100 vidéos/mois | ~55–105 $ | ~0,6–1,1 $ (le fixe domine) |
| **S2 (référence)** | 1 000 vidéos/mois | **~95–145 $** | **~0,10–0,15 $** |
| S3 | 10 000 vidéos/mois | ~600–750 $ | ~0,06–0,08 $ |

**Les deux messages qui comptent** : (1) le coût de ce projet est dans les **jours-homme, pas dans le GPU** — le MVP tourne sur CPU ; (2) l'automatisation coûte **×50 à ×100 de moins** que l'indexation humaine (0,10–0,15 € contre 7,50–15 € par vidéo), l'humain restant dans la boucle en contrôle qualité par échantillonnage (~2 h/mois au scénario S2).

## 8. Deux alternatives

### Alternative 1 — le pipeline « transcripts d'abord » *(recommandée comme cœur du MVP)*

Ne pas analyser l'image du tout : transcrire (sous-titres YouTube disponibles ~70 % du temps, API de transcription sinon), détecter les coups **cités dans le texte** (« et ici, cavalier f3… »), et reconstruire les positions par python-chess en rejouant les coups.
**Pour** : ~10× moins cher, zéro risque CGU (aucun accès aux fichiers), déploiement en quelques semaines.
**Contre** : précision temporelle moindre (le coup est cité avant ou après avoir été montré), et fragile quand le présentateur ne verbalise pas les coups.
**Position retenue** : ce n'est pas un plan B, c'est le **premier étage** — la vision 2D vient ensuite *confirmer* et *horodater* ce que le transcript annonce.

### Alternative 2 — le corpus fermé FFE

La fédération fait produire (ou licencie) ses propres vidéos pédagogiques : le pipeline vision complet devient légitime (fichiers possédés), la qualité est contrôlée à la source (échiquier 2D standardisé, coups verbalisés — la précision de détection devient quasi parfaite *par construction du contenu*).
**Pour** : zéro risque juridique, qualité maximale, cohérence éditoriale avec la DTN.
**Contre** : coût de production du contenu (hors périmètre de cette étude) et corpus initial restreint.
**Position retenue** : la trajectoire long terme naturelle — le pipeline construit au MVP fonctionne tel quel sur ce corpus, seule la source change.

## 9. Feuille de route et critères d'arrêt

| Étape | Contenu | Durée indicative | Critères **go/no-go** pour la suivante |
|---|---|---|---|
| **MVP** | vidéos CC + transcripts + vision 2D ; pilote sur **100 vidéos** ; échantillon de contrôle annoté à la main (~500 images) | 6–8 semaines | précision FEN ≥ **90 %** sur l'échantillon · coût complet ≤ **0,20 €**/vidéo · ≥ **30 %** des recommandations de l'agent enrichies d'un timestamp · validation juridique du sourcing |
| **V1** | alignement audio↔position↔timestamp, monitoring qualité, back-office de contrôle, intégration complète à l'agent du POC | 8–12 semaines | usage réel : taux de clic des liens horodatés ; taux d'erreur signalé par les entraîneurs |
| **V2** | plateaux 3D : jeu de données, fine-tuning d'un modèle de vision (le seul vrai entraînement du projet — GPU, MLflow), inference | à décider post-pilote | uniquement si le pilote montre une demande réelle sur le contenu 3D |

Ce séquencement applique au projet vidéo la même discipline que le POC : **aucune étape n'est engagée sans que la précédente ait produit ses chiffres.**

## 10. Conclusion

Le bénéfice principal est net : passer de « voici une vidéo sur l'Italienne » à **« cette position exacte est expliquée ici, à 4 min 32 »** — pour un coût d'indexation de l'ordre de **dix centimes par vidéo**, cinquante à cent fois moins que l'équivalent humain.

La limite principale est **juridique avant d'être technique** : les CGU de YouTube interdisent de stocker les vidéos. La réponse est double : requalifier ce qu'on stocke (références et produits d'analyse, jamais les fichiers) et démarrer sur le périmètre incontestable (licences Creative Commons + transcripts).

La recommandation : lancer le **MVP « transcripts + CC + vision 2D »** (15–20 k€, ~100–150 $/mois au régime de référence), le mesurer sur un pilote de 100 vidéos contre des critères d'arrêt chiffrés, et ne décider du grand saut technique (le 3D et son entraînement de modèle) qu'au vu de ces mesures. C'est la même démarche qui a conduit le POC : **d'abord l'étalon, ensuite la mesure, enfin la décision.**
