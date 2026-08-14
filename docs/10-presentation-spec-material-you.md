# 10 — Spécification design de la présentation (prête à coller dans Gemini)

> **Usage** : copier ce document (en entier, ou le bloc « Consignes globales » + les slides voulus) dans Gemini / Google Slides « Créer avec l'IA ». Chaque slide contient : mise en page, textes exacts, visuels décrits, et notes du présentateur.
> Le script oral complet reste dans `09-presentation-v0-monture.md` — ce document-ci est la maquette.

---

## CONSIGNES GLOBALES POUR GEMINI (à respecter sur toutes les diapositives)

**Langue & format** : français, 16:9 (1920×1080), thème clair uniquement.

**Style** : Material Design 3 / Material You, sobre et épuré. Aucune photo, aucun clipart, aucune image de stock, aucun dégradé criard. Uniquement : aplats doux, cartes arrondies, icônes Material Symbols (style *rounded*, graisse fine), pictogrammes vectoriels plats, larges marges. Une diapositive = un seul message.

**RÈGLE ABSOLUE SUR LES CHIFFRES** : tout texte entre crochets `[…]` est un emplacement volontairement vide. Ne JAMAIS le remplacer par une valeur inventée. Le représenter par un grand tiret « — » accompagné d'une petite puce (chip) au contour fin portant le libellé du crochet (ex. « à sourcer », « à mesurer »). C'est un choix assumé de version de travail.

**Palette (rôles Material 3, thème « échiquier boisé », clair)** :
- `primary` **#3A5A40** (vert échiquier profond) · `on-primary` #FFFFFF
- `primary-container` **#BFE3C3** · `on-primary-container` #0B2211
- `secondary` **#7A6A4F** (bois/beige) · `secondary-container` **#F0E6D2** · `on-secondary-container` #2A2011
- `tertiary` **#8C4A3C** (terracotta discret, pour les accents « vidéo/alerte douce ») · `tertiary-container` **#FFDAD2**
- `surface` **#FCF9F4** (crème très léger) · `surface-container` **#F3EEE4** · `surface-container-high` #EDE7DA
- `outline` **#7A756C** · texte principal `on-surface` **#1C1B18** · erreur : rouge MD3 standard #BA1A1A (rare, réservé)
- Usage : fonds en `surface` ; cartes en `surface-container` ; l'élément clé du slide (un seul) en `primary-container` ; jamais plus de 3 couleurs visibles par diapositive.

**Typographie (échelle MD3)** :
- Titre de diapositive : *Headline Large* (~40 pt), Google Sans ou Roboto, graisse Medium, `on-surface`.
- « Kicker » au-dessus du titre : *Label Large* (~14 pt), MAJUSCULES, interlettrage +8 %, couleur `primary`.
- Corps : *Body Large* (~20 pt), Roboto Regular, interligne 1,4.
- Grands emplacements chiffrés : *Display Large* (~64 pt) pour le « — ».
- Notation d'échecs / identifiants techniques (FEN) : Roboto Mono, `on-secondary-container` sur fond `secondary-container`.

**Composants récurrents** :
- **Cartes** : coins arrondis 24 px, sans ombre dure (élévation 0–1), padding interne 24 px.
- **Chips** : entièrement arrondies, contour 1 px `outline`, texte *Label Medium*.
- **Chip d'emplacement** (pour les crochets) : contour pointillé, texte gris, icône `pending`.
- **Bandeau de pied de page** sur chaque diapositive : à gauche « Cavalier Data × FFE » (*Label Small*, `outline`), au centre zone réservée « Source : [·] », à droite numéro de diapositive.
- **Motif décoratif** : damier 8×8 très discret (deux tons de `surface`/`surface-container`, opacité ~40 %), placé en coin, jamais derrière du texte. Pièces d'échecs en caractères Unicode (♔ ♕ ♖ ♗ ♘ ♙) utilisées comme pictogrammes, couleur `primary` ou `secondary`.
- **Icônes Material Symbols** (rounded, outlined) : noms précisés slide par slide.

