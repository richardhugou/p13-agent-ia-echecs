"""Câblage du graphe — la structure définitive, stubs compris (D-a)."""

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from graph import nodes
from graph.state import AgentState
from graph.synthese import synthese


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("valider_fen", nodes.valider_fen)
    builder.add_node("identifier_ouverture", nodes.identifier_ouverture)
    builder.add_node("coups_theoriques", nodes.coups_theoriques)
    builder.add_node("evaluer_position", nodes.evaluer_position)
    builder.add_node("contexte_rag", nodes.contexte_rag)
    builder.add_node("videos", nodes.videos)
    builder.add_node("synthese", synthese)

    builder.add_edge(START, "valider_fen")
    builder.add_conditional_edges(
        "valider_fen",
        nodes.apres_validation,
        {"stop": END, "continue": "identifier_ouverture"},
    )
    builder.add_conditional_edges(
        "identifier_ouverture",
        nodes.route_theorie_ou_moteur,
        {"theorie": "coups_theoriques", "moteur": "evaluer_position"},
    )
    builder.add_edge("coups_theoriques", "contexte_rag")
    builder.add_edge("evaluer_position", "contexte_rag")
    builder.add_edge("contexte_rag", "videos")
    builder.add_edge("videos", "synthese")
    builder.add_edge("synthese", END)
    return builder.compile()


@lru_cache
def get_graph():
    return build_graph()
