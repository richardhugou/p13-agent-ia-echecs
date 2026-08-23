"""Validation des positions FEN — la porte d'entrée de tout le système."""

import chess


def parse_fen(fen: str) -> chess.Board:
    """Retourne un Board valide ou lève ValueError avec un message pédagogique."""
    try:
        board = chess.Board(fen)
    except ValueError as exc:
        raise ValueError(f"FEN invalide : {exc}") from exc
    if not board.is_valid():
        raise ValueError(f"Position illégale : {board.status()!r}")
    return board


def normalize_fen(board: chess.Board) -> str:
    """Clé de cache : les 4 premiers champs FEN (pièces, trait, roques, en passant).

    Les compteurs de coups ne changent pas la nature de la position.
    """
    return " ".join(board.fen().split()[:4])
