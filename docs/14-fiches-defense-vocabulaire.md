# 14 — Fiches de défense : le vocabulaire du projet, expliqué et défendable

> Une fiche par brique. Chaque fiche donne : la définition **à dire telle quelle au jury**, l'analogie si on te demande de vulgariser, la justification (pourquoi cette brique chez nous), les chiffres à citer, et les questions pièges avec leur parade.
> À répéter à voix haute avant la soutenance. Le schéma qui relie tout : « le trajet d'un coup » (docs/11 + slide 8).

---

## Fiche 1 — FEN (et sa validation)

**À dire au jury** : « Le FEN est une notation standard qui encode toute une position d'échecs en une ligne de texte : où sont les pièces, à qui de jouer, quels roques restent possibles. C'est la clé primaire de notre système : chaque brique — Lichess, Stockfish, le RAG, le cache — est interrogée par FEN. »

**Analogie** : les coordonnées GPS d'une partie. Deux joueurs arrivés à la même position par des chemins différents ont le même FEN — c'est ce qui rend le cache et les statistiques possibles.

**Exemple concret** (position initiale) :
`rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`
Lecture : les 8 rangées de pièces (majuscules = Blancs), `w` = trait aux Blancs, `KQkq` = tous les roques encore possibles, puis compteurs de coups.

**La validation** : avant tout traitement, la bibliothèque **python-chess** vérifie que le FEN décrit une position *légale* (pas deux rois blancs, pas de pion sur la 1re rangée…). C'est le videur à l'entrée : rien n'entre sans lui.

**Pourquoi chez nous** : objectif O1 = zéro coup illégal proposé. La garantie ne vient pas de l'IA mais de cette validation systématique + un filtre en sortie (tout coup proposé doit appartenir aux coups légaux de la position).

**Questions pièges probables** :
- *« Pourquoi le FEN en query param et pas dans l'URL comme `/moves/{fen}` ? »* → Un FEN contient des espaces et des `/` ; en path param il faut l'encoder et certains serveurs le re-décodent mal. En query param, aucun piège. L'alias conforme à l'énoncé est documenté.
- *« Deux FEN différents peuvent-ils être la même position ? »* → Oui, les deux derniers champs (compteurs) varient sans changer la nature de la position ; c'est pour ça qu'on normalise sur les 4 premiers champs pour les clés de cache.

---

## Fiche 2 — Lichess (et son Opening Explorer)

**À dire au jury** : « Lichess est la plus grande plateforme d'échecs open source au monde. Son API Opening Explorer nous répond, pour n'importe quel FEN : quels coups les maîtres ont joués dans cette position, combien de fois, avec quels résultats, et quelles parties célèbres. C'est notre source de vérité pour "la théorie" — des données réelles, en licence CC0, gratuites. »

**Analogie** : une bibliothèque où sont archivées plus de 2 millions de parties de maîtres depuis 1952. On lui montre la photo de l'échiquier, le bibliothécaire répond « dans cette position, 60 % des maîtres ont joué e4 ».

**Pourquoi chez nous** : « les meilleurs coups issus de la théorie » (le brief) ne peuvent pas venir d'un LLM (il hallucine) ni d'être codés à la main (3 500 ouvertures). L'explorer les fournit avec les statistiques en prime — ce sont les barres du panneau coach.

