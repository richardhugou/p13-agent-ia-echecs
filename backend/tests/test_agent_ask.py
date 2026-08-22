from fastapi.testclient import TestClient

from graph import nodes
from main import app
from tests.test_graph_e2e import EVAL, HORS_THEORIE, ITALIENNE, START_FEN

client = TestClient(app)


def test_ask_theorie(monkeypatch) -> None:
    monkeypatch.setattr(nodes.theory, "masters_with_cache", lambda board: (ITALIENNE, False))
    monkeypatch.setattr(nodes.rag, "search", lambda requete, eco=None: [])
    monkeypatch.setattr(nodes.service_videos, "rechercher", lambda terme, maxi=3: [])
    response = client.post("/api/v1/agent/ask", json={"fen": START_FEN})
    assert response.status_code == 200
    body = response.json()
    assert body["opening"]["eco"] == "C50"
    assert body["in_theory"] is True
    assert body["theory_moves"][0]["san"] == "e4"
    assert "Italian Game" in body["answer"]
    assert body["engine_eval"] is None


def test_ask_moteur(monkeypatch) -> None:
    monkeypatch.setattr(nodes.theory, "masters_with_cache", lambda board: (HORS_THEORIE, False))
    monkeypatch.setattr(nodes.evaluation, "evaluate_with_cache", lambda board, depth: (EVAL, False))
    body = client.post("/api/v1/agent/ask", json={"fen": START_FEN}).json()
    assert body["in_theory"] is False
    assert body["engine_eval"]["cp"] == -110
    assert body["theory_moves"] == []


def test_ask_fen_invalide_reponse_pedagogique(monkeypatch) -> None:
    monkeypatch.setattr(
        nodes.theory, "masters_with_cache", lambda board: (_ for _ in ()).throw(AssertionError)
    )
    response = client.post("/api/v1/agent/ask", json={"fen": "charabia"})
    assert response.status_code == 200  # l'agent répond, il ne rejette pas
    assert "position" in response.json()["answer"].lower()
