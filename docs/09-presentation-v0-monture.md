# 09 — Première mouture de la présentation (v0, sans chiffres)

> **Objet** : vérifier l'articulation des idées. Tout emplacement de chiffre est un crochet `[…]` — il sera rempli par une **mesure** (convention [MESURE]) ou une **source** (convention ⚠️), jamais inventé.
> **Format par slide** : *À l'écran* = le texte tel qu'il apparaîtra (max 5 lignes) ; *À l'oral* = ce que je dis, mot pour mot ou presque ; *→* = la phrase de transition vers le slide suivant.

---

## Slide 1 — Titre *(~30 s)*

**À l'écran**
> **Un coach IA pour les ouvertures d'échecs**
> Preuve de concept pour la Fédération Française des Échecs
> Richard Hugou — IA Engineer junior, Cavalier Data
> Soutenance du [date] · Mission POC — 2 semaines

**À l'oral**
« Bonjour. Je vais vous présenter une preuve de concept réalisée en deux semaines pour la Fédération Française des Échecs : un agent IA qui accompagne de jeunes compétiteurs dans l'apprentissage des ouvertures. Je vais vous raconter la commande, le problème qu'elle pose, les données qui permettent d'y répondre, la solution construite — et je vous la montrerai en fonctionnement. »

**→** « D'abord, le contexte : qui demande quoi, et pourquoi maintenant. »

---

## Slide 2 — La mission : qui, pour qui, pourquoi *(~1 min)*

**À l'écran** *(3 blocs)*
> **Le client** — La FFE, fédération officielle des échecs en France : [nb licenciés] licenciés, dont [part] de jeunes. Objectif : les championnats d'Europe jeunes.
> **Nous** — Cavalier Data, cabinet de conseil IA. Moi : IA Engineer junior, encadré par Alan, responsable technique.
> **La commande** — Un POC en 2 semaines : démontrer la faisabilité et la valeur d'un agent d'entraînement aux ouvertures.

**À l'oral**
« La FFE prépare les championnats d'Europe jeunes. Elle veut savoir si un agent intelligent peut aider ses espoirs à travailler leurs ouvertures — c'est la phase de la partie la plus codifiée, celle où un bon accompagnement fait la différence. Cavalier Data est missionné ; Alan, mon responsable technique, me confie le POC : deux semaines, un objectif de démonstration, pas un produit fini. »

**[Visuel]** mini-organigramme : FFE → Alan → moi.

**→** « Pourquoi ce besoin émerge-t-il maintenant ? Trois constats. »

---

## Slide 3 — Le problème *(~1 min 30)*

