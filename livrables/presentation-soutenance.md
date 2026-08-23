# Présentation — Agent IA d'entraînement aux ouvertures (FFE)

> **v3 (deck) — retours mentor + revue croisée** : la présentation raconte (problème → produit → démonstration → architecture → preuves → coûts → perspective vidéo) ; chaque visuel est une **preuve réelle du projet** (captures de l'app, figures des notebooks) ; les détails techniques vivent dans `documentation-technique.md` et en annexes. 13 diapositives + annexes. Notes : `notes-presentation.md`.

---

## Diapo 1 — Titre

**Un coach IA pour les ouvertures d'échecs** — preuve de concept pour la Fédération Française des Échecs.
Richard Hugou, IA Engineer junior, Cavalier Data. Soutenance — août 2026.

---

## Diapo 2 — L'histoire et le besoin

La FFE prépare ses jeunes espoirs aux championnats d'Europe. **60 000 licenciés, ~60 % de jeunes, quelques centaines d'entraîneurs** — le goulot d'étranglement est humain.

> Imaginez Léa, 12 ans, qui prépare son tournoi : elle veut travailler ses ouvertures ce soir, son entraîneur n'est pas disponible. La commande d'Alan : **un POC en 2 semaines** — une IA qui l'accompagne *pendant qu'elle joue*.

Ce que l'IA doit savoir faire pour elle : (1) proposer les coups reconnus par la théorie, (2) expliquer les idées en citant ses sources, (3) recommander des vidéos adaptées, (4) évaluer objectivement quand Léa sort des sentiers battus.

---

## Diapo 3 — L'application en action *(la vidéo d'abord)*

**→ Vidéo de démonstration (3-4 coups, ~45 s)** : Léa choisit son camp, travaille l'Italienne, reçoit les conseils, sort de la théorie — l'agent bascule sur le moteur.
*Lien : https://www.loom.com/share/821b854d6676475bb82cb1830448a3c3*

Capture : `rendu/captures/ui-conseils-italienne.png` — l'écran unique : échiquier + panneau coach (coups des maîtres « Fc5 (fou f8) » avec statistiques, explication sourcée, vidéos).

---

## Diapo 4 — Le parcours de l'élève (fonctionnel)

Un seul parcours, suivi jusqu'au bout — Léa travaille l'Italienne avec les Blancs :

1. **Elle dit qui elle est** : « je joue les Blancs » — un seul jeu de pièces, son point de vue.
2. **Elle choisit son point de départ** : l'Italienne (parmi les 8 ouvertures), ou une position libre.
3. **L'agent joue les coups de l'adversaire** — les plus joués par les maîtres, jamais un choix de LLM ; elle joue les siens. Une erreur ? « Annuler le coup » retire la paire.
4. **Hors théorie, l'agent le signale** et lui laisse la main : annuler, ou analyser.
5. **Position prête → « Lancer l'IA »** : coups des maîtres avec statistiques **et flèches sur l'échiquier**, explication **avec sources cliquables**, vidéos — et une question libre si elle veut.
6. **Sur un coup douteux**, l'agent change d'outil : **évaluation objective du moteur**.

Capture : `rendu/captures/ui-accueil.png` (l'accueil qui explique ce parcours). À aucun moment le système n'invente : il va chercher, il assemble, il cite.

---

## Diapo 5 — L'architecture : qui communique avec qui, et pourquoi

Schéma de composants (l'architecture réellement implémentée) :

```
Léa (navigateur) → ANGULAR (échiquier + panneau coach)
                        ↕ position (FEN) / réponse
                   FASTAPI + LANGGRAPH (l'orchestrateur : qui décide quelle étape exécuter)
        ┌──────────────┼──────────────┐
     LICHESS       STOCKFISH       MILVUS          + YOUTUBE (ressource pédagogique)
   (que jouent    (que vaut la    (où chercher     + MONGODB (que met-on en cache)
   les maîtres ?)  position ?)     les connaissances ?)
        └──────────────┼──────────────┘
                   LLM local (comment transformer ces informations en explication ?)
                        ↓
                 RÉPONSE SOURCÉE
```

Chaque boîte répond à une question — et **le FEN** (la position en une ligne de texte) est la langue commune qui circule entre toutes. Le **routeur est déterministe** (un seuil de parties, pas un avis de LLM) et **chaque brique a un plan B** (dégradation propre, observée en réel).

---

## Diapo 6 — L'orchestration : le chemin d'une position

*(le graphe de décision — celui du code)*

```
position (FEN) → valider → identifier l'ouverture → en théorie ?
      oui → LICHESS (coups des maîtres + stats)      non → STOCKFISH (évaluation objective)
                     → contexte documentaire (Milvus, rayon de l'ouverture) → vidéos
                     → LLM : rédige et cite — IL NE CHOISIT JAMAIS UN COUP
```

Un seul parcours à raconter : Léa joue 3.Fc4 → Italienne identifiée → en théorie → Fc5/Cf6 avec leurs statistiques → fiches du rayon italienne → vidéos → réponse rédigée et sourcée. Et sur 4.g4?! : hors théorie → le moteur mesure (−1,47) au lieu de réciter.

---

## Diapo 7 — La base vectorielle, expliquée

**Le problème** : Léa demande « pourquoi le fou vise f7 ? » — aucun mot-clé ne relie sa question à la page « Giuoco Piano ». Il faut chercher par le **sens**.

**Comment on indexe** (une fois) :
1. 161 pages encyclopédiques (Wikipédia FR + Wikibooks EN, licences libres, périmètre signé) → **477 fiches** de 300-500 mots ;
2. chaque fiche passe dans un **modèle d'embedding** → un vecteur de **1 024 nombres** qui encode son sens — français et anglais dans le même espace ;
3. les vecteurs sont rangés dans **Milvus**, la base spécialisée qui sait chercher « le plus proche » très vite.

**Comment on cherche** (à chaque question) : la question devient un vecteur à son tour → **similarité cosinus** (l'angle entre les deux vecteurs : 1 = même sujet, 0 = sans rapport) → les 5 fiches les plus proches, **dans le rayon de l'ouverture jouée uniquement** → transmises au rédacteur avec leurs sources.

**Mesuré** : recherche en **7–11 ms** sur 477 fiches ; le réglage des requêtes fait passer la séparation sujet/hors-sujet de 0,29 à **0,50** ; une question hors bibliothèque → **zéro fiche, réponse honnête** (« ma bibliothèque ne couvre pas cette ouverture »).

---

## Diapo 8 — Comment j'ai construit la connaissance

Pour répondre, l'agent s'appuie sur **4 sources complémentaires** :

| Besoin | Source |
|---|---|
| Nommer l'ouverture | le référentiel `chess-openings` (CC0) |
| Voir ce que jouent les maîtres | l'API Lichess (2 M+ parties) |
| Expliquer les idées | la base documentaire vectorielle (Wikipédia FR + Wikibooks EN, CC BY-SA) |
| Donner une ressource pédagogique | YouTube (métadonnées seules) |

La base documentaire est **construite par un pipeline rejouable** : extraction (périmètre signé) → nettoyage → découpage en fiches → vectorisation → Milvus.

**Le visuel de cette diapo est la figure réelle du notebook 03** (`notebooks/figures/01-entonnoir-corpus.png`) : **3 251 pages disponibles → 161 retenues (manifeste signé) → 477 fiches** — avec 95 FEN de référence calculés, 0 échec, 1 doublon écarté.

---

## Diapo 9 — Ce que j'ai mesuré

| Ce qu'on promet à Léa | Cible | Mesuré |
|---|---|---|
| Jamais un coup illégal | 0 | **0 sur 56 coups affichés** (scénario complet rejoué) |
| Une réponse rapide | p95 < 8 s | **6,1 s** (médiane 4,5 s — rédaction LLM locale comprise) |
| Toujours ses sources | 100 % | **100 % — garanti par le code**, pas par le LLM |
| Ne jamais inventer hors sujet | abstention 5/5 pièges | **5/5 — par construction** (règle des rayons) |
| Recherche documentaire instantanée | < 100 ms | **7–11 ms** |

**Un mot de théorie LLM** (pourquoi ces garde-fous) : un modèle de langage prédit le mot suivant — il est fait pour être *plausible*, pas pour être *vrai*. D'où l'architecture : les faits viennent de systèmes vérifiables, le LLM **met en mots** des faits qu'on lui annote (« Fc5 — le Fou va en c5 »), à basse température, avec un gabarit déterministe en repli.

---

## Diapo 10 — Une amélioration guidée par la mesure

Trois exemples de décisions prises **par la mesure** (le détail : documentation technique + notebooks versionnés) :

1. **Le choix du LLM** : plan initial = API payante ; le banc de mesure (4 modèles locaux) a montré qu'un modèle de 3,2 Go répond en 3-7 s en bon français → **local, 0 €**. La décision a été *révisée par les chiffres*.
2. **Le gold set** : 25 questions étiquetées, figées avant tout réglage. Résultat 1,0 partout → l'étalon était trop facile — c'est une découverte, pas un échec ; l'étalon v2 est l'axe suivant.
3. **L'abstention** : une question hors corpus faisait citer des sources voisines (mesuré). Un seuil de score ne sépare pas (0,618 vs 0,619 à un millième !) → **règle déterministe** : le corpus n'est consulté que dans le rayon de l'ouverture jouée ou nommée. Vérifié : 5/5 pièges bloqués, aucune question légitime sacrifiée.

Discipline : chaque chiffre de ce deck sort d'un notebook exécuté ou d'un run MLflow versionné — aucun d'ailleurs.

---

## Diapo 11 — Le déploiement et les coûts

```
./demarrer.sh          # ou : docker compose up
```

7 conteneurs + le modèle local sur l'hôte. Volumes persistants, secrets en variables d'environnement, CI verte. **Installation fraîche mesurée : application utilisable en 2 min 09** (bibliothèque prête à 2 min 28, protocole rejouable).

**Combien ça coûte ?** POC : **0 € de consommation** (données libres, briques open source, LLM local — le poste payant a été supprimé par la mesure). Passage cloud : ≈ **0,25 centime/réponse** (option Haiku mesurée) → < 0,10 €/élève/mois. À industrialiser : hébergement UE (public mineur), stockage, supervision, montée en charge — détail dans l'étude jointe.

---

## Diapo 12 — Et si la connaissance était dans une vidéo ? (partie 2)

La demande d'Alan : indexer les vidéos **par position**, pas par titre — « cette position est expliquée à 4 min 32 ». **C'est une étude : rien de ce système n'est développé, c'est volontaire et conforme à la commande** — voilà comment le POC *pourrait évoluer*.

```
vidéo → images extraites → détection de l'échiquier → position → FEN → l'AGENT EXISTANT
```

**Ce n'est pas un deuxième agent** : le principe est de transformer la vidéo en positions FEN — la même clé que tout le POC — exploitables par l'agent déjà construit. Les capacités d'analyse sont exposées en **MCP** : des serveurs d'outils indépendants que tout agent futur de la FFE peut appeler.

- Bénéfice chiffré : ≈ **0,10–0,15 €/vidéo** contre 7,50–15 € à la main (×50-100).
- **La limite dure est juridique** (CGU : jamais les fichiers) → MVP : licences Creative Commons + transcripts d'abord, vision 2D ; le 3D attendra les chiffres du pilote.
- Build MVP **15–20 k€** · opex ~100–150 $/mois à 1 000 vidéos/mois · roadmap avec critères go/no-go.

Livrables joints : note bénéfices/limites (9 p.), schéma MCP, étude de faisabilité et coûts.

---

## Diapo 13 — Conclusion : démontré, limites, suite

**Démontré et mesuré** : la boucle jouer → comprendre → dévier → évaluer fonctionne (0/56 coup illégal · abstention 5/5 · 100 % sourcé · p95 6,1 s · 0 € · installation 2 min 09).
**Limites assumées** : 8 ouvertures (manifeste signé), gold set v1 grossier (v2 en axe), exécution locale.
**La suite** : groupe pilote d'élèves avant les championnats d'Europe ; industrialisation (architecture inchangée, redimensionnée) ; MVP analyse vidéo ; mode entraînement actif (l'agent joue l'adversaire) ; corpus élargi vers les 500 codes ECO.

**→ Démo en direct.** *(Annexes et documentation technique à disposition.)*

---
---

# Annexes (montrées seulement si le jury demande)

## Annexe A — Les sources de données en détail

| Source | Contenu | Volumétrie | Licence |
|---|---|---|---|
| Référentiel `chess-openings` (Lichess) | 3 810 ouvertures nommées, 500 codes ECO | ~500 Ko | CC0 |
| API Lichess Opening Explorer | stats masters (2 M+ parties) par position | temps réel + cache 24 h | CC0 |
| Corpus « Wikichess » | 225 articles FR + 3 026 pages EN disponibles → **161 retenues** (manifeste signé) → 477 fiches | sélection par ouvertures cibles | CC BY-SA |
| YouTube Data API v3 | métadonnées uniquement (jamais les fichiers) | ~300 unités réelles, cache 7 j | CGU respectées |

ETL rejouable et idempotent : 156 pages extraites → 477 fiches (moyenne 244 tokens — sous-cible mesurée et assumée), 1 doublon écarté, 95 FEN calculés / 0 échec. Figures EDA : notebooks/figures 01-03.

## Annexe B — Le protocole d'évaluation en détail

Gold set 25 questions figé avant tout réglage (15 directes FR/EN, 5 par position, 5 pièges). Runs A « naïf » (chunks 1000, top-3, sans filtre) vs B « soigné » (300-500 + ariane, top-5, filtre ECO) loggés MLflow : recall@5 et MRR **1,0 partout** → l'étalon v1 mesure le routage, les deux configs le réussissent ; la vraie différence (qualité des fiches transmises au rédacteur) exige des labels fins. Mesure d'adoption des embeddings : préfixe d'instruction 0,29 → 0,50 (notebook 02). Capture MLflow : `notebooks/figures/04-mlflow-runs.png`.

## Annexe C — La décision d'abstention, l'histoire complète

Préjudice mesuré (notebook 05) → photo des 25 scores par le chemin de production (notebook 07, figure) : pièges grossiers ≤ 0,548, entrelacement 0,618-0,663, seuil pur impossible (et les vraies questions scorent bas : 0,629). Décision : règle des rayons signés (position OU nom dans la question → rayon ; hors manifeste → zéro fiche + note honnête) + filet 0,58. Tests garde-fous versionnés.

## Annexe D — Le choix du LLM en détail

Campagne mesurée de 4 modèles locaux (22/08) : qwen3.5:4b retenu (3,2 Go RAM, 3-7 s, FR correct avec faits annotés + temp 0,2) ; Claude Haiku 4.5 = option qualité par variable d'environnement ; gabarit déterministe = repli toujours juste. Le LLM ne fait que la mise en forme finale.

## Annexe E — Modèle de données

Milvus `openings_kb` : vecteur 1024 d (HNSW/cosinus), texte, eco/opening_name/fen_ref/lang (filtres), source_url/licence (attribution), content_hash/ingested_at (idempotence). MongoDB : explorer_cache (TTL 24 h), videos_cache (7 j), eval_cache (sans TTL), sessions, eval_runs. Clé transverse : le FEN normalisé.
