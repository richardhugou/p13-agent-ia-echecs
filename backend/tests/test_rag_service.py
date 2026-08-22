import httpx2
import pytest

from services import rag


def test_eco_vers_ouverture() -> None:
    assert rag.eco_vers_ouverture("C50") == "italienne"
    assert rag.eco_vers_ouverture("B22") == "sicilienne"
    assert rag.eco_vers_ouverture("E75") == "est_indienne"
    assert rag.eco_vers_ouverture("D35") == "gambit_dame"
    assert rag.eco_vers_ouverture("A40") is None  # hors des rayons du manifeste
    assert rag.eco_vers_ouverture("C57") is None  # deux cavaliers : hors bornes signées
    assert rag.eco_vers_ouverture(None) is None


class FakeMilvus:
    def __init__(self) -> None:
        self.dernier_filtre = None

    def search(self, collection, data, limit, filter, output_fields):
        self.dernier_filtre = filter
        return [
            [
                {
                    "distance": 0.712,
                    "entity": {
                        "text": "Partie italienne > Page > Section —\nLe fou vise f7.",
                        "source_url": "https://fr.wikipedia.org/wiki/Partie_italienne",
                        "opening_name": "Partie italienne",
                        "lang": "fr",
                        "section": "Introduction",
                        "ouverture": "italienne",
                    },
                }
            ]
        ]


def test_search_filtre_par_rayon(monkeypatch) -> None:
    fake = FakeMilvus()
    monkeypatch.setattr(rag, "_milvus", lambda: fake)
    monkeypatch.setattr(rag, "_embed_question", lambda q: [0.0])
    resultats = rag.search("pourquoi le fou en c4 ?", eco="C50")
    assert fake.dernier_filtre == 'ouverture == "italienne"'
    assert resultats[0]["score"] == 0.712
    assert "wikipedia" in resultats[0]["source_url"]


def test_search_sans_eco_sans_filtre(monkeypatch) -> None:
    fake = FakeMilvus()
    monkeypatch.setattr(rag, "_milvus", lambda: fake)
    monkeypatch.setattr(rag, "_embed_question", lambda q: [0.0])
    rag.search("question libre")
    assert fake.dernier_filtre == ""


def test_search_indisponible(monkeypatch) -> None:
    def boom(question):
        raise httpx2.HTTPError("ollama éteint")

    monkeypatch.setattr(rag, "_embed_question", boom)
    with pytest.raises(rag.RagUnavailable):
        rag.search("q")
