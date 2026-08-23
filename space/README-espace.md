---
title: Coach IA Ouvertures d'Echecs
emoji: ♞
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Coach IA d'ouvertures d'échecs — vitrine du POC FFE

Démo publique du POC « Agent IA pour l'apprentissage des échecs » (projet OpenClassrooms, mission fictive FFE / Cavalier Data).

**Ce que fait la vitrine** : choisis ton camp, une ouverture à travailler — l'agent joue les coups de ton adversaire (les plus joués par les maîtres), affiche les suggestions sur l'échiquier, explique avec sources, recommande des vidéos, et bascule sur l'évaluation Stockfish hors théorie.

**Variante allégée, assumée** : un seul conteneur — Milvus Lite embarqué (477 fiches pré-vectorisées), embeddings Qwen3-0.6B sur CPU, synthèse par gabarit déterministe (pas de LLM ici), sans cache MongoDB. La version complète (7 conteneurs, LLM local qwen3.5:4b via Ollama) s'installe en une commande depuis le dépôt : **https://github.com/richardhugou/p13-agent-ia-echecs** (`./demarrer.sh`, installation fraîche mesurée : 2 min 09).

Secret requis pour la théorie : `LICHESS_API_TOKEN` (jeton personnel gratuit, aucun scope). Première requête d'embedding : quelques secondes (CPU).

Auteur : Richard Hugou — code sous licence du dépôt ; données Lichess CC0, corpus Wikipédia/Wikibooks CC BY-SA, Stockfish GPLv3.
