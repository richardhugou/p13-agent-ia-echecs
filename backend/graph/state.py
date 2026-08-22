"""L'état partagé du graphe — le dossier que chaque nœud enrichit puis transmet."""

from typing import TypedDict


class AgentState(TypedDict, total=False):
    # Entrées
    fen: str
    question: str | None

    # Produit par valider_fen
    fatal_error: str | None  # FEN invalide : on s'arrête avec une réponse pédagogique

    # Produit par identifier_ouverture
    opening: dict | None  # {eco, name} ou None
    in_theory: bool
    total_games: int
    explorer_data: dict | None  # réponse brute, réutilisée par coups_theoriques

    # Produit par les branches du routeur
    theory_moves: list[dict]
    top_games: list[dict]
    engine_eval: dict | None  # {cp, mate, depth, best_line}

    # Produit par les stubs (É3/É4) puis leurs vraies implémentations
    rag_chunks: list[dict]
    videos: list[dict]

    # Produit par la synthèse
    answer: str
    sources: list[str]

    # Incidents non fatals accumulés en chemin (l'agent dégrade, ne plante pas)
    errors: list[str]
