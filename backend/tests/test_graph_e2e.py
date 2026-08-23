"""Le graphe de bout en bout, services mockés — les trois trajets types."""

from graph import nodes
from graph.build import get_graph

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

ITALIENNE = {
    "white": 25000,
    "draws": 15000,
    "black": 8726,
    "opening": {"eco": "C50", "name": "Italian Game"},
    "moves": [{"uci": "e2e4", "san": "e4", "white": 60, "draws": 40, "black": 30}],
    "topGames": [{"white": {"name": "Caruana"}, "black": {"name": "Carlsen"}, "year": 2020}],
}

HORS_THEORIE = {"white": 0, "draws": 0, "black": 0, "opening": None, "moves": [], "topGames": []}

EVAL = {"cp": -110, "mate": None, "depth": 12, "best_line": ["d4", "d5"], "engine": "stockfish"}


FICHE_WIKI = {
    "text": "Partie italienne > Partie italienne > Introduction —\nLe fou en c4 vise f7.",
    "score": 0.7,
    "source_url": "https://fr.wikipedia.org/wiki/Partie_italienne",
    "opening_name": "Partie italienne",
    "lang": "fr",
    "section": "Introduction",
    "ouverture": "italienne",
}


def test_trajet_theorie(monkeypatch) -> None:
    monkeypatch.setattr(nodes.theory, "masters_with_cache", lambda board: (ITALIENNE, False))
    monkeypatch.setattr(nodes.rag, "search", lambda requete, eco=None, rayon=None: [FICHE_WIKI])
    monkeypatch.setattr(nodes.service_videos, "rechercher", lambda terme, maxi=3: [])
    result = get_graph().invoke({"fen": START_FEN})
    assert "Italian Game" in result["answer"]
    assert "e4" in result["answer"]
    assert "Caruana" in result["answer"]
    assert "f7" in result["answer"]  # l'extrait de la bibliothèque est dans la réponse
    assert any("Lichess" in s for s in result["sources"])
    assert any("wikipedia" in s for s in result["sources"])  # attribution CC BY-SA
    assert result["videos"] == []  # stub É4 toujours traversé


def test_trajet_moteur(monkeypatch) -> None:
    monkeypatch.setattr(nodes.theory, "masters_with_cache", lambda board: (HORS_THEORIE, False))
    monkeypatch.setattr(nodes.evaluation, "evaluate_with_cache", lambda board, depth: (EVAL, False))
    result = get_graph().invoke({"fen": START_FEN})
    assert "sort de la théorie" in result["answer"]
    assert "Stockfish" in result["answer"]
    assert "1.1 pion" in result["answer"]
    assert any("Stockfish" in s for s in result["sources"])


def test_trajet_fen_invalide(monkeypatch) -> None:
    def interdit(board):
        raise AssertionError("l'explorer ne doit pas être appelé sur un FEN invalide")

    monkeypatch.setattr(nodes.theory, "masters_with_cache", interdit)
    result = get_graph().invoke({"fen": "charabia"})
    assert "position" in result["answer"].lower()
    assert result["sources"] == []


def test_trajet_degrade_lichess_ko(monkeypatch) -> None:
    def boom(board):
        raise nodes.lichess.LichessUnavailable("panne simulée")

    monkeypatch.setattr(nodes.theory, "masters_with_cache", boom)
    monkeypatch.setattr(nodes.evaluation, "evaluate_with_cache", lambda board, depth: (EVAL, False))
    result = get_graph().invoke({"fen": START_FEN})
    assert "Stockfish" in result["answer"]  # bascule moteur
    assert "indisponibles" in result["answer"]  # la note d'incident
