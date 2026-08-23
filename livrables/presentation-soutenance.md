# Présentation — Agent IA d'entraînement aux ouvertures (FFE)

> **v5 — restructurée sur retours mentor** : la présentation raconte la démarche (fonctionnement → architecture → déploiement → mesure → coûts), les détails techniques vivent dans `documentation-technique.md`. 13 diapositives + annexes. Notes de l'orateur : `notes-presentation.md`.

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

**→ Vidéo de démonstration (3-4 coups, ~1 min)** : Léa choisit son camp, travaille l'Italienne, reçoit les conseils, sort de la théorie — l'agent bascule sur le moteur.

Capture : `rendu/captures/ui-conseils-italienne.png` — l'écran unique : échiquier + panneau coach (coups des maîtres « Fc5 (fou f8) » avec statistiques, explication sourcée, vidéos).

---

## Diapo 4 — Le parcours de l'élève (fonctionnel)

Ce que fait Léa, et ce que fait le système à chaque étape :

| Ce que fait Léa | Ce que fait le système | Pourquoi |
|---|---|---|
| 1. Elle dit qui elle est : « je joue les Noirs » | le plateau se retourne vers elle | un seul jeu de pions, son point de vue |
| 2. Elle choisit une ouverture à travailler — ou joue ses coups **et ceux de son adversaire** (corrigeables) | la position s'installe, validée à chaque coup | l'erreur de saisie ne pollue jamais l'analyse |
| 3. Elle appuie sur **« Lancer l'IA »** | l'agent interroge ses sources et compose la réponse | c'est elle qui décide quand demander conseil |
| 4. Elle lit : coups des maîtres + statistiques, explication **avec sources cliquables**, vidéos | chaque bloc vient d'une source vérifiable | rien n'est inventé |
| 5. Elle pose une question libre (« pourquoi le fou vise f7 ? ») | réponse fondée sur le corpus documentaire, sourcée | la boucle jouer → comprendre |
| 6. Elle tente un coup douteux hors théorie | l'agent change d'outil : **évaluation objective du moteur** | hors des livres, on mesure au lieu de réciter |

Capture : `rendu/captures/ui-accueil.png` (l'accueil qui explique ce parcours).

---

## Diapo 5 — L'architecture

*(le schéma — chaque brique, son intérêt, les liens ; les détails : documentation technique)*

```
Léa (navigateur) ⇄ FRONTEND Angular (échiquier + panneau coach)
                      ⇄ API FastAPI — L'AGENT (graphe LangGraph) :
   valider la position → identifier l'ouverture → ROUTEUR (déterministe)
     en théorie  → LICHESS  : les coups des maîtres (2 M+ parties, la vérité statistique)
     hors théorie → STOCKFISH : l'évaluation objective (embarqué, aucune position inconnue)
   → BASE VECTORIELLE Milvus : le « pourquoi » documentaire (diapo suivante)
   → YOUTUBE (métadonnées) : les vidéos — il y a toujours quelque chose à proposer
   → LLM local (Ollama) : RÉDIGE la réponse — il ne décide jamais, il met en mots
   ⇢ MONGODB : les caches (théorie 24 h, évals, vidéos 7 j) — rapidité et résilience
```

**Les trois principes qui tiennent l'ensemble** : le **FEN** (la position en une ligne de texte) circule entre toutes les briques ; le **routeur est déterministe** (un seuil de parties, pas un avis de LLM) ; **chaque brique a un plan B** (une source en panne → l'agent dégrade, ne plante pas — observé en conditions réelles).

---

## Diapo 6 — La base vectorielle, expliquée

**Le problème** : Léa demande « pourquoi le fou vise f7 ? » — aucun mot-clé ne relie sa question à la page « Giuoco Piano ». Il faut chercher par le **sens**.

**Comment on indexe** (une fois) :
1. 161 pages encyclopédiques (Wikipédia FR + Wikibooks EN, licences libres, périmètre signé) → **477 fiches** de 300-500 mots ;
2. chaque fiche passe dans un **modèle d'embedding** → un vecteur de **1 024 nombres** qui encode son sens — français et anglais dans le même espace ;
3. les vecteurs sont rangés dans **Milvus**, la base spécialisée qui sait chercher « le plus proche » très vite.

