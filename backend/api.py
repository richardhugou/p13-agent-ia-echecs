"""Routes de l'agent — la logique métier vit dans services/, ici on traduit en HTTP."""

import chess
from fastapi import APIRouter, HTTPException, Query

from config import get_settings
from services import engine, evaluation, lichess, theory
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
