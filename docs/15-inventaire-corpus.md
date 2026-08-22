# 15 — Inventaire du corpus (T0) : les comptes exacts

> Réalisé le **2026-08-22**, en lecture seule via les APIs officielles (aucun scraping). C'est l'étape « inventaire » d'É3 : on compte ce qui existe, on n'extrait rien encore. Ces chiffres alimentent les diapos 4–5 et fondent la décision de périmètre (liste des ouvertures cibles).

## 1. Résultats

| Source | Méthode de comptage | Résultat |
|---|---|---|
| **Référentiel `lichess-org/chess-openings`** | Téléchargement des 5 TSV (a–e), comptage des lignes moins en-têtes | **3 810 ouvertures nommées** (a: 817, b: 772, c: 1 250, d: 614, e: 357) |
| **Wikipédia FR** — arbre `Catégorie:Ouverture d'échecs` | API MediaWiki `list=categorymembers`, récursif ≤ 3 niveaux, **articles dédupliqués par titre**, catégories Projet:/Portail: exclues | **225 articles uniques** |
| **Wikibooks EN** — « Chess Opening Theory » | API MediaWiki `list=allpages` avec préfixe, pagination suivie | **3 026 pages** |

Répartition FR notable : Ouverture du pion roi 109 · Début ouvert 54 · Gambits 48 · Pion dame 45 · Sicilienne 33 · Irrégulières 32 · Indiennes 18 · Espagnole 15.

## 2. Ce que ces chiffres changent

- **L'estimation « quelques centaines d'articles FR » est confirmée (225)** — le corpus FR entier tient dans le POC si on veut ; la sélection ~100–150 pages du plan initial reste pertinente en y ajoutant les pages EN des ouvertures cibles.
- **Wikibooks EN (3 026 pages) est trop gros pour tout prendre** : c'est bien la granularité par ligne qui compte — on n'y prendra que les sous-arbres des ouvertures cibles.
- **Le référentiel (3 810 lignes) se charge en entier** (~500 Ko) : l'identification d'ouverture couvrira tout, seul le corpus RAG est restreint aux cibles.

## 3. Accrocs de mesure (traçabilité)

- Premier essai FR à 0 : la catégorie supposée (« Ouverture du jeu d'échecs ») n'existe pas — la vraie racine est `Catégorie:Ouverture d'échecs`, retrouvée en remontant les catégories de l'article « Partie italienne ».
- **Erratum de méthode (même jour)** : le premier comptage donnait 268 en additionnant les catégories sans dédupliquer les articles présents dans plusieurs d'entre elles ; le notebook `01-inventaire-corpus.ipynb` (ensemble de titres) donne le chiffre correct : **225**.
- HTTP 429 de l'API en crawl rapide → throttle 0,6 s/requête + retry, et exclusion des catégories techniques Projet:/Portail: (qui explosaient le parcours).

## 4. Décision de périmètre à valider (proposition)

Liste proposée des **ouvertures cibles** du POC (critères : mix 1.e4 / 1.d4 / 1.c4, popularité chez les jeunes joueurs, richesse du corpus FR+EN) :

| # | Ouverture | ECO | Pourquoi |
|---|---|---|---|
| 1 | Partie italienne | C50–C54 | LA porte d'entrée pédagogique ; démo du script (doc 08) |
| 2 | Partie espagnole | C60–C99 | référence absolue, 15 articles FR dédiés |
| 3 | Défense sicilienne | B20–B99 | la plus jouée au monde, 33 articles FR |
| 4 | Défense française | C00–C19 | répertoire jeune classique |
| 5 | Défense caro-kann | B10–B19 | solide, pédagogique |
| 6 | Gambit dame (accepté + refusé) | D06–D69 | l'entrée 1.d4, 43 articles FR (gambits) |
| 7 | Défense est-indienne | E60–E99 | structure moderne, couvre la série E |
| 8 | Partie anglaise | A10–A39 | l'entrée 1.c4, couvre la série A |
| 9 *(option)* | Défense scandinave | B01 | simple, fréquente chez les jeunes |
| 10 *(option)* | Gambit du roi | C30–C39 | riche historiquement — parties de référence spectaculaires |

→ Couverture des 5 séries ECO (A–E) assurée dès les 8 premières.

**✅ Décision validée par Richard le 2026-08-22 : les 8 ouvertures fermes, sans les optionnelles.**

## 5. Reproductibilité

**Notebook exécutable : `notebooks/01-inventaire-corpus.ipynb`** (résultats du 2026-08-22 figés dedans). À re-exécuter à l'identique lors de l'ETL (É3), où sa logique deviendra le module d'inventaire du pipeline avec rapport chiffré versionné.
