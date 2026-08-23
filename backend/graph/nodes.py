"""Les nœuds du graphe — chacun enrobe un service, écrit dans l'état, et gère son plan B."""

from config import get_settings
from graph.state import AgentState
from services import engine, evaluation, lichess, rag, theory
from services import videos as service_videos
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
    """La bibliothèque : fiches wiki les plus proches de la question (ou de l'ouverture).

    Requête = la question de l'élève si présente, sinon les idées de l'ouverture
    identifiée. Ni l'une ni l'autre → rien à chercher. Plan B : bibliothèque
    injoignable → on continue sans fiches, avec une note d'incident.
    """
    question = state.get("question")
    opening = state.get("opening") or {}
    if not question and not opening.get("name"):
        return {"rag_chunks": []}
    # Règle des rayons signés (décision du 26/08) : le corpus n'est consulté que dans un
    # rayon établi — par la position, sinon par le nom d'ouverture dans la question.
    # Hors des 8 rayons du manifeste → zéro fiche : une citation trompeuse est impossible.
    rayon = rag.eco_vers_ouverture(opening.get("eco")) or rag.rayon_depuis_question(question)
    if not rayon:
        return {"rag_chunks": [], "rag_hors_bibliotheque": True}
    requete = question or f"Idées principales et plans de l'ouverture {opening.get('name')}"
    try:
        chunks = rag.search(requete, rayon=rayon)
    except rag.RagUnavailable as exc:
        return {
            "rag_chunks": [],
            "errors": state.get("errors", []) + [f"bibliothèque indisponible : {exc}"],
        }
    return {"rag_chunks": chunks}


def videos(state: AgentState) -> dict:
    """Vidéos pédagogiques pour l'ouverture identifiée. Plan B : on continue sans vidéos."""
    opening = state.get("opening") or {}
    rayon = rag.eco_vers_ouverture(opening.get("eco"))
    terme = service_videos.NOMS_FR.get(rayon) or opening.get("name")
    if not terme:
        return {"videos": []}
    try:
        return {"videos": service_videos.rechercher(terme)}
    except service_videos.VideosUnavailable as exc:
        return {
            "videos": [],
            "errors": state.get("errors", []) + [f"vidéos indisponibles : {exc}"],
        }
