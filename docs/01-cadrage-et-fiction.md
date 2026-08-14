# 01 — Cadrage & fiction : sur quoi on travaille, pour qui, et pourquoi

## 1. La fiction (à raconter en 90 secondes en début de soutenance)

| Élément | Choix retenu |
|---|---|
| **Client** | Fédération Française des Échecs (FFE) — organisation réelle, mission fictive |
| **Notre entreprise (fictive)** | « Cavalier Data » (proposition — n'importe quelle ESN fictive fait l'affaire), cabinet de conseil IA/data, 25 collaborateurs |
| **Notre rôle** | IA Engineer **junior**, missionné chez le client, encadré par Alan |
| **Commanditaire** | Alan, responsable technique de Cavalier Data (sponsor interne) ; côté FFE : la direction technique nationale (DTN) jeunes |
| **Déclencheur** | Championnats d'Europe **jeunes** à venir : la FFE veut outiller l'entraînement aux **ouvertures** de ses jeunes espoirs |
| **Commande** | Un **POC en 2 semaines** qui démontre la faisabilité et la valeur d'un agent IA d'entraînement aux ouvertures |

### Pourquoi la FFE paierait pour ça — les chiffres simples et actionnables

| Chiffre | Valeur | Usage dans le pitch |
|---|---|---|
| Licenciés FFE | **> 60 000** (record historique, saison 2024) ⚠️ à vérifier sur ffechecs.fr | Le vivier à entraîner |
| Part de jeunes parmi les licenciés | **~60 %** ⚠️ à vérifier | La cible directe du produit |
| Entraîneurs diplômés disponibles | quelques **centaines** pour des dizaines de milliers de jeunes ⚠️ à vérifier | **Le goulot d'étranglement** que l'IA dessert |
| Boom des échecs en ligne | Lichess : **≈ 100 M de parties/mois**, base publique cumulée **> 6 milliards de parties** ⚠️ ordres de grandeur à vérifier | La donnée existe, massive et ouverte |
| Coût d'un entraîneur particulier | **30–60 €/h** (marché) ⚠️ | Le comparatif économique de l'agent |
| Combinatoire du jeu | **≈ 69 000 milliards** de suites possibles après 5 coups de chaque camp (perft(10) = 69 352 859 712 417) ; ≈ 4,8×10⁴⁴ positions légales (Tromp) | Pourquoi on ne peut pas « tout apprendre par cœur » → théorie + moteur |

> Règle du pitch : 4 à 5 chiffres maximum sur le slide, chacun relié à une décision (« donc on… »).

## 2. La problématique (formulée SANS solution technique)

> **« Comment permettre à chaque jeune espoir de la FFE de travailler ses ouvertures avec un retour de niveau "entraîneur", à la demande, sans multiplier les entraîneurs humains ? »**

Réponse au stade du pitch (toujours sans techno) : **« une IA qui accompagne l'élève pendant qu'il joue »** — elle :
1. propose les **meilleurs coups reconnus par la théorie** ;
2. **explique** l'ouverture (idées, histoire, parties de référence) ;
3. recommande des **vidéos pédagogiques** adaptées à la position ;
4. **évalue objectivement** la position quand l'élève sort des sentiers battus.

Ce n'est qu'ensuite qu'on déroule : pour faire ça, l'IA a besoin de **données** (lesquelles → doc 04), puis d'une **technologie** pour les orchestrer (laquelle → doc 05).

## 3. Périmètre du POC

### Dans le périmètre (2 semaines)
- Échiquier interactif Angular (ngx-chessboard, repo OC `material-chessboard`).
- Agent LangGraph branché sur : validation FEN, coups théoriques (API Lichess), évaluation Stockfish hors théorie, contexte RAG (Milvus + corpus « Wikichess »/wiki ouvertures), vidéos YouTube pertinentes.
- Persistance MongoDB (caches API, sessions/conversations, métadonnées vidéos).
- Livraison locale : `docker compose up` unique.
- Étude (sans développement) du système d'analyse vidéo → FEN, avec architecture MCP et coûts.

### Hors périmètre (à dire explicitement — ça protège en soutenance)
- Pas de comptes utilisateurs, pas d'authentification, pas de déploiement cloud.
- Pas de fine-tuning de modèle (choix assumé, voir doc 06 §3).
- Pas de couverture de tout le répertoire d'ouvertures : **8 à 10 ouvertures majeures** seulement.
- Pas de téléchargement de vidéos YouTube (conformité CGU — voir doc 04 §2.5) : affichage/embed uniquement.
- Le système d'analyse vidéo (partie 2) est **conçu, pas développé**.

## 4. Personas (pour ancrer les choix UX et les exemples de démo)

| Persona | Besoin | Ce que l'agent lui donne |
|---|---|---|
| **Léa, 12 ans, espoir régional (~1500 Elo)** | Comprendre *pourquoi* un coup est bon, pas juste lequel | Coups théoriques + explication simple + vidéo |
| **Marc, entraîneur de club** | Préparer des séances, vérifier les écarts à la théorie | Éval Stockfish + parties de référence |
| **La DTN FFE** | Un outil scalable avant les championnats d'Europe | La démo du POC + l'étude d'industrialisation |

## 5. Objectifs mesurables du POC (les critères de succès qu'on s'engage à mesurer)

| # | Objectif | Cible | Comment on mesure |
|---|---|---|---|
| O1 | Zéro coup illégal proposé | 0 sur le jeu de test | Validation python-chess sur 100 % des sorties |
| O2 | Couverture ouvertures | 8–10 ouvertures majeures indexées | Inventaire ETL (doc 04) |
| O3 | Pertinence du RAG | recall@5 ≥ 0,8 sur le gold set de 25 questions | Protocole d'éval doc 04 §6 |
| O4 | Latence de réponse agent | p95 < 8 s (hors premier démarrage) | Traces LangGraph/MLflow |
| O5 | Robustesse démo | `docker compose up` → app utilisable en < 5 min sur machine vierge | Test d'installation fraîche (étape 6) |
| O6 | Coût d'exploitation POC | < 5 € de LLM pour tout le développement + démo | Compteur de tokens (doc 06) |

## 6. Glossaire échecs (pour les slides et pour un jury non joueur)

- **Ouverture** : les premiers coups d'une partie ; **théorie** : suites étudiées et validées par la pratique des maîtres.
- **FEN** (Forsyth-Edwards Notation) : une chaîne de texte qui encode entièrement une position (pièces, trait, roques, en passant, compteurs). C'est **la clé primaire** de tout notre système.
- **ECO** : classification des ouvertures en 500 codes (A00–E99).
- **Centipawn (cp)** : unité d'évaluation des moteurs ; +100 cp ≈ un pion d'avance pour les Blancs.
- **Stockfish** : moteur d'échecs open source (GPLv3), force estimée > 3600 Elo — très au-dessus du champion du monde humain (~2830).
