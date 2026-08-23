from types import SimpleNamespace

import pytest

from graph import synthese as syn
from graph.notation import annoter_san, libelle_fr
from services import llm

ETAT_THEORIE = {
    "fen": "x",
    "opening": {"eco": "C50", "name": "Partie italienne"},
    "in_theory": True,
    "total_games": 48726,
    "theory_moves": [{"san": "Bc5", "games": 25481}],
    "top_games": [{"white": "Caruana", "black": "Carlsen", "year": 2020}],
}


def _settings(provider: str) -> SimpleNamespace:
    return SimpleNamespace(
        llm_provider=provider,
        llm_model="qwen3.5:4b",
        llm_api_key="",
        llm_timeout_s=5.0,
        ollama_base_url="http://localhost:11434",
    )


def test_annoter_san() -> None:
    assert annoter_san("Bc5") == "Fc5 — le Fou va en c5"
    assert annoter_san("Nf6") == "Cf6 — le Cavalier va en f6"
    assert annoter_san("Qh4#") == "Dh4# — la Dame va en h4"
    assert annoter_san("e4") == "e4 — le pion va en e4"
    assert annoter_san("O-O") == "O-O — le petit roque"
    assert annoter_san("e8=Q") == "e8=Q — le pion va en e8 et devient une Dame"


def test_champ_des_possibles_se_resserre() -> None:
    # Le resserrement est calculé par le CODE, pas estimé par le LLM (déterminisme).
    moves = [{"san": "e4", "games": 60}, {"san": "d4", "games": 30}, {"san": "h4", "games": 1}]
    large = syn._champ_des_possibles(moves, 200_000)
    etroit = syn._champ_des_possibles(moves, 91)
    assert "très large" in large
    assert "sentier étroit" in etroit and "moteur" in etroit
    assert etroit.startswith("2 option(s) sérieusement jouée(s) parmi 3 coups")


def test_salutations_retirees() -> None:
    for debut in ("Salut !", "Bonjour jeune champion,", "Coucou Léa !", "Hey :"):
        assert syn._SALUTATIONS.sub("", debut + " deux options.").strip() == "deux options."


def test_libelle_fr() -> None:
    # Né de l'alerte « Bc5 illégal » : la case de départ lève l'ambiguïté visuelle.
    assert libelle_fr("Bc5", "f8c5") == "Fc5 (fou f8)"
    assert libelle_fr("Nf6", "g8f6") == "Cf6 (cavalier g8)"
    assert libelle_fr("Qh4#", "d8h4") == "Dh4# (dame d8)"
    assert libelle_fr("e4", "e2e4") == "e4 (pion e2)"
    assert libelle_fr("O-O", "e1g1") == "O-O (petit roque)"
    assert libelle_fr("O-O-O", "e8c8") == "O-O-O (grand roque)"
    assert libelle_fr("e4", "") == "e4"  # UCI absent : on n'invente pas


def test_mode_none_renvoie_le_gabarit(monkeypatch) -> None:
    monkeypatch.setattr(syn, "get_settings", lambda: _settings("none"))
    result = syn.synthese(ETAT_THEORIE)
    assert "Partie italienne" in result["answer"]
    assert result["sources"] == ["Base masters — Lichess Opening Explorer (CC0)"]


def test_mode_ollama_corps_llm_et_sources_par_construction(monkeypatch) -> None:
    monkeypatch.setattr(syn, "get_settings", lambda: _settings("ollama"))
    monkeypatch.setattr(syn.llm, "generate", lambda system, user: "Salut ! voici la théorie.")
    result = syn.synthese(ETAT_THEORIE)
    # règle 6 + garde-fou code : la salutation du LLM est retirée, ce n'est pas une discussion
    assert result["answer"].startswith("Voici la théorie.")
    # la ligne Sources est ajoutée par le code, jamais par le LLM
    assert "Sources : Base masters — Lichess Opening Explorer (CC0)" in result["answer"]


def test_faits_annotes_traduisent_la_notation(monkeypatch) -> None:
    recu = {}

    def espion(system, user):
        recu["user"] = user
        return "ok"

    monkeypatch.setattr(syn, "get_settings", lambda: _settings("ollama"))
    monkeypatch.setattr(syn.llm, "generate", espion)
    syn.synthese(ETAT_THEORIE)
    assert "Fc5 — le Fou va en c5" in recu["user"]
    assert "Bc5" not in recu["user"].replace("Fc5", "")  # la notation anglaise ne fuit pas


def test_llm_indisponible_repli_gabarit(monkeypatch) -> None:
    monkeypatch.setattr(syn, "get_settings", lambda: _settings("ollama"))

    def boom(system, user):
        raise llm.LLMUnavailable("ollama éteint")

    monkeypatch.setattr(syn.llm, "generate", boom)
    result = syn.synthese(ETAT_THEORIE)
    assert "Partie italienne" in result["answer"]  # le gabarit a pris le relais
    assert any("repli gabarit" in e for e in result["errors"])


def test_generate_fournisseur_inconnu(monkeypatch) -> None:
    monkeypatch.setattr(llm, "get_settings", lambda: _settings("hologramme"))
    with pytest.raises(llm.LLMUnavailable):
        llm.generate("s", "u")


def test_anthropic_sans_cle(monkeypatch) -> None:
    monkeypatch.setattr(llm, "get_settings", lambda: _settings("anthropic"))
    with pytest.raises(llm.LLMUnavailable, match="LLM_API_KEY"):
        llm.generate("s", "u")