**Grille** : 12 colonnes, marges latérales 64 px, gouttières 24 px. Aérer : viser ≤ 60 % de surface occupée.

---

## DIAPOSITIVE 1 — Titre

**Mise en page** : deux zones. Gauche (7 colonnes) : bloc titre aligné à gauche, centré verticalement. Droite (5 colonnes) : visuel décoratif.

**Textes exacts**
- Kicker : `SOUTENANCE · PREUVE DE CONCEPT`
- Titre (*Display Small*, Medium) : **Un coach IA pour les ouvertures d'échecs**
- Sous-titre (*Title Medium*, `outline`) : Preuve de concept pour la Fédération Française des Échecs
- Ligne meta (*Body Medium*) : Richard Hugou — IA Engineer junior, Cavalier Data · Soutenance du [date] · Mission POC — 2 semaines

**Visuel (droite)** : damier 8×8 stylisé en deux tons (`surface-container` / `secondary-container`), légèrement incliné, débordant du bord droit ; trois pièces Unicode géantes (♘ ♗ ♖) en `primary`, posées sur le damier. Aucune ombre portée.

**Notes présentateur** : annonce du plan en une phrase : commande → problème → données → solution → démonstration → mesure → suite.

---

## DIAPOSITIVE 2 — La mission : qui, pour qui, pourquoi

**Mise en page** : kicker + titre en haut ; dessous, trois cartes de largeur égale sur une rangée ; petit schéma de relation sous les cartes.

**Textes exacts**
- Kicker : `LE CONTEXTE`
- Titre : **Une commande de la FFE, un POC en deux semaines**
- Carte 1 — icône `flag` — **Le client** : La FFE, fédération officielle des échecs en France. — [nb licenciés] licenciés *(chip : à sourcer)* — dont [part] de jeunes *(chip : à sourcer)*. Cap : les championnats d'Europe jeunes.
- Carte 2 — icône `engineering` — **Nous** : Cavalier Data, cabinet de conseil IA. Moi : IA Engineer junior, encadré par Alan, responsable technique.
- Carte 3 — icône `assignment` — **La commande** : Un POC en 2 semaines : démontrer la faisabilité et la valeur d'un agent d'entraînement aux ouvertures.

**Visuel** : sous les cartes, une ligne fine reliant trois pastilles : « FFE » → « Alan (Cavalier Data) » → « moi » ; flèches simples, *Label Medium*.

**Couleur** : carte 3 (la commande) en `primary-container` — c'est l'élément clé ; les deux autres en `surface-container`.

**Notes présentateur** : la FFE veut savoir si un agent peut faire travailler les ouvertures — la phase la plus codifiée du jeu ; deux semaines, objectif de démonstration, pas un produit fini.

---

## DIAPOSITIVE 3 — Le problème

**Mise en page** : kicker + titre ; grille 2×2 de quatre grandes tuiles identiques.

**Textes exacts**
- Kicker : `LE PROBLÈME`
- Titre : **La demande explose, l'accompagnement ne suit pas**
- Tuile 1 — icône `trending_up` — grand « — » *(chip : volume de la pratique en ligne, à sourcer)* — libellé : la pratique a explosé depuis [période] — ligne conclusive en `primary`, graisse Medium : **donc une génération apprend en ligne, seule.**
- Tuile 2 — icône `payments` — grand « — » *(chip : tarif horaire d'un entraîneur, à sourcer)* — libellé : un accompagnement humain cher et rare — **donc l'humain seul ne passe pas à l'échelle.**
- Tuile 3 — icône `all_inclusive` — grand « — » *(chip : combinatoire après quelques coups, à sourcer)* — libellé : des possibilités astronomiques dès l'ouverture — **donc on n'apprend pas par cœur : on apprend la théorie.**
- Tuile 4 — icône `location_on` — libellé : des espoirs répartis sur tout le territoire — **donc l'outil doit être disponible partout, à la demande.** *(pas d'emplacement chiffré sur cette tuile)*

