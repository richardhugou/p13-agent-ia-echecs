"""Routes de l'agent — la logique métier vit dans services/, ici on traduit en HTTP."""

import chess
from fastapi import APIRouter, HTTPException, Query

from config import get_settings
from services import engine, lichess
from services.board import normalize_fen, parse_fen
from services.cache import get_cache

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
    key = normalize_fen(board)
    cache = get_cache()

    data = cache.get_explorer(key)
    cached = data is not None
    if data is None:
        try:
            data = lichess.fetch_masters(board.fen())
        except lichess.LichessRateLimited as exc:
            raise HTTPException(
                status_code=503, detail=str(exc), headers={"Retry-After": "60"}
            ) from exc
        except lichess.LichessUnavailable as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        cache.set_explorer(key, data)

    legal_uci = {move.uci() for move in board.legal_moves}
    moves = []
    for move in data.get("moves", []):
        games = move.get("white", 0) + move.get("draws", 0) + move.get("black", 0)
        if move.get("uci") not in legal_uci:
            continue  # garde-fou objectif O1 : jamais un coup illégal en sortie
        moves.append(
            {
                "uci": move["uci"],
                "san": move.get("san"),
                "games": games,
                "white": move.get("white", 0),
                "draws": move.get("draws", 0),
                "black": move.get("black", 0),
            }
        )

    total_games = data.get("white", 0) + data.get("draws", 0) + data.get("black", 0)
    return {
        "fen": board.fen(),
        "opening": data.get("opening"),
        "in_theory": total_games >= settings.theory_min_games,
        "total_games": total_games,
        "moves": moves,
        "top_games": [
            {
                "white": game.get("white", {}).get("name"),
                "black": game.get("black", {}).get("name"),
                "year": game.get("year"),
                "winner": game.get("winner"),
            }
            for game in data.get("topGames", [])
        ],
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
    key = f"{normalize_fen(board)}|d{effective_depth}"
    cache = get_cache()

    result = cache.get_eval(key)
    cached = result is not None
    if result is None:
        try:
            result = engine.evaluate(board, depth=effective_depth)
        except engine.EngineUnavailable as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        cache.set_eval(key, result)

    return {"fen": board.fen(), **result, "cached": cached}
