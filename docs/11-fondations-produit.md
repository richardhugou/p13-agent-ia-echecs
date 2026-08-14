# 11 — Fondations produit : donnée d'entrée, comportement utilisateur, interface

> Rédigé lors du « redémarrage de zéro » du 2026-08-14. Ce document fixe le niveau produit **avant** toute discussion de modèle ou de technologie. Tout choix technique ultérieur doit se justifier par rapport à ces trois fondations.

## 1. La donnée d'entrée : une position d'échecs, rien d'autre

L'élève ne tape presque rien. Sa donnée d'entrée est **la position sur l'échiquier**, produite naturellement en jouant des coups à la souris. Techniquement, cette position s'encode en une ligne de texte (le FEN), mais du point de vue produit l'entrée c'est « où en est la partie ». C'est la clé primaire de tout le système : chaque nouvelle position déclenche tout le reste.

Il existe une deuxième entrée, **optionnelle** : une question en langage naturel (« pourquoi ce coup ? », « c'est quoi l'idée de cette ouverture ? »). Elle est toujours interprétée **dans le contexte de la position courante** — c'est ce qui distingue un coach d'un chatbot générique.

À ne pas confondre : les statistiques de parties (Lichess), les textes encyclopédiques (corpus RAG), les vidéos (YouTube) et l'évaluation moteur (Stockfish) sont des données que **le système va chercher**, pas des entrées utilisateur.

| | Donnée | Fournie par |
|---|---|---|
| Entrée primaire | Position (FEN) | L'élève, en jouant |
| Entrée secondaire | Question en langage naturel | L'élève, optionnellement |
| Contexte | Stats masters, textes, vidéos, éval moteur | Le système |

## 2. Le comportement utilisateur attendu : une boucle, pas un formulaire

Usage de référence (persona : Léa, 12 ans, ~1500 Elo) — session courte de 10–20 minutes :

1. **Elle joue un coup** sur l'échiquier.
2. **L'agent réagit sans qu'on lui demande** : nom de l'ouverture + coups recommandés par la théorie avec leur popularité chez les maîtres.
3. **Elle demande « pourquoi ? »** → explication pédagogique en langage simple, source citée, vidéo adaptée.
4. **Elle sort de la théorie** (coup absent des parties de maîtres) → l'agent le signale et bascule sur une évaluation objective : « ce coup te coûte environ un pion, voici pourquoi ».
5. Elle revient en arrière, essaie autre chose — la boucle recommence.

Principes de comportement :
- L'agent est **proactif sur la position** (il commente chaque coup) et **réactif sur les questions** (il n'inonde pas de texte non sollicité).
- L'étape 4 — la frontière « fin de la théorie → début de l'analyse » — est le cœur de la valeur : c'est elle qui remplace le regard de l'entraîneur.

**En une phrase : une position en entrée, une boucle jouer → comprendre → dévier → évaluer comme usage.**

## 3. L'interface finale : un seul écran, trois zones

Pas de page d'accueil, pas de menu, pas de compte : on arrive sur l'échiquier et on joue. La complexité (RAG, moteur, APIs) est entièrement invisible — elle ne se manifeste que par la qualité du panneau de droite.

| Zone | Contenu | Rôle |
|---|---|---|
| **Échiquier** (principale, gauche) | Plateau interactif ngx-chessboard ; cases des coups théoriques mises en évidence directement dessus | L'élève joue ici et ne quitte jamais cette zone des yeux |
| **Panneau coach** (droite) | Badge d'état (« En théorie » / « Hors théorie » + éval chiffrée), nom d'ouverture + code ECO, coups recommandés avec stats masters, explication courante **avec source citée**, champ de question | Toute la valeur pédagogique |
| **Bandeau vidéos** (bas) | 2–3 vidéos pertinentes pour la position courante (embed/lien) | Secondaire, jamais intrusif |

Comportement du panneau coach : quand la position sort de la théorie, le badge vert « En théorie » devient une évaluation chiffrée (centipawns traduits en langage d'élève : « ≈ un pion de retard »).

## 4. Ce que ces fondations imposent à la technique (aval)

- La **latence** de la boucle est un critère produit : si l'agent met 20 s à commenter un coup, la boucle est morte (→ objectif O4, p95 < 8 s).
- Le **routeur théorie/moteur** n'est pas un détail d'architecture : c'est l'étape 4 de la boucle, la valeur centrale.
- La **citation des sources** dans le panneau coach n'est pas que de la conformité CC BY-SA : c'est un élément d'interface visible.
- Les coups proposés doivent être **100 % légaux** (objectif O1) : une seule suggestion illégale détruit la confiance de l'élève.
