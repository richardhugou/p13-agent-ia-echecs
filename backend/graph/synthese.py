"""Nœud de synthèse — met les faits en mots pour l'élève.

Deux modes : gabarit déterministe (toujours disponible, zéro coût) ; LLM (à venir,
activé par LLM_API_KEY). Règle intangible : la synthèse ne choisit JAMAIS un coup —
elle rédige à partir des faits présents dans l'état, rien d'autre.
"""

from graph.state import AgentState


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


def synthese(state: AgentState) -> dict:
    """Point d'entrée du nœud — le mode LLM (Haiku) se branchera ici (commit 4)."""
    return synthese_gabarit(state)
