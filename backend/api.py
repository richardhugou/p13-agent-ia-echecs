"""Routes de l'agent — la logique métier vit dans services/, ici on traduit en HTTP."""

import chess
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from config import get_settings
from graph.build import get_graph
from services import engine, evaluation, lichess, rag, theory
from services import videos as service_videos
from services.board import parse_fen

router = APIRouter(prefix="/api/v1")


def _parse_or_400(fen: str) -> chess.Board:
    try:
        return parse_fen(fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/moves")
def theoretical_moves(fen: str = Query(..., description="Position FEN complète")) -> dict:
    """Coups théoriques (base masters Lichess) : stats et parties de référence."""
    settings = get_settings()
    board = _parse_or_400(fen)
    try:
        data, cached = theory.masters_with_cache(board)
    except lichess.LichessRateLimited as exc:
        raise HTTPException(
            status_code=503, detail=str(exc), headers={"Retry-After": "60"}
        ) from exc
    except lichess.LichessUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    total = theory.total_games(data)
    return {
        "fen": board.fen(),
        "opening": data.get("opening"),
        "in_theory": total >= settings.theory_min_games,
        "total_games": total,
        "moves": theory.legal_moves_payload(board, data),
        "top_games": theory.top_games_payload(data),
        "cached": cached,
    }


@router.get("/evaluate")
def evaluate_position(
    fen: str = Query(..., description="Position FEN complète"),
    depth: int | None = Query(None, ge=4, le=30, description="Profondeur (défaut : config)"),
) -> dict:
    """Évaluation Stockfish (centipawns, point de vue Blancs) avec cache persistant."""
    settings = get_settings()
    board = _parse_or_400(fen)
    effective_depth = depth or settings.stockfish_depth
    try:
        result, cached = evaluation.evaluate_with_cache(board, effective_depth)
    except engine.EngineUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"fen": board.fen(), **result, "cached": cached}


@router.get("/engine-move")
def calculate_engine_move(
    fen: str = Query(..., description="Position FEN complète"),
    elo: int | None = Query(
        None, ge=800, le=3000, description="Niveau Elo cible (défaut : sans limite)"
    ),
    depth: int | None = Query(None, ge=1, le=30, description="Profondeur de recherche"),
) -> dict:
    """Calcul du coup joué par Stockfish avec calibration Elo optionnelle."""
    board = _parse_or_400(fen)
    try:
        res = engine.best_move(board, elo=elo, depth=depth)
    except engine.EngineUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"fen": board.fen(), **res}


@router.get("/videos")
def videos_pour_ouverture(
    opening: str = Query(..., description="Nom d'ouverture (FR de préférence)"),
    maxi: int = Query(3, ge=1, le=8, description="Nb de vidéos"),
) -> dict:
    """Vidéos pédagogiques (métadonnées YouTube, cache 7 j, filtres durée + titre)."""
    try:
        resultats = service_videos.rechercher(opening, maxi=maxi)
    except service_videos.VideosUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"opening": opening, "videos": resultats}


@router.get("/vector-search")
def vector_search(
    q: str = Query(..., description="Question en langage naturel (FR ou EN)"),
    k: int | None = Query(None, ge=1, le=20, description="Nb de fiches (défaut : config)"),
    eco: str | None = Query(None, description="Code ECO pour filtrer (ex. C50)"),
) -> dict:
    """Recherche sémantique dans la bibliothèque (Milvus), filtre par rayon d'ouverture.

    Endpoint diagnostic : le seuil d'abstention est désactivé ici (scores bruts visibles) ;
    il s'applique dans le graphe (nœud contexte_rag), sur le chemin de l'élève.
    """
    try:
        results = rag.search(q, eco=eco, k=k, score_min=0.0)
    except rag.RagUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"q": q, "rayon_filtre": rag.eco_vers_ouverture(eco), "results": results}


class AskRequest(BaseModel):
    fen: str
    question: str | None = None
    session_id: str | None = None


@router.post("/agent/ask")
def agent_ask(payload: AskRequest) -> dict:
    """Le parcours d'un coup, orchestré par le graphe. Réponse structurée en blocs + sources.

    Un FEN invalide renvoie 200 avec une réponse pédagogique : c'est l'agent qui
    répond à l'élève, pas le serveur qui rejette une requête.
    """
    state = get_graph().invoke({"fen": payload.fen, "question": payload.question})
    return {
        "fen": payload.fen,
        "answer": state.get("answer", ""),
        "sources": state.get("sources", []),
        "opening": state.get("opening"),
        "in_theory": state.get("in_theory"),
        "total_games": state.get("total_games", 0),
        "theory_moves": state.get("theory_moves", []),
        "top_games": state.get("top_games", []),
        "engine_eval": state.get("engine_eval"),
        "rag_chunks": state.get("rag_chunks", []),
        "videos": state.get("videos", []),
        "errors": state.get("errors", []),
    }
