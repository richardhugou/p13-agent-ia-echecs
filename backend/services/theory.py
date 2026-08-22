"""Théorie : explorer masters + cache, mise en forme des coups légaux et parties de référence."""

import chess

from services import lichess
from services.board import normalize_fen
from services.cache import get_cache


def masters_with_cache(board: chess.Board) -> tuple[dict, bool]:
    """Réponse explorer pour la position (cache 24 h). Retourne (données, servi_par_cache)."""
    key = normalize_fen(board)
    cache = get_cache()
    data = cache.get_explorer(key)
    if data is not None:
        return data, True
    data = lichess.fetch_masters(board.fen())
    cache.set_explorer(key, data)
    return data, False


def total_games(data: dict) -> int:
    return data.get("white", 0) + data.get("draws", 0) + data.get("black", 0)


def legal_moves_payload(board: chess.Board, data: dict) -> list[dict]:
    """Coups de l'explorer filtrés sur les coups légaux — garde-fou objectif O1."""
    legal_uci = {move.uci() for move in board.legal_moves}
    moves = []
    for move in data.get("moves", []):
        if move.get("uci") not in legal_uci:
            continue
        games = move.get("white", 0) + move.get("draws", 0) + move.get("black", 0)
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
    return moves


def top_games_payload(data: dict) -> list[dict]:
    return [
        {
            "white": game.get("white", {}).get("name"),
            "black": game.get("black", {}).get("name"),
            "year": game.get("year"),
            "winner": game.get("winner"),
        }
        for game in data.get("topGames", [])
    ]