**Comment on cherche** (à chaque question) : la question devient un vecteur à son tour → **similarité cosinus** (l'angle entre les deux vecteurs : 1 = même sujet, 0 = sans rapport) → les 5 fiches les plus proches, **dans le rayon de l'ouverture jouée uniquement** → transmises au rédacteur avec leurs sources.

**Mesuré** : recherche en **7–11 ms** sur 477 fiches ; le réglage des requêtes fait passer la séparation sujet/hors-sujet de 0,29 à **0,50** ; une question hors bibliothèque → **zéro fiche, réponse honnête** (« ma bibliothèque ne couvre pas cette ouverture »).

---

## Diapo 7 — Le déploiement

```
./demarrer.sh          # ou : docker compose up
```

7 conteneurs (front nginx 78 Mo, API+Stockfish, Milvus, MongoDB, MLflow) + Ollama sur l'hôte. Volumes persistants, secrets en variables d'environnement, CI (lint + 65 tests + build front).

**Installation fraîche mesurée** : application utilisable en **2 min 09**, bibliothèque vectorielle prête à 2 min 28 (protocole rejouable `tester-installation.sh`) — critère « < 5 minutes » largement tenu.

---

## Diapo 8 — Performances et fiabilité (tout est mesuré)

| Ce qu'on promet à Léa | Cible | Mesuré |
|---|---|---|
| Jamais un coup illégal | 0 | **0 sur 56 coups affichés** (scénario complet rejoué) |
| Une réponse rapide | p95 < 8 s | **6,1 s** (médiane 4,5 s — rédaction LLM locale comprise) |
| Toujours ses sources | 100 % | **100 % — garanti par le code**, pas par le LLM |
| Ne jamais inventer hors sujet | abstention 5/5 pièges | **5/5 — par construction** (règle des rayons) |
| Recherche documentaire instantanée | < 100 ms | **7–11 ms** |

**Un mot de théorie LLM** (pourquoi ces garde-fous) : un modèle de langage prédit le mot suivant — il est fait pour être *plausible*, pas pour être *vrai*. D'où l'architecture : les faits viennent de systèmes vérifiables, le LLM **met en mots** des faits qu'on lui annote (« Fc5 — le Fou va en c5 »), à basse température, avec un gabarit déterministe en repli.

---

## Diapo 9 — La démarche : mesurer avant de décider

Trois exemples de décisions prises **par la mesure** (le détail : documentation technique + notebooks versionnés) :

1. **Le choix du LLM** : plan initial = API payante ; le banc de mesure (4 modèles locaux) a montré qu'un modèle de 3,2 Go répond en 3-7 s en bon français → **local, 0 €**. La décision a été *révisée par les chiffres*.
2. **Le gold set** : 25 questions étiquetées, figées avant tout réglage. Résultat 1,0 partout → l'étalon était trop facile — c'est une découverte, pas un échec ; l'étalon v2 est l'axe suivant.
3. **L'abstention** : une question hors corpus faisait citer des sources voisines (mesuré). Un seuil de score ne sépare pas (0,618 vs 0,619 à un millième !) → **règle déterministe** : le corpus n'est consulté que dans le rayon de l'ouverture jouée ou nommée. Vérifié : 5/5 pièges bloqués, aucune question légitime sacrifiée.

Discipline : chaque chiffre de ce deck sort d'un notebook exécuté ou d'un run MLflow versionné — aucun d'ailleurs.

---

## Diapo 10 — Structure de coûts

| Poste (coût du POC) | Coût | Pourquoi |
|---|---|---|
| Données (Lichess, wikis, référentiel) | **0 €** | licences libres (CC0, CC BY-SA) |
| Moteur Stockfish + embeddings | **0 €** | open source, exécution locale |
| Recherche vidéos | **0 €** | quota gratuit YouTube (~300 unités réelles / 10 000 par jour, cache 7 j) |
| LLM (dev + démo) | **0,00 €** | local — le poste payant a été supprimé par la mesure |

**À l'échelle** : coût marginal d'une réponse nul en local ; en cloud ≈ 0,25 centime/réponse → **< 0,10 €/élève/mois**. Postes réels d'industrialisation : hébergement UE (public mineur, RGPD) et supervision — détaillés dans l'étude jointe.

---

## Diapo 11 — Partie 2 : l'étude du système d'analyse vidéo

La demande : indexer les vidéos **par position** (FEN), pas par titre — « cette position est expliquée à 4 min 32 ».

- **Bénéfice chiffré** : indexation automatique ≈ **0,10–0,15 €/vidéo** contre 7,50–15 € à la main (×50-100).
- **La limite dure est juridique** (CGU YouTube : jamais les fichiers) → périmètre MVP : licences Creative Commons + **transcripts d'abord**, vision 2D ensuite ; le 3D (seul vrai entraînement de modèle du projet) attendra les chiffres du pilote.
- **Architecture MCP** : 4 serveurs d'outils réutilisables par tout agent FFE (youtube, vision, chess-tools, connaissances) + pipeline batch assumé pour la masse.
- **Build MVP : 15–20 k€** · opex ~100–150 $/mois à 1 000 vidéos/mois · roadmap avec critères go/no-go chiffrés.

Livrables joints : note bénéfices/limites (9 p.), schéma d'architecture MCP, étude de faisabilité et coûts.

---

## Diapo 12 — Pistes d'amélioration

- **Gold set v2** à labels fins — la suite logique de la leçon de mesure.
- **Corpus élargi** : de 8 ouvertures vers les 500 codes ECO + parties commentées FFE.
- **Mode entraînement actif** : l'agent joue la ligne théorique contre l'élève.
- **Analyse vidéo → FEN** : le MVP de la partie 2.
- Répertoire personnalisé par élève ; A/B qualité LLM sur le gold set.

---

## Diapo 13 — Conclusion

**La promesse : un retour de niveau entraîneur, à la demande.** Objectifs mesurés et tenus : 0/56 coup illégal · abstention 5/5 · 100 % sourcé · p95 6,1 s · 0,00 € de LLM · installation 2 min 09.

Recommandation à la FFE : un groupe pilote d'élèves avant les championnats d'Europe, puis industrialisation (architecture inchangée, redimensionnée) et lancement du MVP analyse vidéo.

**→ Démo en direct.** *(Questions bienvenues — annexes et documentation technique à disposition.)*

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
