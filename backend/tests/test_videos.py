import pytest

from graph import nodes
from services import videos as sv


def test_duree_secondes() -> None:
    assert sv._duree_secondes("PT12M4S") == 724
    assert sv._duree_secondes("PT1H2M") == 3720
    assert sv._duree_secondes("PT45S") == 45


def test_titre_pertinent() -> None:
    assert sv._titre_pertinent("La Partie ITALIENNE expliquée", "partie italienne")
    assert sv._titre_pertinent("Caro-Kann pour débutants", "défense caro-kann")
    assert not sv._titre_pertinent("Top 10 des gaffes aux échecs", "partie italienne")


class FakeReponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        pass


RECHERCHE = {"items": [{"id": {"videoId": "abc123"}}, {"id": {"videoId": "def456"}}]}
DETAILS = {
    "items": [
        {
            "id": "abc123",
            "contentDetails": {"duration": "PT12M4S"},
            "status": {"embeddable": True},
            "snippet": {"title": "La partie italienne expliquée", "channelTitle": "Coach Échecs"},
        },
        {
            "id": "def456",
            "contentDetails": {"duration": "PT2M"},
            "status": {"embeddable": True},
            "snippet": {"title": "Italienne éclair", "channelTitle": "X"},
        },  # trop courte → filtrée
    ]
}


def _fake_get_factory(reponses: list):
    it = iter(reponses)

    def fake_get(url, params=None, timeout=None):
        return next(it)

    return fake_get


def test_rechercher_filtre_et_forme(monkeypatch) -> None:
    monkeypatch.setattr(
        sv,
        "get_settings",
        lambda: type("S", (), {"youtube_api_key": "k", "lichess_timeout_s": 5.0})(),
    )
    monkeypatch.setattr(
        sv.httpx2, "get", _fake_get_factory([FakeReponse(RECHERCHE), FakeReponse(DETAILS)])
    )
    resultats = sv.rechercher("partie italienne")
    assert len(resultats) == 1  # la vidéo de 2 min est filtrée
    assert resultats[0]["url"] == "https://www.youtube.com/watch?v=abc123"
    assert resultats[0]["embeddable"] is True


def test_rechercher_quota(monkeypatch) -> None:
    monkeypatch.setattr(
        sv,
        "get_settings",
        lambda: type("S", (), {"youtube_api_key": "k", "lichess_timeout_s": 5.0})(),
    )
    monkeypatch.setattr(
        sv.httpx2, "get", _fake_get_factory([FakeReponse({"error": "quota"}, status_code=403)])
    )
    with pytest.raises(sv.VideosUnavailable, match="quota"):
        sv.rechercher("partie italienne")


def test_rechercher_sans_cle(monkeypatch) -> None:
    monkeypatch.setattr(
        sv,
        "get_settings",
        lambda: type("S", (), {"youtube_api_key": "", "lichess_timeout_s": 5.0})(),
    )
    with pytest.raises(sv.VideosUnavailable, match="YOUTUBE_API_KEY"):
        sv.rechercher("x")


def test_noeud_videos_terme_francais(monkeypatch) -> None:
    recu = {}
    monkeypatch.setattr(
        nodes.service_videos,
        "rechercher",
        lambda terme, maxi=3: recu.update(terme=terme) or [{"video_id": "v"}],
    )
    out = nodes.videos({"opening": {"name": "Italian Game", "eco": "C50"}})
    assert recu["terme"] == "partie italienne"  # ECO → rayon → nom FR
    assert out["videos"][0]["video_id"] == "v"


def test_noeud_videos_plan_b(monkeypatch) -> None:
    def boom(terme, maxi=3):
        raise sv.VideosUnavailable("quota")

    monkeypatch.setattr(nodes.service_videos, "rechercher", boom)
    out = nodes.videos({"opening": {"name": "Italian Game", "eco": "C50"}})
    assert out["videos"] == []
    assert "vidéos indisponibles" in out["errors"][0]


def test_noeud_videos_sans_ouverture() -> None:
    assert nodes.videos({}) == {"videos": []}
