"""Les nœuds du graphe — chacun enrobe un service, écrit dans l'état, et gère son plan B."""

from config import get_settings
from graph.state import AgentState
from services import engine, evaluation, lichess, theory
from services.board import parse_fen


def valider_fen(state: AgentState) -> dict:
    """Porte d'entrée : position légale ou réponse pédagogique immédiate."""
    try:
        board = parse_fen(state["fen"])
    except ValueError as exc:
        return {
            "fatal_error": str(exc),
            "answer": (
                f"Je ne peux pas lire cette position ({exc}). "
                "Rejoue le coup sur l'échiquier et je reprends l'analyse."
            ),
            "sources": [],
        }
    return {"fen": board.fen(), "fatal_error": None}


def apres_validation(state: AgentState) -> str:
    return "stop" if state.get("fatal_error") else "continue"


def identifier_ouverture(state: AgentState) -> dict:
    """Nomme l'ouverture et mesure la présence en théorie. Plan B : Lichess KO → branche moteur."""
    settings = get_settings()
    board = parse_fen(state["fen"])
    try:
        data, _ = theory.masters_with_cache(board)
    except (lichess.LichessUnavailable, lichess.LichessRateLimited) as exc:
        return {
            "opening": None,
            "in_theory": False,
            "total_games": 0,
            "explorer_data": None,
            "errors": state.get("errors", []) + [f"théorie indisponible : {exc}"],
        }
    total = theory.total_games(data)
    return {
        "opening": data.get("opening"),
        "in_theory": total >= settings.theory_min_games,
        "total_games": total,
        "explorer_data": data,
    }


def route_theorie_ou_moteur(state: AgentState) -> str:
    """LE routeur — déterministe : seuil de parties masters, jamais un choix LLM."""
    return "theorie" if state.get("in_theory") else "moteur"


def coups_theoriques(state: AgentState) -> dict:
    """Branche théorie : coups joués par les maîtres, filtrés sur les coups légaux (O1)."""
    board = parse_fen(state["fen"])
    data = state.get("explorer_data") or {}
    return {
        "theory_moves": theory.legal_moves_payload(board, data),
        "top_games": theory.top_games_payload(data),
    }


def evaluer_position(state: AgentState) -> dict:
    """Branche moteur : évaluation objective. Plan B : moteur KO → on continue sans éval."""
    settings = get_settings()
    board = parse_fen(state["fen"])
    try:
        result, _ = evaluation.evaluate_with_cache(board, settings.stockfish_depth)
    except engine.EngineUnavailable as exc:
        return {
            "engine_eval": None,
            "errors": state.get("errors", []) + [f"moteur indisponible : {exc}"],
        }
    return {"engine_eval": result}


def contexte_rag(state: AgentState) -> dict:
    """Stub É3 : la recherche documentaire Milvus branchera ici. Vide, sans casser le flux."""
    return {"rag_chunks": []}


def videos(state: AgentState) -> dict:
    """Stub É4 : la recherche YouTube branchera ici. Vide, sans casser le flux."""
    return {"videos": []}