**À l'écran** *(4 tuiles, chacune : constat → « donc »)*
> [volume de la pratique en ligne, à sourcer] — la pratique a explosé depuis [période] → **donc** une génération entière apprend désormais en ligne, seule.
> [tarif horaire d'un entraîneur, à sourcer] et des créneaux limités → **donc** l'accompagnement humain ne passe pas à l'échelle.
> [combinatoire du jeu après quelques coups, à sourcer] → **donc** on n'apprend pas les échecs par cœur : on apprend la **théorie**.
> Des espoirs répartis sur tout le territoire → **donc** l'outil doit être disponible partout, à la demande.

**À l'oral**
« Trois tensions. La pratique explose — chiffre à l'appui — mais elle se fait en ligne, sans retour qualifié. L'accompagnement humain existe, mais il est cher et rare : il ne suit pas la demande. Et la nature même du jeu — la combinatoire devient astronomique en quelques coups — fait qu'il n'y a rien à mémoriser bêtement : il y a un corpus de théorie à comprendre. Chaque constat pousse vers la même conclusion : il faut un accompagnement qui soit disponible, qualifié, et adossé à la théorie. »

**[Visuel]** 4 grandes tuiles ; les valeurs seront sourcées en note de bas de slide.

**→** « D'où la question qui structure tout le projet. »

---

## Slide 4 — La problématique *(~45 s)*

**À l'écran** *(la question seule, encadrée, puis 4 attentes)*
> **« Comment offrir à chaque jeune espoir un retour de niveau entraîneur sur ses ouvertures, à la demande ? »**
>
> Ce retour doit : proposer des coups **sûrs, validés par la théorie** · **expliquer** les idées derrière les coups · s'appuyer sur des **ressources pédagogiques** adaptées · rester **objectif** quand on sort des sentiers battus.

**À l'oral**
« Voilà la problématique, et les quatre attentes qui en découlent : des coups fiables, des explications, des ressources, et une évaluation honnête quand l'élève improvise. Notez qu'à ce stade je n'ai encore rien dit de technique — c'est volontaire : la solution doit se déduire du besoin, pas l'inverse. »

*(Interdit sur ce slide : RAG, LangGraph, tout vocabulaire d'implémentation.)*

**→** « Notre réponse tient en une image. »

---

## Slide 5 — Notre réponse (toujours sans technique) *(~1 min)*

**À l'écran**
> **Une IA-coach qui regarde l'échiquier avec l'élève.**
> ① Je joue un coup → ② elle me montre ce que la théorie recommande ici → ③ elle m'explique l'idée et me propose une vidéo → ④ si je quitte la théorie, elle évalue objectivement ma position et me dit pourquoi.

**À l'oral**
« L'expérience visée : l'élève joue, l'IA suit la position en continu. Tant qu'on est dans la théorie, elle montre les coups reconnus et explique les idées. Dès qu'on en sort — un coup créatif, ou une erreur — elle bascule sur une évaluation objective. L'élève n'est jamais jugé : il est guidé. »

**[Visuel]** storyboard en 4 vignettes autour d'un échiquier.

**→ (transition à répéter, c'est la charnière du deck)** « Pour faire ça, cette IA ne peut rien inventer : chaque coup montré, chaque explication, chaque évaluation doit venir de quelque part. La vraie question devient : **de quelles données a-t-elle besoin, et où les trouver ?** »

---

## Slide 6 — Les données nécessaires : l'inventaire *(~1 min 30)*

**À l'écran** *(tableau : besoin → source → volumétrie → licence)*
> Connaître les ouvertures → référentiel public des ouvertures nommées → [volumétrie] → licence libre
> Savoir ce que joue l'élite → statistiques et parties de référence (base Lichess) → [volumétrie] → licence libre
> Expliquer les idées → corpus encyclopédique (wiki d'ouvertures) → [volumétrie à inventorier] → licence libre avec attribution
> Montrer des vidéos → métadonnées YouTube via l'API officielle → [contrainte de quota] → CGU : liens et lecture intégrée uniquement
> **+ un outil de vérité** → le moteur Stockfish, pour évaluer n'importe quelle position → open source

**À l'oral**
« Constat clé du cadrage : tout existe déjà, ouvert, massif, et légalement utilisable. Le répertoire des ouvertures est public. La pratique réelle des maîtres est disponible via Lichess. Le savoir pédagogique est sur des wikis sous licence libre — à condition de citer les sources, ce que l'agent fera. Les vidéos sont accessibles par l'API officielle. Et pour évaluer une position quelconque, il existe un moteur open source plus fort que n'importe quel humain. Notre valeur ajoutée n'est donc pas de créer de la donnée : c'est de **sélectionner, structurer et brancher** ces sources. »

**→** « Voilà le paysage. Maintenant, ce qu'on a réellement retenu et indexé pour le POC. »

---

## Slide 7 — Le jeu de données du POC *(~1 min 30 — slide EDA n°1)*

**À l'écran**
> **Ce qu'on indexe, exactement.**
> [graphique : nombre de documents retenus, par source]
> [graphique : couverture des ouvertures cibles du POC]
> Nettoyage : [pages écartées] écartées, [doublons] doublons éliminés, [langues] langues.

**À l'oral**
« Périmètre assumé du POC : un petit nombre d'ouvertures majeures, choisies avec le métier, plutôt que tout le répertoire. Ce slide montrera trois choses issues de l'analyse exploratoire : de quoi le corpus est composé, la preuve qu'il couvre bien les ouvertures annoncées, et ce que le nettoyage a écarté. Le message : un corpus **petit mais propre et traçable** — parce que la qualité des réponses de l'agent se joue ici, pas dans le modèle. »

**→** « Comment on passe de pages wiki brutes à un index interrogeable : le pipeline. »

---

## Slide 8 — Du brut à l'index : le pipeline ETL *(~1 min 30 — slide EDA n°2)*

**À l'écran**
> **Extraire → Nettoyer → Découper → Vectoriser → Indexer** *(schéma fléché)*
> Règles : chaque position normalisée en **FEN** (l'identifiant pivot de tout le système) · découpage en passages courts sans jamais couper une suite de coups · métadonnées systématiques (source, licence, ouverture) · déduplication.
> Chaque exécution produit un **rapport chiffré** : [emplacements des mesures d'ingestion].

**À l'oral**
« Le pipeline est rejouable et se contrôle lui-même : à chaque exécution, il compte ce qu'il a pris, transformé, écarté. Deux règles méritent une seconde : d'abord, tout est indexé sur la notation FEN — la « carte d'identité » d'une position — c'est elle qui relie l'échiquier, la théorie, le corpus et le moteur. Ensuite, le découpage du texte respecte la structure du contenu : on ne coupe jamais une variante en deux. Les paramètres exacts — tailles, recouvrement, modèle de vectorisation — sont des choix **mesurés**, j'y reviens au slide résultats. »

**→** « Les données sont prêtes. Reste une question de fond avant l'architecture : pourquoi un *agent outillé*, et pas simplement un grand modèle de langage à qui on demande de jouer ? »

---

## Slide 9 — Pourquoi un agent outillé *(~1 min 30 — la justification de l'approche)*

**À l'écran** *(2 colonnes)*
> **LLM seul** : connaissances figées · propose des coups illégaux [référence compétition Kaggle, à sourcer] · aucune source vérifiable · niveau de jeu faible.
> **LLM outillé (notre choix)** : les coups viennent de la **théorie** · l'évaluation vient du **moteur** · les explications viennent d'un **corpus cité** · le LLM comprend la demande et rédige.
> **Chez nous, le LLM n'invente jamais un coup.**

**À l'oral**
« Une compétition récente a fait s'affronter les grands modèles de langage aux échecs, sans outils : position transmise en notation standard, historique, coups légaux fournis. Résultat — à sourcer précisément dans le dossier — des coups illégaux et un niveau faible. C'est la démonstration par l'absurde : le LLM est excellent pour comprendre et expliquer, mauvais pour être une source de vérité. Notre architecture en tire la conséquence : chaque type d'information a sa source dédiée, et le LLM orchestre et pédagogise. C'est le principe de conception numéro un du projet. »

**→** « Voilà pourquoi l'architecture a la forme que je vais vous montrer. »

---

## Slide 10 — Architecture *(~2 min — la techno, enfin)*

**À l'écran**
> [schéma du graphe : valider la position → identifier l'ouverture → **routeur** : en théorie ? → oui : coups théoriques (Lichess) / non : évaluation (Stockfish) → contexte documentaire (Milvus) → vidéos (YouTube) → synthèse (LLM) → réponse sourcée]
> Bandeau services : Angular · FastAPI + LangGraph · Milvus · MongoDB · Stockfish embarqué · [suivi d'expériences]

**À l'oral** *(raconter le trajet d'UNE position, une phrase par brique)*
« Suivons un coup joué par l'élève. L'échiquier Angular envoie la position au backend FastAPI. Le graphe LangGraph — c'est le chef d'orchestre — valide d'abord la position, identifie l'ouverture, puis **route** : si la position est connue de la théorie, il interroge Lichess ; sinon, il demande une évaluation à Stockfish. Dans les deux cas, il enrichit avec le corpus indexé dans Milvus et des vidéos, puis le LLM rédige une réponse — avec ses sources. MongoDB tient les caches et les sessions ; chaque exécution laisse une trace consultable. Pourquoi un graphe plutôt qu'un enchaînement linéaire ? Parce que ce **routage conditionnel testable** est exactement ce que le besoin exige. »

**→** « Assez de schémas — regardons-le fonctionner. »

---

## Slide 11 — Démo *(~5–8 min)*

**À l'écran**
> **Une commande pour lancer. Quatre moments à observer :**
> ① la théorie sur une position d'ouverture · ② l'explication sourcée + la vidéo · ③ une question libre · ④ la sortie de théorie → évaluation moteur.

**À l'oral**
« Je lance l'application d'une seule commande. [Déroulé du script de démo, doc 08 : position d'Italienne pour la théorie et le contexte ; question libre au chat ; coup douteux pour montrer la bascule vers le moteur — en montrant au passage que la réponse cite ses sources.] Si un aléa survient : tout le scénario est servi par les caches, la démo ne dépend ni du réseau ni des quotas. »

**→** « Vous l'avez vu fonctionner. Maintenant : comment je *prouve* qu'il fonctionne bien ? »

---

## Slide 12 — Résultats : la mesure avant l'intuition *(~1 min 30)*

**À l'écran** *(tableau avant/après, valeurs à remplir depuis les runs)*
> | Indicateur | Version initiale | Version améliorée |
> |---|---|---|
> | Pertinence de la recherche (jeu d'évaluation dédié) | [mesure] | [mesure] |
> | Coups illégaux proposés | [mesure] | [mesure] |
> | Latence ressentie | [mesure] | [mesure] |
> | Coût par interaction | [mesure] | [mesure] |
> *(capture de l'outil de suivi des expériences)*

**À l'oral**
« Le protocole d'abord, les chiffres ensuite. J'ai construit un jeu d'évaluation de questions étiquetées — y compris des questions pièges hors corpus, où la bonne réponse est de s'abstenir. Chaque configuration du système est un *run* tracé : paramètres, métriques, artefacts. Le tableau compare la première version fonctionnelle à la version améliorée — et toute valeur affichée ici sortira de ces runs, d'aucun autre endroit. C'est ce qui distingue un POC démontrable d'une jolie démo. »

**→** « Reste à voir comment tout cela est mis à disposition et vit dans le temps. »

---

## Slide 13 — La plateforme : mise à disposition & maintenance *(~1 min 30)*

**À l'écran**
> [capture UI annotée : échiquier · panneau « coups recommandés » · « l'explication et ses sources » · « vidéos » · « évaluation » si hors théorie]
> Exploitation : lancement en une commande · données persistantes · quotas protégés par caches · index rafraîchi périodiquement · traces consultables.

**À l'oral**
« Côté élève : un échiquier, et un panneau unique où l'information est organisée par usage — ce que je peux jouer, pourquoi, avec quoi approfondir. Côté exploitation : l'installation tient en une commande ; les données survivent aux redémarrages ; les appels externes passent par des caches qui protègent les quotas ; la connaissance se met à jour en relançant l'ingestion, pas en réentraînant quoi que ce soit ; et chaque réponse est traçable. C'est pensé comme un petit produit, pas comme un notebook. »

**→** « Ce POC ouvre une suite naturelle — c'est la deuxième partie de la commande d'Alan. »

---

## Slide 14 — Et demain ? L'analyse vidéo (conçue, pas développée) *(~2 min)*

**À l'écran**
> **L'idée** : transformer les vidéos pédagogiques en positions indexées → « cette position est expliquée à telle minute de telle vidéo ».
> **3 limites majeures** : juridique (CGU YouTube : pas de téléchargement) · technique (fiabilité de la lecture d'échiquier selon le type d'image) · économique (coût proportionnel au volume : [étude jointe]).
> [schéma simplifié : agent ↔ serveurs d'outils MCP ↔ pipeline d'analyse ↔ stockages]
> **Verdict** : faisable en MVP restreint — vidéos sous licence libre + transcriptions d'abord.

**À l'oral**
« La FFE aimerait aller plus loin : que l'agent pointe la minute exacte d'une vidéo où la position de l'élève est expliquée. J'ai conçu ce système sans le développer — note détaillée, architecture, étude de coûts. Je commence volontairement par la limite juridique, parce qu'elle est structurante : on ne télécharge pas des vidéos YouTube, donc l'architecture se construit autour de ce qui est licite — licences libres, transcriptions, contenus fédéraux. Techniquement, l'architecture s'appuie sur MCP, un standard ouvert qui rend chaque outil — vision, échecs, base de connaissances — réutilisable par n'importe quel agent futur de la fédération. L'étude chiffre un MVP prudent et des critères d'arrêt avant chaque étape suivante. »

**→** « Ce qui donne la trajectoire d'ensemble. »

---

## Slide 15 — Roadmap & risques *(~1 min)*

**À l'écran**
> **POC (aujourd'hui)** → **V1** : élargir le répertoire, comptes utilisateurs, évaluation continue, hébergement adapté à un public mineur → **V2** : l'analyse vidéo, en commençant par le MVP le moins risqué.
> **3 risques suivis** : dépendance aux services tiers → caches + modes dégradés · qualité du corpus → évaluation permanente · cadre juridique vidéo → périmètre licence libre d'abord.

**À l'oral**
« Le POC est l'étape un d'une trajectoire volontairement incrémentale : chaque étape a ses critères d'entrée et de sortie. Et les trois risques principaux ont déjà leur mitigation en place dans le POC — ce ne sont pas des promesses. »

**→** « Pour conclure. »

---

## Slide 16 — Conclusion *(~1 min)*

**À l'écran**
> **La promesse** : un retour de niveau entraîneur, à la demande.
> **Démontré** : le routage théorie/moteur · des réponses sourcées · la livraison en une commande · un protocole de mesure.
> [tableau objectifs O1–O6 : statut à remplir]
> **Merci — place aux questions.**

**À l'oral**
« En deux semaines : un agent qui ne propose que des coups issus de la théorie, qui explique en citant ses sources, qui bascule sur une évaluation objective hors théorie, livré en une commande, et — surtout — mesurable. Ce que j'en retiens : la fiabilité d'un agent vient de la répartition des rôles entre le modèle et ses outils, et sans évaluation chiffrée, on ne sait rien. Merci — j'attends vos questions. »

---
---

# Lecture critique de cette v0 (l'articulation tient-elle ?)

## Ce qui tient bien
1. **La colonne vertébrale est saine** : besoin → problématique → réponse sans techno → données → justification de l'approche → architecture → preuve (démo) → preuve (mesure) → produit → suite. Chaque slide répond à une question que le précédent a fait naître — le test « sans chiffres » le confirme : le récit reste compréhensible.
2. **Les deux charnières demandées existent et sont écrites** (5→6 « il lui faut des données », 9→10 « voilà pourquoi cette architecture ») — à répéter telles quelles.
3. **Slide 12 sans chiffres reste crédible** parce qu'il présente un *protocole* (gold set, runs tracés, abstention sur questions pièges) : c'est la bonne posture — les valeurs tomberont dedans.

## Points de vigilance (à trancher avant la v1)
1. **Le slide 3 est le plus dépendant du sourcing** : sans ses chiffres réels, c'est le seul slide « creux » de la v0. Il est urgent de sourcer ses 3–4 valeurs (tâche T0) — tout le pathos du problème repose dessus.
2. **Tunnel data 6-7-8** : trois slides de données d'affilée peuvent perdre un jury pressé. Mitigation intégrée : trois angles distincts (6 = *où trouver*, 7 = *ce qu'on a pris*, 8 = *comment on l'a rendu propre*) — l'annoncer à l'oral en entrant dans le slide 6 (« trois slides de données : le paysage, notre sélection, notre pipeline »).
3. **Position du slide 9** : la justification « agent outillé » arrive après les données. C'est conforme à notre méthode (les données d'abord) et ça fonctionne comme pont vers l'architecture ; mais si en répétition la coupure 8→9 paraît abrupte, l'alternative est de glisser 9 entre 5 et 6. À tester chrono en main — ne changer qu'après une répétition réelle.
4. **La démo (11) avant les résultats (12)** : bon pour l'énergie, mais la couture doit être dite explicitement (« vous l'avez vu fonctionner ; maintenant comment je prouve qu'il fonctionne bien ») — elle est écrite, ne pas l'improviser.
5. **Slide 14 : une seule respiration** pour bénéfices + limites + MCP + coûts, c'est dense. Tenir la hiérarchie choisie (juridique d'abord, le reste suit) et renvoyer les détails aux annexes A4/A5.

## Prochaine itération (v1)
- Remplir les crochets du slide 3 et du slide 6 (sourcing T0) — le reste attend les mesures.
- Répéter à voix haute avec chrono : cible ~20 min hors questions ; ajuster d'abord en coupant de l'oral, jamais en ajoutant du texte à l'écran.
- Ensuite seulement : passage en support visuel (pptx/HTML) — la v0 est un script, pas une maquette graphique.
