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

## Diapo 3 - L'application en action *(la vidéo d'abord)*

**-> Vidéo de démonstration (3-4 coups, ~45 s)** : Léa choisit son camp, travaille l'Italienne, reçoit les conseils, sort de la théorie : l'agent bascule sur le moteur.
*Lien vidéo : https://www.loom.com/share/821b854d6676475bb82cb1830448a3c3*

Visuels :
- Capture réelle `rendu/captures/ui-conseils-italienne.png` (écran unique : camp, modes, coups des maîtres « Fc5 (fou f8) », explication sourcée, vidéos).
- QR Code ## Diapo 4 - Le parcours de l'élève (fonctionnel)

Un seul parcours, suivi jusqu'au bout : Léa travaille l'Italienne avec les Blancs :

1. **Choix du camp** : « je joue les Blancs » (un seul jeu de pièces, point de vue du joueur).
2. **Point de départ** : l'Italienne (parmi les 8 ouvertures du manifeste), ou position libre.
3. **Réponse adverse automatique** : l'agent joue le coup Lichess Masters le plus fréquent. L'élève joue son coup ; « Annuler le coup » retire la paire en cas d'erreur.
4. **Détection hors théorie** : signalement immédiat et passage de main à l'élève.
5. **Déclenchement explicite (« Demander à Chessbot »)** : coups théoriques avec statistiques, flèches sur l'échiquier, explication sourcée, vidéos pédagogiques.
6. **Évaluation tactique** : sur coup douteux, bascule automatique sur le moteur Stockfish.

Visuel : capture réelle `rendu/captures/ui-accueil.png`.
*Les faits proviennent des outils spécialisés ; le LLM intervient uniquement pour formuler la réponse.*

---

## Diapo 5 - L'architecture : qui communique avec qui, et pourquoi

