import pytest

from graph import nodes
from services import lichess

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

MASTERS_FIXTURE = {
    "white": 100,
    "draws": 80,
    "black": 60,
    "opening": {"eco": "C50", "name": "Italian Game"},
    "moves": [
        {"uci": "e2e4", "san": "e4", "white": 60, "draws": 40, "black": 30},
        {"uci": "e7e5", "san": "e5", "white": 5, "draws": 5, "black": 5},
    ],
    "topGames": [{"white": {"name": "Caruana"}, "black": {"name": "Carlsen"}, "year": 2020}],
}


def test_valider_fen_ok() -> None:
    result = nodes.valider_fen({"fen": START_FEN})
    assert result["fatal_error"] is None
    assert nodes.apres_validation(result) == "continue"


def test_valider_fen_invalide() -> None:
    result = nodes.valider_fen({"fen": "grosse bêtise"})
    assert result["fatal_error"]
    assert "position" in result["answer"].lower()
    assert nodes.apres_validation(result) == "stop"


def test_identifier_ouverture_en_theorie(monkeypatch) -> None:
    monkeypatch.setattr(nodes.theory, "masters_with_cache", lambda board: (MASTERS_FIXTURE, False))
    result = nodes.identifier_ouverture({"fen": START_FEN})
    assert result["opening"]["eco"] == "C50"
    assert result["total_games"] == 240
    assert result["in_theory"] is True
    assert result["explorer_data"] is MASTERS_FIXTURE


def test_identifier_ouverture_sous_le_seuil(monkeypatch) -> None:
    petit = {**MASTERS_FIXTURE, "white": 2, "draws": 1, "black": 1}  # 4 < seuil 5
    monkeypatch.setattr(nodes.theory, "masters_with_cache", lambda board: (petit, False))
    result = nodes.identifier_ouverture({"fen": START_FEN})
    assert result["in_theory"] is False


def test_identifier_ouverture_lichess_ko(monkeypatch) -> None:
    def boom(board):
        raise lichess.LichessUnavailable("timeout")

    monkeypatch.setattr(nodes.theory, "masters_with_cache", boom)
    result = nodes.identifier_ouverture({"fen": START_FEN})
    assert result["in_theory"] is False
    assert result["explorer_data"] is None
    assert "théorie indisponible" in result["errors"][0]


def test_routeur_deterministe() -> None:
    assert nodes.route_theorie_ou_moteur({"in_theory": True}) == "theorie"
    assert nodes.route_theorie_ou_moteur({"in_theory": False}) == "moteur"
    assert nodes.route_theorie_ou_moteur({}) == "moteur"


def test_coups_theoriques_filtre_les_illegaux() -> None:
    state = {"fen": START_FEN, "explorer_data": MASTERS_FIXTURE}
    result = nodes.coups_theoriques(state)
    ucis = [m["uci"] for m in result["theory_moves"]]
    assert "e2e4" in ucis
    assert "e7e5" not in ucis  # coup noir au trait blanc → filtré (O1)
    assert result["top_games"][0]["white"] == "Caruana"


def test_evaluer_position(monkeypatch) -> None:
    fake = {"cp": 38, "mate": None, "depth": 12, "best_line": ["e4"], "engine": "stockfish"}
    monkeypatch.setattr(nodes.evaluation, "evaluate_with_cache", lambda board, depth: (fake, False))
    result = nodes.evaluer_position({"fen": START_FEN})
    assert result["engine_eval"]["cp"] == 38


def test_evaluer_position_moteur_ko(monkeypatch) -> None:
    def boom(board, depth):
        raise nodes.engine.EngineUnavailable("binaire absent")

    monkeypatch.setattr(nodes.evaluation, "evaluate_with_cache", boom)
    result = nodes.evaluer_position({"fen": START_FEN})
    assert result["engine_eval"] is None
    assert "moteur indisponible" in result["errors"][0]


def test_stubs_ne_cassent_pas_le_flux() -> None:
    assert nodes.contexte_rag({}) == {"rag_chunks": []}
    assert nodes.videos({}) == {"videos": []}


@pytest.mark.parametrize("total,attendu", [(4, False), (5, True), (6, True)])
def test_seuil_exact_du_routeur(monkeypatch, total, attendu) -> None:
    fixture = {**MASTERS_FIXTURE, "white": total, "draws": 0, "black": 0}
    monkeypatch.setattr(nodes.theory, "masters_with_cache", lambda board: (fixture, False))
    result = nodes.identifier_ouverture({"fen": START_FEN})
    assert result["in_theory"] is attendu


def test_contexte_rag_requete_depuis_ouverture(monkeypatch) -> None:
    recu = {}

    def espion(requete, eco=None):
        recu.update(requete=requete, eco=eco)
        return [{"text": "x", "source_url": "u"}]

    monkeypatch.setattr(nodes.rag, "search", espion)
    out = nodes.contexte_rag({"opening": {"name": "Italian Game", "eco": "C50"}})
    assert out["rag_chunks"][0]["source_url"] == "u"
    assert "Italian Game" in recu["requete"] and recu["eco"] == "C50"


def test_contexte_rag_question_prioritaire(monkeypatch) -> None:
    recu = {}
    monkeypatch.setattr(
        nodes.rag, "search", lambda requete, eco=None: recu.update(requete=requete) or []
    )
    nodes.contexte_rag({"question": "pourquoi f7 ?", "opening": {"name": "X", "eco": "C50"}})
    assert recu["requete"] == "pourquoi f7 ?"


def test_contexte_rag_rien_a_chercher(monkeypatch) -> None:
    def interdit(*a, **k):
        raise AssertionError("la bibliothèque ne doit pas être appelée sans requête")

    monkeypatch.setattr(nodes.rag, "search", interdit)
    assert nodes.contexte_rag({}) == {"rag_chunks": []}


def test_contexte_rag_indisponible(monkeypatch) -> None:
    def boom(requete, eco=None):
        raise nodes.rag.RagUnavailable("Milvus éteint")

    monkeypatch.setattr(nodes.rag, "search", boom)
    out = nodes.contexte_rag({"opening": {"name": "X", "eco": "C50"}})
    assert out["rag_chunks"] == []
    assert "bibliothèque indisponible" in out["errors"][0]