**Chiffres** : ~2 M+ parties de maîtres (endpoint `/masters`) ; base en ligne cumulée > 6 milliards de parties ; accès par **jeton personnel gratuit** (constaté le 22/08/2026 : l'explorer répond 401 sans autorisation — la doc initiale disait « aucune auth ») ; licence CC0.

**Questions pièges** :
- *« Que se passe-t-il si l'API est en panne ou vous limite ? »* → Erreurs typées : un HTTP 429 impose 60 s d'attente (règle officielle Lichess) — on renvoie un 503 avec `Retry-After: 60` ; un timeout → l'agent dégrade (éval Stockfish + RAG sans les stats). Et le cache MongoDB (TTL 24 h) fait qu'une position déjà vue ne re-sollicite jamais l'API.
- *« C'est quoi, être "en théorie" ? »* → Décision de conception : une position est en théorie si elle apparaît dans ≥ N parties de maîtres (N=5 par défaut, paramètre configurable). C'est un seuil déterministe, testable — pas un jugement du LLM.

---

## Fiche 3 — Stockfish

**À dire au jury** : « Stockfish est le moteur d'échecs open source de référence — un programme de calcul pur, environ 3600 Elo, très au-dessus du champion du monde humain (~2830). Il ne parle pas, il ne pense pas : il calcule des millions de positions et rend un chiffre — l'évaluation en centipawns, où +100 équivaut à un pion d'avance pour les Blancs. »

**Analogie** : la calculatrice scientifique des échecs. On ne lui demande pas d'expliquer, on lui demande de mesurer.

**Pourquoi chez nous** : quand Léa sort des sentiers battus (position absente de la base des maîtres), il n'y a plus de statistiques à montrer. Le brief demande alors « une évaluation par un moteur spécialisé » : Stockfish nous dit objectivement si son coup est bon. C'est l'étape « dévier → évaluer » de la boucle — ce que ferait un entraîneur en regardant la position.

**Chiffres** : > 3600 Elo ; licence GPLv3 (version épinglée dans le Dockerfile) ; local (zéro coût, zéro réseau) ; profondeur bornée (16) ou temps borné (~1 s) pour une latence prévisible.

**Questions pièges** :
- *« Pourquoi ne pas utiliser Stockfish pour tout, même la théorie ? »* → Il donne le meilleur coup *de calcul*, pas le coup *pédagogique* : pour apprendre les ouvertures, on veut ce que la pratique des maîtres a validé, avec noms, plans et parties de référence. Le moteur prend le relais là où la théorie s'arrête.
- *« Un seul processus moteur, ça tient la charge ? »* → Pour un POC mono-utilisateur, oui (accès sérialisé par verrou + cache persistant des évaluations : une position n'est jamais recalculée). En production : pool de workers — c'est dans la trajectoire d'industrialisation.

---

## Fiche 4 — LangGraph

**À dire au jury** : « LangGraph est un framework Python pour construire des agents IA sous forme de graphe : des nœuds — chacun une étape de travail — reliés par des arêtes, y compris conditionnelles. Notre agent est littéralement l'organigramme du slide : valider le FEN → identifier l'ouverture → router selon "en théorie ou pas" → collecter les faits → rédiger. »

**Analogie** : le chef de gare. Il ne conduit aucun train (il ne calcule pas un coup, n'évalue rien) ; il fait passer la demande de Léa par les bons guichets, dans le bon ordre, avec des aiguillages et des plans B si un guichet ferme.

**Pourquoi chez nous** : imposé par le brief, mais surtout pertinent : notre logique **branche** (théorie vs moteur), et un graphe à arêtes conditionnelles exprime ça proprement. Chaque nœud est testable isolément, chaque passage est tracé (durée, tokens) — c'est la preuve « mon agent choisit des outils pertinents » de la fiche d'autoévaluation.

**Le point d'architecture à assumer fièrement** : notre routeur est **déterministe** (seuil de parties masters), pas décidé par le LLM. Plus testable, plus prévisible, plus défendable.

**Questions pièges** :
- *« Pourquoi pas une simple chaîne d'appels ou du code maison ? »* → Une chaîne ne branche pas ; du code maison réinventerait l'état partagé, les traces et la reprise. Le graphe donne une structure standard que le jury peut auditer d'un regard.
- *« Où intervient le LLM là-dedans ? »* → Dans un seul nœud, le dernier : la synthèse. Il reçoit les faits (coups+stats Lichess, éval Stockfish, extraits sourcés du RAG) et les met en mots pour une enfant de 12 ans. Il ne choisit jamais un coup — enseignement direct de la compétition Kaggle citée par Alan : des LLM seuls aux échecs jouent des coups illégaux et des blunders.

---

## Fiche 5 — la phrase qui relie tout (conclusion de slide)

« Chaque brique fait ce qu'elle sait faire de mieux : **python-chess** garantit la légalité, **Lichess** fournit la théorie vécue par les maîtres, **Stockfish** mesure objectivement, le **LLM** explique pédagogiquement, et **LangGraph** orchestre le tout. Le LLM n'est jamais la source de vérité — c'est ce qui rend l'agent fiable. »
