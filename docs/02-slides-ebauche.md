# 02 — Ébauche des slides de soutenance

Format visé : **~20 min de présentation + démo, 16 slides** (hors annexes). Le fil narratif suit strictement :
fiction → problématique → « une IA qui… » → **données** → techno → application → exemples/baselines/résultats → plateforme & maintenance → étude d'évolution (partie 2) → conclusion.

Chaque slide : **Message clé** (une phrase que le jury doit retenir) / Contenu / Chiffres / Visuel / Notes orateur.

---

### Slide 1 — Titre
- **Message** : un agent IA pour l'apprentissage des ouvertures d'échecs.
- Contenu : titre, nom, date, logos fictifs (Cavalier Data × FFE), mention « POC — 2 semaines ».
- Visuel : échiquier stylisé.

### Slide 2 — La fiction : qui, pour qui, pourquoi
- **Message** : la FFE veut outiller ses jeunes espoirs avant les championnats d'Europe ; on est l'IA Engineer junior missionné pour un POC.
- Contenu : 3 blocs (Client FFE / Nous / La commande d'Alan), périmètre 2 semaines.
- Chiffres : > 60 000 licenciés ⚠️, ~60 % de jeunes ⚠️.
- Visuel : mini-organigramme de la mission (doc 01 §1).

### Slide 3 — Le problème en chiffres
- **Message** : la demande d'entraînement explose, l'offre d'entraîneurs ne suit pas.
- Chiffres : boom post-2020 ; Lichess ≈ 100 M parties/mois ⚠️ ; 30–60 €/h un entraîneur ; ≈ 69 000 milliards de suites après 5 coups chacun → on ne « mémorise » pas les échecs, on apprend la théorie.
- Visuel : 4 grandes tuiles chiffrées.
- Note orateur : chaque chiffre se conclut par « donc… ».

### Slide 4 — La problématique
- **Message** : « Comment donner à chaque jeune un retour de niveau entraîneur, à la demande ? »
- Contenu : la question, encadrée, seule. Puis 4 attentes : bons coups théoriques / explications / vidéos / évaluation objective hors théorie.
- **Interdit sur ce slide : tout mot technique (pas de RAG, pas de LangGraph).**

### Slide 5 — Notre réponse (encore sans techno)
- **Message** : une IA-coach qui observe l'échiquier et guide l'élève en continu.
- Contenu : parcours utilisateur en 4 temps (je joue → elle propose la théorie → elle explique et montre une vidéo → si je sors de la théorie, elle évalue).
- Visuel : storyboard 4 vignettes avec l'échiquier.

### Slide 6 — Cette IA a besoin de données : l'inventaire
- **Message** : tout existe déjà, ouvert et massif — notre travail est de le structurer.
- Contenu : les 4 familles de données + 1 outil (tableau doc 04 §1).
- Chiffres : ~3 500 lignes d'ouvertures nommées (ECO A00–E99) ; ≈ 2 M parties de maîtres (explorer Lichess) ⚠️ ; corpus wiki : **[MESURE] pages / [MESURE] tokens** ; YouTube : quota 10 000 unités/jour.
- Visuel : tableau sources × volumétrie × licence.

### Slide 7 — Le jeu de données du POC, en chiffres (slide EDA n°1)
- **Message** : voilà exactement ce qu'on indexe.
- Chiffres à remplir depuis l'EDA : nb documents par source, nb chunks, longueur moyenne (tokens), couverture des codes ECO, % doublons éliminés, langues.
- Visuel : bar chart docs/source + heatmap couverture ECO A–E. **[MESURE]**

### Slide 8 — Du brut à l'index : ETL (slide EDA n°2)
- **Message** : un pipeline reproductible Extract → Transform → Load, avec contrôles qualité.
- Contenu : schéma du pipeline (doc 04 §4) ; règles clés : normalisation FEN, chunking 300–500 tokens avec ~15 % d'overlap, métadonnées obligatoires, déduplication.
- Chiffres : embeddings 1024 dimensions (Qwen3-Embedding-0.6B) ; ~4 Ko/vecteur ; index total **[MESURE] Mo** ; temps d'ingestion **[MESURE]**.

### Slide 9 — Pourquoi un agent outillé (la baseline qui justifie tout)
- **Message** : un LLM seul joue mal et triche involontairement ; un LLM **outillé** devient fiable.
- Contenu : enseignements de la compétition Kaggle Game Arena (exhibition LLM vs LLM aux échecs, août 2025 ⚠️ à re-sourcer) : positions transmises en FEN + historique + coups légaux ; malgré ça, coups illégaux fréquents et niveau faible sans outils.
- Conclusion : le LLM n'invente jamais un coup chez nous — **la théorie vient de Lichess, l'évaluation de Stockfish, le LLM orchestre et explique**.
- Visuel : « LLM seul vs LLM outillé » en 2 colonnes.

### Slide 10 — Architecture (la techno, enfin)
- **Message** : un graphe de décision LangGraph qui route chaque position vers la bonne source.
- Contenu : schéma du graphe (doc 05 §2) + les 6 services Docker (Angular, FastAPI, Milvus, MongoDB, Stockfish embarqué, [MLflow]).
- Note orateur : justifier en 1 phrase chaque techno (tableau doc 05 §5) ; ne pas lire le schéma, raconter **le trajet d'une position FEN**.

### Slide 11 — Démo
- **Message** : ça tourne, en local, en une commande.
- Contenu : renvoi au script de démo (doc 08) : théorie → explication + vidéo → coup hors théorie → Stockfish.
- Plan B : captures + vidéo enregistrée.

### Slide 12 — Résultats : baseline vs version améliorée
- **Message** : on mesure, on ne « sent » pas.
- Contenu : tableau avant/après — run A (chunking naïf 1000 tokens, top-3) vs run B (chunking 400 + overlap, top-5) : recall@5 **[MESURE]** → **[MESURE]** ; coups illégaux 0 ; latence p95 **[MESURE]** ; coût/interaction **[MESURE] €**.
- Visuel : tableau MLflow (capture) — c'est notre preuve de rigueur.

### Slide 13 — La plateforme : mise à disposition & maintenance
- **Message** : un produit, pas un notebook.
- Contenu : parcours utilisateur dans l'UI Angular ; comment l'info est « goupillée » (panneau coups / contexte / vidéos) ; exploitation : caches MongoDB (quotas), volumes persistants, variables d'environnement, rafraîchissement hebdo de l'index, monitoring des traces.
- Visuel : capture UI annotée.

### Slide 14 — Et demain ? Le système d'analyse vidéo (partie 2)
- **Message** : transformer les vidéos YouTube en positions indexées — conçu, chiffré, pas développé.
- Contenu : bénéfices attendus / 3 limites majeures (CGU YouTube, précision détection, coûts) / architecture MCP en 1 schéma / coûts : **~0,10–0,15 €/vidéo** en opex, build MVP ~15–20 k€ (hypothèses doc livrables).
- Visuel : schéma MCP simplifié (livrables/schema-architecture-mcp.md).

### Slide 15 — Roadmap & risques
- **Message** : le POC est l'étape 1 d'une trajectoire réaliste.
- Contenu : POC → V1 (multi-utilisateurs, plus d'ouvertures, éval continue) → V2 (analyse vidéo MCP) ; top 3 risques et mitigations (doc 06 §5).

### Slide 16 — Conclusion + questions
- **Message** : objectifs O1–O6 atteints (tableau vert/orange), ce que j'ai appris, ouverture à la discussion.

---

## Annexes à préparer (slides de secours pour les questions)
- A1 : tableau complet des choix techno et alternatives (doc 05 §5).
- A2 : schéma détaillé du graphe LangGraph avec les états.
- A3 : détail du protocole d'évaluation RAG + gold set.
- A4 : tableau de coûts détaillé partie 2 (3 scénarios).
- A5 : conformité — licences des données (CC0/CC BY-SA/CGU YouTube), RGPD mineurs.
- A6 : audit matériel et contraintes Docker/macOS (doc 06 §1–2).

## Checklist de fabrication des slides
- [ ] Reprendre les chiffres ⚠️ et les sourcer (une note de bas de slide par source).
- [ ] Remplacer tous les **[MESURE]** par les valeurs réelles (jamais de chiffre inventé).
- [ ] 1 message par slide, max 5 lignes de texte, le reste à l'oral.
- [ ] Répéter la transition 5→6 (« pour faire ça, il faut des données ») et 9→10 (« voilà pourquoi cette architecture »).
- [ ] Minuter : 45–90 s par slide, démo 5–8 min.
