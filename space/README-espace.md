---
title: Coach IA Ouvertures d'Echecs (Full Stack GPU)
emoji: 🐎
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
suggested_hardware: t4-small
pinned: false
---

# Coach IA d'ouvertures d'échecs — Déploiement Complet (GPU T4)

Application complète « Agent IA pour l'apprentissage des ouvertures d'échecs » (mission FFE / Cavalier Data).

## Architecture embarquée
- **Frontend** : Interface Angular 17 complète avec échiquier interactif responsive, 4 modes de jeu (Guidé, Simulation, Robot Stockfish Elo 1200-2200, Relais libre).
- **Orchestration** : Backend FastAPI avec graphe déterministe LangGraph.
- **Théorie & Moteur** : Intégration Lichess Opening Explorer + moteur Stockfish UCI.
- **Base documentaire** : Base vectorielle Milvus Lite (477 fiches structurées avec filtres scalaires).
- **Modèle de langage (LLM)** : Serveur Ollama avec modèle Qwen accéléré par GPU NVIDIA T4 (VRAM 16 Go).

## Configuration
- Secret recommandé : `LICHESS_API_TOKEN` (jeton personnel Lichess gratuit pour requêtes non bridées).

Auteur : Richard Hugou — Dépôt officiel : https://github.com/richardhugou/p13-agent-ia-echecs