Schéma de composants (l'architecture réellement implémentée) :

```
                         ┌───────────────┐
                         │   MONGODB     │  (cache applicatif : théorie,
                         │ cache/mémoire │   évaluations, vidéos)
                         └───────▲───────┘
                                 ┆ (lecture / écriture)
Léa (navigateur) -> ANGULAR (échiquier + panneau coach)
                        ↕ position (FEN) / réponse
                   FASTAPI + LANGGRAPH (orchestrateur : routage et exécution)
        ┌──────────────┬──────────────┬──────────────┐
     LICHESS       STOCKFISH       MILVUS         YOUTUBE
   (théorie &      (moteur &     (recherche      (ressource
   stats masters)   éval obj.)    vectorielle)   pédagogique)
        └──────────────┴──────────────┴──────────────┘
                               ↓
                   LLM local (formulation de la réponse sourcée)
                               ↓
                         RÉPONSE SOURCÉE
```

Chaque boîte répond à une fonction précise. Le **FEN** (notation standard de position) est la clé pivot qui circule entre toutes les briques. Le **routeur est déterministe** (seuil de parties masters) et **chaque brique dispose d'un mécanisme de repli** (mode dégradé testé en conditions réelles).

---

## Diapo 6 - L'orchestration : le chemin d'une position

Graphe d'exécution LangGraph (implémenté dans `backend/graph/`) :

```
position (FEN) -> valider -> identifier l'ouverture -> en théorie ?
      oui -> LICHESS (coups des maîtres + stats)      non -> STOCKFISH (évaluation objective)
                     -> contexte documentaire (Milvus, rayon de l'ouverture) -> vidéos
                     -> LLM : rédige et cite (aucun choix de coup délégué au modèle)
```

Déroulement nominal : coup 3.Fc4 -> Italienne identifiée -> en théorie -> statistiques Lichess Fc5/Cf6 -> extraction des fiches du rayon Italienne -> vidéos YouTube -> synthèse sourcée.
Sur coup hors théorie (ex : 4.g4?!) -> évaluation chiffrée du moteur Stockfish (-1,47 cp).

---

## Diapo 7 - La base documentaire : retrouver une information par son sens

**Exemple de recherche sémantique** : « pourquoi le fou vise f7 ? » (aucun mot-clé exact ne relie la question à la page « Giuoco Piano »).

**Mécanisme d'indexation** :
1. 161 pages encyclopédiques (Wikipédia FR + Wikibooks EN, licences libres) -> **477 fiches structurées** de 300 à 500 mots.
2. Vectorisation via un **modèle d'embedding multilingue** (`qwen3-embedding:0.6b`) -> vecteurs de **1 024 dimensions** partageant le même espace sémantique FR/EN.
3. Stockage et indexation dans **Milvus** (index HNSW, métrique cosinus).

**Mécanisme de recherche** :
- Vectorisation de la requête utilisateur à la volée.
- Recherche par similarité cosinus restreinte au **rayon de l'ouverture active**.
- Transmission des 5 fiches les plus proches au générateur avec leurs URLs sources.

**Performances mesurées** : temps de recherche de **7 à 11 ms** sur 477 fiches ; séparation sémantique cible/hors-sujet portée de 0,29 à **0,50** ; filtrage hors-rayon garantissant l'absence d'hallucination de source.

---

## Diapo 8 - Construction de la base documentaire

**4 sources pour 4 fonctions** :

| Fonction | Source | Format / Licence |
|---|---|---|
| Nomenclature des ouvertures | Référentiel `chess-openings` | TSV / CC0 |
| Coups et statistiques des maîtres | API Lichess Explorer | JSON / CC0 (2 M+ parties) |
| Connaissances encyclopédiques | Wikipédia FR + Wikibooks EN | Fiches vectorisées / CC BY-SA |
| Recommandations pédagogiques | YouTube Data API v3 | Métadonnées seules / CGU respectées |

**Pipeline de traitement (ETL rejouable et idempotent)** :
`extraction (périmètre signé) -> nettoyage -> découpage en fiches -> vectorisation -> chargement Milvus`

Visuel : graphique réel du notebook 03 (`notebooks/figures/01-entonnoir-corpus.png`) illustrant l'entonnoir :
**3 251 pages disponibles -> 161 retenues (manifeste signé) -> 477 fiches** (95 FEN de référence calculés, 0 échec).

---

## Diapo 9 - Résultats et performances

| Indicateur clé | Cible | Résultat mesuré |
|---|---|---|
| Coups illégaux en sortie | 0 | **0 sur 56 coups testés** (scénario e2e complet) |
| Recall@5 (Gold Set 25 questions) | >= 0,80 | **1,0** (runs A/B tracés dans MLflow) |
| Abstention sur questions pièges | 5 / 5 | **5 / 5** (filtrage déterministe par rayon) |
| Réponses avec sources valides | 100 % | **100 %** (garanti par le pipeline d'assemblage) |
| Latence de recherche vectorielle | < 100 ms | **7 à 11 ms** (p95) |
| Latence globale avec LLM | p95 < 8 s | **1,81 s** (p50) / **2,41 s** (p95) sur Cloud GPU T4 · **6,3 s** (p95) local |
| Coût d'inférence LLM du POC | 0 € | **0,00 €** (exécution locale sur l'hôte et GPU T4) |

Visuel : graphique des latences réelles du notebook 05 (`notebooks/figures/06-latences-agent.png`).

---

## Diapo 10 - Les principaux choix techniques

| Choix d'architecture | Alternative évaluée | Décision et justification technique |
|---|---|---|
| **Modèle LLM local / GPU** | API managée payante | Modèle Qwen 3.5 / 2.5 local (3,2 Go) retenu : coût 0 €, latence 1,8 s (GPU T4) / 6,3 s (CPU) |
| **Structure documentaire** | Chunks bruts 1 000 tokens | Fiches 300-500 tokens avec fil d'Ariane, section et métadonnées scalaires (ECO, FEN) |
| **Gestion du hors-sujet** | Seuil de score cosinus seul | Filtrage déterministe par rayon d'ouverture + seuil filet à 0,58 (5/5 pièges bloqués) |

*Chaque choix d'architecture a été comparé et validé sur des bancs de mesure reproductibles.*

---

## Diapo 11 - Déploiement et coûts

### 1. Environnement Local (POC complet)
- **Architecture** : 7 conteneurs orchestrés (`docker-compose.yml` / `./demarrer.sh`) + modèle Ollama sur l'hôte.
- **Déploiement** : Volumes persistants, secrets isolés via `.env`, initialisation complète en **2 min 09**.

### 2. Environnement En ligne (Déploiement complet GPU T4)
- **Plateforme** : Hugging Face Spaces (mono-conteneur Docker avec Ollama + GPU NVIDIA T4 16 Go VRAM).
- **Performances mesurées** : **p50 = 1,81 s**, **p95 = 2,41 s** avec chaîne complète (LLM Qwen + Stockfish + Milvus).
- **Intégration continue** : Pipeline CI/CD GitHub Actions (`push main -> déploiement automatique sur le Space`).
- **Accès public** : https://trikwi-p13-agent-echecs.hf.space

### 3. Modèle économique
- **Coût du POC** : **0,00 €** (données libres, modèles open source, hébergement local).
- **Projection cloud managé** : ~**0,0025 € / requête (0,25 centime)** (option Claude Haiku mesurée, < 0,10 € / élève / mois).

---

## Diapo 12 - Perspective : analyse vidéo (Partie 2)

**Objectif de l'étude** : indexer les vidéos pédagogiques par position d'échiquier exacte (horodatage au coup près).

```
vidéo -> extraction d'images -> détection de l'échiquier -> position FEN -> agent existant
```

1. **Faisabilité** : Reconnaissance visuelle 2D sur screencasts et conversion des positions en FEN validées par `python-chess`.
2. **Intégration MCP** : Architecture modulaire reposant sur 4 serveurs d'outils FastMCP réutilisant directement le moteur et la base vectorielle du POC.
3. **Stratégie MVP** : Exploitation prioritaire des transcripts et vidéos sous licence Creative Commons pour respecter les CGU de diffusion.
4. **Chiffrage** : Build MVP estimé à **15-20 k€** (30-40 j-h) ; coût de traitement automatisé de **0,10 à 0,15 € / vidéo** (facteur x50 à x100 vs indexation manuelle).

*Étude d'ingénierie réalisée (note détaillée, schéma d'architecture MCP, modèle de coûts) : développement hors périmètre du POC.*

---

## Diapo 13 - Ce que le POC démontre

- **Objectif du POC** : fournir un accompagnement pédagogique disponible à la demande.
- **Agent fonctionnel** : Reconnaissance théorique immédiate, bascule moteur sur sortie de théorie, explications sourcées.
- **Déjà intégré (Dépassement du périmètre)** : Mode Robot Stockfish avec niveau Elo paramétrable (1200 à 2200) et mode saisie libre avec relais Chessbot.
- **Déploiement éprouvé** : Initialisation locale en 2 min 09 et démonstrateur public en ligne sur Hugging Face Spaces.
- **Prochaines évolutions** : Phase pilote auprès des jeunes espoirs FFE, serveurs d'outils MCP pour l'analyse vidéo, extension du corpus aux 500 codes ECO.

**-> Place à la démonstration en direct et aux échanges.**

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
