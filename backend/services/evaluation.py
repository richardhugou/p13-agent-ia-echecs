"""Évaluation : Stockfish + cache persistant (une position n'est jamais recalculée)."""

import chess

from services import engine
from services.board import normalize_fen
from services.cache import get_cache


def evaluate_with_cache(board: chess.Board, depth: int) -> tuple[dict, bool]:
    """Évaluation de la position (cache MongoDB sans TTL). Retourne (résultat, servi_par_cache)."""
    key = f"{normalize_fen(board)}|d{depth}"
    cache = get_cache()
    result = cache.get_eval(key)
    if result is not None:
        return result, True
    result = engine.evaluate(board, depth=depth)
    cache.set_eval(key, result)
    return result, False
