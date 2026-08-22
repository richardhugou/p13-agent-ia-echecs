"""Nœud de synthèse — met les faits en mots pour l'élève.

Trois modes (LLM_PROVIDER) : none = gabarit déterministe seul ; ollama (défaut POC,
qwen3.5:4b local) ; anthropic (option qualité). Le LLM rédige le corps de la réponse,
la ligne Sources est ajoutée par le code — garantie par construction, pas par prompt
(les mesures ont montré que les petits modèles la perdent). Règle intangible : la
synthèse ne choisit JAMAIS un coup — elle rédige à partir des faits de l'état.
"""

import json

from config import get_settings
from graph.notation import annoter_san
from graph.state import AgentState
from services import llm

PROMPT_COACH = """Tu es un coach d'échecs pour de jeunes joueurs (10 à 14 ans).
On te donne des FAITS vérifiés sur une position. Règles absolues :
1. Ne recommande JAMAIS un coup absent des faits fournis. N'invente ni coup, ni chiffre.
2. N'ajoute AUCUNE explication stratégique de ton cru : présente les faits, rien de plus.
3. Si les faits sont vides ou insuffisants, dis honnêtement que tu ne peux pas répondre.
4. Rédige 3 à 5 phrases en français simple, tutoie l'élève, reste encourageant.
5. N'écris PAS de ligne « Sources » : elle est ajoutée automatiquement après toi."""


def _eval_en_mots(engine_eval: dict) -> str:
    mate = engine_eval.get("mate")
    if mate is not None:
        camp = "les Blancs" if mate > 0 else "les Noirs"
        return f"Mat en {abs(mate)} pour {camp}."
    cp = engine_eval.get("cp") or 0
    pions = cp / 100
    if abs(pions) < 0.3:
        verdict = "position équilibrée"
    else:
        camp = "les Blancs" if pions > 0 else "les Noirs"
        verdict = f"environ {abs(pions):.1f} pion(s) d'avance pour {camp}"
    ligne = " ".join(engine_eval.get("best_line", [])[:4])
    texte = f"Évaluation Stockfish : {pions:+.2f} — {verdict}."
    if ligne:
        texte += f" Meilleure suite : {ligne}."
    return texte


def synthese_gabarit(state: AgentState) -> dict:
    """Assemble une réponse lisible à partir des blocs factuels de l'état."""
    parts: list[str] = []
    sources: list[str] = []

    opening = state.get("opening")
    if opening:
        parts.append(f"Position : {opening.get('name')} ({opening.get('eco')}).")

    if state.get("in_theory"):
        moves = state.get("theory_moves") or []
        if moves:
            liste = ", ".join(f"{m['san']} ({m['games']} parties)" for m in moves[:3])
            parts.append(
                f"La théorie ({state.get('total_games', 0)} parties de maîtres) "
                f"recommande : {liste}."
            )
            sources.append("Base masters — Lichess Opening Explorer (CC0)")
        top_games = state.get("top_games") or []
        if top_games:
            game = top_games[0]
            parts.append(
                f"Partie de référence : {game.get('white')} – {game.get('black')} "
                f"({game.get('year')})."
            )
    else:
        parts.append(
            "Cette position sort de la théorie "
            f"({state.get('total_games', 0)} partie(s) de maîtres connue(s))."
        )
        engine_eval = state.get("engine_eval")
        if engine_eval:
            parts.append(_eval_en_mots(engine_eval))
            sources.append(f"Stockfish (profondeur {engine_eval.get('depth')})")

    errors = state.get("errors") or []
    if errors:
        parts.append("Note : certaines sources étaient indisponibles (" + " ; ".join(errors) + ").")

    if not parts:
        parts.append("Je n'ai trouvé aucune information exploitable pour cette position.")

    return {"answer": " ".join(parts), "sources": sources}


def _faits_annotes(state: AgentState) -> str:
    """Les faits préparés pour le LLM — coups annotés, évaluation pré-verbalisée."""
    faits: dict = {}
    trait = "aux Blancs" if " w " in state.get("fen", "") else "aux Noirs"
    faits["au_trait"] = f"C'est {trait} de jouer."
    if state.get("opening"):
        faits["ouverture"] = state["opening"]
    faits["position_en_theorie"] = bool(state.get("in_theory"))
    faits["parties_de_maitres_connues"] = state.get("total_games", 0)
    moves = state.get("theory_moves") or []
    if moves:
        faits["coups_recommandes_par_la_theorie"] = [
            {"coup": annoter_san(m["san"]), "parties": m["games"]} for m in moves[:3]
        ]
    top_games = state.get("top_games") or []
    if top_games:
        faits["partie_de_reference"] = top_games[0]
    if state.get("engine_eval"):
        engine_eval = state["engine_eval"]
        faits["evaluation_du_moteur"] = _eval_en_mots(engine_eval)
        if engine_eval.get("best_line"):
            faits["meilleure_suite_detaillee"] = [
                annoter_san(coup) for coup in engine_eval["best_line"][:3]
            ]
    if state.get("errors"):
        faits["sources_indisponibles"] = state["errors"]
    if state.get("question"):
        faits["question_de_l_eleve"] = state["question"]
    return "FAITS :\n" + json.dumps(faits, ensure_ascii=False)


def synthese(state: AgentState) -> dict:
    """Gabarit d'abord (toujours juste), LLM ensuite s'il est disponible — sinon repli."""
    gabarit = synthese_gabarit(state)
    settings = get_settings()
    if settings.llm_provider == "none":
        return gabarit

    try:
        corps = llm.generate(PROMPT_COACH, _faits_annotes(state)).strip()
    except llm.LLMUnavailable as exc:
        return {
            **gabarit,
            "errors": (state.get("errors") or []) + [f"LLM indisponible, repli gabarit : {exc}"],
        }

    answer = corps
    if gabarit["sources"]:
        answer += "\n\nSources : " + " · ".join(gabarit["sources"])
    return {"answer": answer, "sources": gabarit["sources"]}
