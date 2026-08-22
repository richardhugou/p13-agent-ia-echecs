"""Évaluation Stockfish via python-chess (UCI) — moteur unique, accès sérialisé."""

import shutil
import threading

import chess
import chess.engine

from config import get_settings

_lock = threading.Lock()
_engine: chess.engine.SimpleEngine | None = None


class EngineUnavailable(Exception):
    """Binaire Stockfish introuvable ou moteur mort."""


def _resolve_path() -> str:
    settings = get_settings()
    path = settings.stockfish_path or shutil.which("stockfish") or "/usr/games/stockfish"
    if not shutil.which(path):
        raise EngineUnavailable(f"Stockfish introuvable ({path!r}) — définir STOCKFISH_PATH")
    return path


def _get_engine() -> chess.engine.SimpleEngine:
    global _engine
    if _engine is None:
        _engine = chess.engine.SimpleEngine.popen_uci(_resolve_path())
    return _engine


def evaluate(board: chess.Board, depth: int | None = None) -> dict:
    """Évalue une position. Score toujours du point de vue des Blancs (convention UI)."""
    settings = get_settings()
    limit = chess.engine.Limit(
        depth=depth or settings.stockfish_depth,
        time=settings.stockfish_time_ms / 1000,
    )
    with _lock:
        try:
            info = _get_engine().analyse(board, limit)
        except chess.engine.EngineError as exc:
            raise EngineUnavailable(f"Erreur moteur : {exc}") from exc

    score = info["score"].pov(chess.WHITE)
    line_board = board.copy()
    best_line = []
    for move in info.get("pv", [])[:8]:
        best_line.append(line_board.san(move))
        line_board.push(move)

    return {
        "cp": score.score(),
        "mate": score.mate(),
        "depth": info.get("depth"),
        "best_line": best_line,
        "engine": "stockfish",
    }


def shutdown() -> None:
    global _engine
    if _engine is not None:
        _engine.quit()
        _engine = None