**Structure interne d'une tuile** : icône en haut à gauche (`primary`) ; « — » en *Display Large* ; chip d'emplacement ; libellé *Body Medium* ; ligne « donc… » séparée par un filet fin `outline`.

**Notes présentateur** : chaque constat se termine par « donc » ; les valeurs seront sourcées en note de bas de diapositive.

---

## DIAPOSITIVE 4 — La problématique

**Mise en page** : diapositive « respiration », la plus vide du deck. Une seule grande carte centrale (8 colonnes, centrée) ; une rangée de quatre petites chips-cartes en dessous.

**Textes exacts**
- Kicker : `LA PROBLÉMATIQUE`
- Carte centrale (fond `primary-container`, texte *Headline Medium* centré, `on-primary-container`) :
  **« Comment offrir à chaque jeune espoir un retour de niveau entraîneur sur ses ouvertures, à la demande ? »**
- Quatre attentes (petites cartes égales, `surface-container`, icône + une ligne) :
  - `verified` — Des coups sûrs, validés par la théorie
  - `school` — Des explications compréhensibles
  - `smart_display` — Des ressources vidéo adaptées
  - `balance` — Une évaluation objective hors des sentiers battus

**Contrainte** : aucun terme technique sur cette diapositive (pas de « RAG », « LangGraph », « base vectorielle »).

**Notes présentateur** : la solution doit se déduire du besoin, pas l'inverse — le vocabulaire technique n'arrive que plus tard.

---

## DIAPOSITIVE 5 — Notre réponse (sans technique)

**Mise en page** : kicker + titre ; storyboard horizontal de quatre vignettes reliées par des flèches fines.

**Textes exacts**
- Kicker : `LA RÉPONSE`
- Titre : **Une IA-coach qui regarde l'échiquier avec l'élève**
- Vignette ① — icône `touch_app` — « Je joue un coup »
- Vignette ② — icône `menu_book` — « Elle me montre ce que la théorie recommande ici »
- Vignette ③ — icône `smart_display` — « Elle m'explique l'idée et me propose une vidéo »
- Vignette ④ — icône `query_stats` — « Si je quitte la théorie, elle évalue ma position et me dit pourquoi »

**Visuel** : chaque vignette est une carte verticale avec, en haut, un mini-damier 4×4 stylisé (deux tons) et un petit symbole d'échecs Unicode différent (♙ ♘ ♗ ♕) ; numérotation ①–④ en `primary`. La vignette ④ porte un liseré `tertiary` (c'est la bascule « hors théorie »).

**Notes présentateur** : l'élève n'est jamais jugé, il est guidé. Transition charnière à dire telle quelle : « Pour faire ça, cette IA ne peut rien inventer — il lui faut des données. Lesquelles, et où les trouver ? »

---

## DIAPOSITIVE 6 — Les données nécessaires : l'inventaire

**Mise en page** : kicker + titre ; tableau MD3 pleine largeur (5 rangées) ; la dernière rangée visuellement distincte.

