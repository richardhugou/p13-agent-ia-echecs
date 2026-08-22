# 08 — Script de démonstration (8 minutes) + plans B

## 1. Checklist AVANT la démo (la veille + H-1)

- [ ] `docker compose up -d` la veille sur la machine de démo ; healthcheck vert.
- [ ] **Caches chauds** : dérouler une fois tout le scénario → Lichess/YouTube/évals en cache MongoDB (la démo ne dépend plus du réseau ni des quotas).
- [ ] Vérifier le quota YouTube restant ; sinon basculer le flag « fixtures ».
- [ ] Warm-up embeddings (une recherche vectorielle à vide) — pas de cold start devant le jury.
- [ ] MLflow ouvert dans un onglet (runs baseline vs amélioré visibles).
- [ ] **Plan B enregistré** : screencast complet du scénario (à enregistrer en É6, jour du test d'installation fraîche).
- [ ] Onglets prêts : app (4200), Swagger (8000), MLflow (5001 — 5000 hôte squatté par AirPlay). Notifications coupées.

## 2. Scénario minuté

### Séquence 0 — Lancement (30 s)
Une seule commande (`docker compose up`), montrer les services qui passent healthy. Message : « livraison = 1 commande ».

### Séquence 1 — Position initiale, l'élève joue 1.e4 (1 min 30)
- Jouer **1.e4** sur l'échiquier.
- Attendu : panneau agent → coups théoriques (e5, c5, e6, c6…) avec statistiques masters (nb parties, % W/D/L), début d'explication « débuts ouverts ».
- Phrase : « les coups ne sortent pas du LLM : ce sont les statistiques de la théorie ».

### Séquence 2 — L'Italienne : théorie + RAG + vidéo (2 min 30)
- Amener la position : **1.e4 e5 2.Cf3 Cc6 3.Fc4**
- FEN attendu : `r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3`
- Attendu : ouverture identifiée « Partie Italienne (C50) » ; suites théoriques (3…Fc5 Giuoco Piano, 3…Cf6 Deux Cavaliers) ; **contexte RAG avec sources citées** ; partie historique de référence ; **vidéo YouTube intégrée**.
- Phrase : « le texte vient d'un corpus indexé sous licence libre — les sources sont cliquables ».

### Séquence 3 — Question libre au chat (1 min)
- Taper : « Pourquoi joue-t-on 3.Fc4 ? »
- Attendu : réponse pédagogique sourcée (pression sur f7, développement rapide), cohérente avec la position affichée.

### Séquence 4 — Sortie de théorie → Stockfish (2 min)
- Jouer : **3…Fc5 4.g4?!**
- FEN attendu : `r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P1P1/5N2/PPPP1P1P/RNBQK2R b KQkq g3 0 4`
- Attendu : le routeur bascule branche **moteur** (position quasi absente des parties de maîtres) ; évaluation Stockfish négative pour les Blancs (ordre de grandeur −1 à −2 pions, **annoncer la valeur mesurée en répétition, pas de promesse**) + meilleure suite + explication « pourquoi c'est douteux ».
- Phrase : « hors des sentiers battus, l'agent change d'outil : évaluation objective au lieu de théorie » — montrer la trace du chemin dans MLflow.

### Séquence 5 — Sous le capot (30 s, optionnel selon jury)
Swagger : un appel `/agent/ask` brut → blocs structurés (coups/contexte/vidéos/éval + sources). MLflow : le run d'éval avant/après.

## 3. Pannes possibles pendant la démo → réflexes

| Symptôme | Réflexe immédiat |
|---|---|
| Réseau coupé | Continuer : tout le scénario est en cache/fixtures (c'est prévu ET c'est un argument) |
| Latence LLM anormale | Commenter la trace MLflow pendant l'attente ; si > 20 s, basculer sur la vidéo plan B |
| Pas de vidéo retournée | Dire que le fallback « réponse sans vidéo » est un comportement conçu, montrer le cache |
| Échiquier désynchronisé | Bouton refresh du starter → recharger le FEN de la séquence |
| Compose cassé sur la machine de démo | Vidéo plan B + Swagger sur machine de secours |

## 4. Positions de secours (variété si le jury veut « autre chose »)
- Sicilienne : `rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2` (après 1.e4 c5)
- Française : après 1.e4 e6 — montre une autre famille indexée.
- Position illégale (2 rois blancs, à préparer) : montre la validation FEN et l'erreur pédagogique.

## 5. Ce que la démo doit PROUVER (relire avant d'entrer)
1. Le routage intelligent théorie/moteur (cœur de l'agent). 2. Les sources citées (RAG honnête). 3. La résilience (caches, fallbacks). 4. La mesure (MLflow). 5. La livraison en une commande.