**Textes exacts**
- Kicker : `LES DONNÉES · 1/3 — LE PAYSAGE`
- Titre : **Tout existe déjà : ouvert, massif, licite**
- Tableau (colonnes : **Besoin → Source → Volumétrie → Licence**) :
  1. Connaître les ouvertures → Référentiel public des ouvertures nommées → *(chip : volumétrie à confirmer)* → Licence libre
  2. Savoir ce que joue l'élite → Statistiques et parties de référence (base Lichess) → *(chip : volumétrie à confirmer)* → Licence libre
  3. Expliquer les idées → Corpus encyclopédique (wiki d'ouvertures) → *(chip : à inventorier)* → Libre, **attribution requise**
  4. Montrer des vidéos → Métadonnées via l'API officielle YouTube → *(chip : contrainte de quota)* → CGU : liens et lecture intégrée uniquement
  5. **+ Un outil de vérité** → Le moteur Stockfish : évalue n'importe quelle position → — → Open source
- Phrase de synthèse sous le tableau (*Title Small*, `primary`) : **Notre valeur ajoutée : sélectionner, structurer, brancher.**

**Couleur** : rangées 1–4 sur `surface-container` ; rangée 5 sur `secondary-container` avec icône `construction` (c'est un outil, pas une donnée — la distinction doit se voir).

**Notes présentateur** : annoncer le bloc : « trois diapositives de données : le paysage, notre sélection, notre pipeline ».

---

## DIAPOSITIVE 7 — Le jeu de données du POC

**Mise en page** : kicker + titre ; deux zones graphiques côte à côte (6 colonnes chacune) ; bandeau de trois chips en dessous.

**Textes exacts**
- Kicker : `LES DONNÉES · 2/3 — NOTRE SÉLECTION`
- Titre : **Ce qu'on indexe, exactement**
- Zone graphique A — étiquette : « Documents retenus, par source » ; sous-étiquette : *(chip : graphique issu de l'EDA — à mesurer)*
- Zone graphique B — étiquette : « Couverture des ouvertures cibles » ; sous-étiquette : *(chip : graphique issu de l'EDA — à mesurer)*
- Bandeau nettoyage (3 chips d'emplacement) : « pages écartées : — » · « doublons éliminés : — » · « langues : — »
- Phrase de synthèse (*Title Small*, `primary`) : **Un corpus petit, propre et traçable — la qualité se joue ici.**

**Visuel — IMPORTANT** : les deux zones graphiques sont des **maquettes volontairement neutres** : cadre au contour `outline`, fond `surface-container`, barres toutes de hauteur identique et hachurées (aucune donnée simulée), icône `bar_chart` (zone A) et `grid_on` (zone B) en filigrane. Elles ne doivent surtout pas ressembler à de vraies données.

**Notes présentateur** : périmètre assumé — quelques ouvertures majeures, pas tout le répertoire ; les graphiques réels remplaceront les maquettes après l'EDA.

---

## DIAPOSITIVE 8 — Du brut à l'index : le pipeline

**Mise en page** : kicker + titre ; frise horizontale de cinq étapes ; dessous, deux colonnes : règles (gauche, 7 col.) et encadré rapport (droite, 5 col.).

**Textes exacts**
- Kicker : `LES DONNÉES · 3/3 — NOTRE PIPELINE`
- Titre : **Un pipeline reproductible, qui se contrôle lui-même**
- Frise (5 pastilles reliées par des flèches) : **Extraire → Nettoyer → Découper → Vectoriser → Indexer**
- Règles (liste à icônes) :
  - `key` — Chaque position est normalisée en **FEN** — l'identifiant pivot de tout le système *(mot « FEN » en Roboto Mono sur fond `secondary-container`)*
  - `content_cut` — Découpage en passages courts, **sans jamais couper une suite de coups**
  - `sell` — Métadonnées systématiques : source, licence, ouverture
  - `filter_alt` — Déduplication
- Encadré droite (carte `surface-container-high`, icône `fact_check`) : titre **Rapport d'ingestion à chaque exécution** ; trois lignes « — » avec chips : « volumes traités : à mesurer » · « éléments écartés : à mesurer » · « durée : à mesurer ».

**Couleur** : la pastille « Vectoriser » de la frise en `primary-container` (c'est l'étape signature) ; les autres en `surface-container`.

**Notes présentateur** : le FEN relie l'échiquier, la théorie, le corpus et le moteur ; les paramètres de découpage sont des choix mesurés — revoir diapositive 12.

---

## DIAPOSITIVE 9 — Pourquoi un agent outillé

**Mise en page** : kicker + titre ; deux colonnes contrastées de même taille ; bandeau punchline pleine largeur en bas.

**Textes exacts**
- Kicker : `L'APPROCHE`
- Titre : **Un LLM seul joue mal ; un LLM outillé devient fiable**
- Colonne gauche — carte au contour `outline`, sans remplissage — titre : **LLM seul** — liste (icône `close` grise devant chaque item) :
  - Connaissances figées
  - Coups illégaux constatés en compétition *(chip : référence Kaggle, à sourcer)*
  - Aucune source vérifiable
  - Niveau de jeu faible
- Colonne droite — carte `primary-container` — titre : **LLM outillé — notre choix** — liste (icône `check` en `primary` devant chaque item) :
  - Les coups viennent de la **théorie**
  - L'évaluation vient du **moteur**
  - Les explications viennent d'un **corpus cité**
  - Le LLM **comprend et rédige**
- Bandeau bas (*Headline Small*, centré) : **« Chez nous, le LLM n'invente jamais un coup. »**

**Notes présentateur** : compétition récente LLM vs LLM aux échecs, sans outils : coups illégaux malgré position et coups légaux fournis — démonstration par l'absurde ; conséquence : chaque information a sa source dédiée.

---

## DIAPOSITIVE 10 — Architecture

**Mise en page** : kicker + titre ; grand schéma central (10 colonnes) ; bandeau de services en bas.

**Textes exacts et schéma (à dessiner en boîtes arrondies reliées par des flèches fines)** :
- Kicker : `LA TECHNO`
- Titre : **Un graphe de décision qui route chaque position vers la bonne source**
- Schéma, de gauche à droite :
  1. Boîte « Valider la position » → 2. Boîte « Identifier l'ouverture » → 3. **Losange** « En théorie ? » (fond `secondary-container`)
  4. Branche **Oui** (vers le haut) : boîte « Coups théoriques — Lichess » (fond `primary-container`)
  5. Branche **Non** (vers le bas) : boîte « Évaluation — Stockfish » (fond `primary-container`)
  6. Convergence → « Contexte documentaire — Milvus » (fond `primary-container`) → « Vidéos — YouTube » (fond `primary-container`) → « Synthèse — LLM » (fond `tertiary-container`) → « **Réponse sourcée** » (contour épais `primary`)
- Légende discrète sous le schéma : vert = sources de vérité · terracotta = rédaction · le LLM ne choisit jamais un coup.
- Bandeau services (6 chips) : Angular · FastAPI + LangGraph · Milvus · MongoDB · Stockfish embarqué · Suivi d'expériences

**Notes présentateur** : raconter le trajet d'UNE position, une phrase par brique ; pourquoi un graphe : le routage conditionnel testable est exactement ce que le besoin exige.

---

## DIAPOSITIVE 11 — Démo

**Mise en page** : diapositive minimale (on quitte l'écran pour l'application). Titre + carte « commande » + quatre points numérotés.

**Textes exacts**
- Kicker : `LA PREUVE · DÉMONSTRATION`
- Titre : **En local, en une commande**
- Carte façon terminal (fond `surface-container-high`, Roboto Mono, coin arrondi 16 px) : `docker compose up`
- Les quatre moments à observer (liste numérotée ①–④, *Body Large*) :
  ① La théorie sur une position d'ouverture · ② L'explication sourcée + la vidéo · ③ Une question libre · ④ La sortie de théorie → l'évaluation moteur
- Petite ligne en bas (*Label Medium*, `outline`) : Plan B : captures et enregistrement — la démonstration ne dépend ni du réseau ni des quotas.

**Notes présentateur** : dérouler le script de démo (document 08) ; en cas d'aléa, tout le scénario est servi par les caches.

---

## DIAPOSITIVE 12 — Résultats : la mesure avant l'intuition

**Mise en page** : kicker + titre ; tableau (7 colonnes de large) à gauche, zone capture (5 colonnes) à droite.

**Textes exacts**
- Kicker : `LA PREUVE · MESURE`
- Titre : **On mesure, on ne « sent » pas**
- Tableau (rangées × 2 colonnes de valeurs) :
  | Indicateur | Version initiale | Version améliorée |
  | Pertinence de la recherche (jeu d'évaluation dédié) | — *(chip : à mesurer)* | — *(chip : à mesurer)* |
  | Coups illégaux proposés | — | — |
  | Latence ressentie | — | — |
  | Coût par interaction | — | — |
- Zone droite : cadre `outline` avec icône `monitoring` en filigrane, étiquette : « Capture de l'outil de suivi des expériences — *(chip : à insérer)* »
- Phrase de synthèse (*Title Small*, `primary`) : **Toute valeur affichée ici sortira d'un run tracé — d'aucun autre endroit.**

**Notes présentateur** : le protocole d'abord : jeu d'évaluation étiqueté, y compris questions pièges où la bonne réponse est de s'abstenir ; chaque configuration = un run tracé (paramètres, métriques, artefacts).

---

## DIAPOSITIVE 13 — La plateforme : mise à disposition & maintenance

**Mise en page** : gauche (6 colonnes) : maquette d'interface simplifiée ; droite (6 colonnes) : liste exploitation.

**Textes exacts**
- Kicker : `LE PRODUIT`
- Titre : **Un produit, pas un notebook**
- Maquette gauche (wireframe plat, traits `outline`, fonds `surface-container`) : un grand carré « Échiquier » (avec mini-damier stylisé) et, à sa droite, trois panneaux empilés étiquetés : « Coups recommandés » · « L'explication et ses sources » · « Vidéos » ; un quatrième panneau discret en dessous : « Évaluation (hors théorie) » avec liseré `tertiary`.
- Liste droite (icône + une ligne chacune) :
  - `rocket_launch` — Lancement en une commande
  - `save` — Données persistantes entre les redémarrages
  - `cached` — Quotas protégés par des caches
  - `update` — Connaissance mise à jour en relançant l'ingestion — sans réentraînement
  - `receipt_long` — Chaque réponse traçable

**Notes présentateur** : côté élève, l'information est organisée par usage : ce que je peux jouer, pourquoi, avec quoi approfondir.

---

## DIAPOSITIVE 14 — Et demain ? L'analyse vidéo (conçue, pas développée)

**Mise en page** : quatre bandes horizontales : idée / limites / schéma / verdict.

**Textes exacts**
- Kicker : `LA SUITE · CONCEPTION`
- Titre : **Des vidéos aux positions indexées — conçu et chiffré, pas développé**
- Bande 1 — l'idée (une ligne, *Title Medium*) : Relier chaque position d'échecs à **la minute exacte** d'une vidéo qui l'explique.
- Bande 2 — trois cartes « limites », dans cet ordre :
  - `gavel` — **Juridique (structurante)** : CGU YouTube — pas de téléchargement de vidéos. *(badge : « limite n°1 », liseré `tertiary`)*
  - `visibility` — **Technique** : fiabilité de la lecture d'échiquier selon le type d'image.
  - `payments` — **Économique** : coût proportionnel au volume *(chip : étude jointe — hypothèses posées)*.
- Bande 3 — mini-schéma en trois groupes reliés : « Agent (existant) » ↔ « Serveurs d'outils **MCP** : vidéos · vision · échecs · connaissances » ↔ « Pipeline d'analyse + stockages » ; étiquette sous le schéma : *MCP : un standard ouvert — chaque outil devient réutilisable par tout agent futur de la fédération.*
- Bande 4 — verdict (bandeau `primary-container`, *Title Medium*) : **Faisable en MVP restreint : vidéos sous licence libre + transcriptions d'abord.**

**Notes présentateur** : commencer par la limite juridique parce qu'elle structure l'architecture ; l'étude chiffre un MVP prudent avec des critères d'arrêt.

---

## DIAPOSITIVE 15 — Roadmap & risques

**Mise en page** : moitié haute : frise chronologique à trois jalons ; moitié basse : tableau compact risque → mitigation.

**Textes exacts**
- Kicker : `LA SUITE · TRAJECTOIRE`
- Titre : **Le POC est l'étape 1 d'une trajectoire réaliste**
- Frise (trois jalons sur une ligne, pastilles reliées) :
  - **POC — aujourd'hui** (pastille pleine `primary`) : routage théorie/moteur · réponses sourcées · livraison en une commande
  - **V1** (pastille contour) : répertoire élargi · comptes utilisateurs · évaluation continue · hébergement adapté à un public mineur
  - **V2** (pastille contour) : l'analyse vidéo, en commençant par le MVP le moins risqué
- Tableau risques (3 rangées, 2 colonnes) :
  - Dépendance aux services tiers → caches + modes dégradés (déjà en place)
  - Qualité du corpus → évaluation permanente sur jeu de test (déjà en place)
  - Cadre juridique vidéo → périmètre licence libre d'abord (décision de conception)

**Notes présentateur** : les mitigations des trois risques existent déjà dans le POC — ce ne sont pas des promesses.

---

## DIAPOSITIVE 16 — Conclusion

**Mise en page** : symétrique de la diapositive 4 (respiration) : une grande carte centrale, une rangée de chips, un petit tableau discret, la ligne de remerciement.

**Textes exacts**
- Kicker : `CONCLUSION`
- Carte centrale (`primary-container`, *Headline Small* centré) : **La promesse : un retour de niveau entraîneur, à la demande.**
- Rangée « démontré » (4 chips avec icône `check`) : Routage théorie/moteur · Réponses sourcées · Livraison en une commande · Protocole de mesure
- Petit tableau « Objectifs O1–O6 » : six pastilles grises identiques avec *(chip : statuts à remplir après mesure)* — ne pas colorer en vert/orange tant que les mesures n'existent pas.
- Ligne finale (*Title Medium*, centré) : **Merci — place aux questions.**

**Notes présentateur** : une phrase de bilan (« la fiabilité d'un agent vient de la répartition des rôles entre le modèle et ses outils ») puis ouvrir les questions.

---

## ANNEXES (diapositives de secours — même gabarit, kicker `ANNEXE`)

- **A1 — Choix techniques & alternatives** : tableau 3 colonnes (brique / choix / alternatives écartées et pourquoi), une rangée par brique.
- **A2 — Le graphe en détail** : version agrandie du schéma de la diapositive 10 avec l'état partagé listé dans une carte latérale.
- **A3 — Protocole d'évaluation** : composition du jeu de test (directes / par position / pièges), métriques suivies, cellules valeurs en « — » *(à mesurer)*.
- **A4 — Coûts du système vidéo** : tableau à 3 scénarios de volume, toutes les valeurs en « — » *(chips : hypothèses de l'étude jointe)*.
- **A5 — Conformité** : trois cartes : licences des données (libre / attribution requise / CGU) · règle « liens et lecture intégrée uniquement » · public mineur : minimisation des données.
- **A6 — Contraintes matérielles** : liste sobre des contraintes du poste et de leurs conséquences de conception *(sans chiffres : libellés + chips « détail en dossier »)*.

---

## RAPPELS FINAUX POUR GEMINI
1. Ne jamais remplir un crochet `[…]` ni un « — » par une valeur inventée.
2. Un seul élément en `primary-container` par diapositive (l'élément clé).
3. Pas de photos, pas d'ombres dures, pas de dégradés ; icônes Material Symbols rounded uniquement.
4. Kicker + titre + pied de page identiques sur toutes les diapositives ; numéroter.
5. Textes fournis = textes définitifs : ne pas reformuler, ne pas traduire, ne pas compléter.
