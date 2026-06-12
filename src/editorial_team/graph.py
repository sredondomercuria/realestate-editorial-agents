"""Definición del grafo LangGraph del equipo editorial.

Dos runtimes (config `AGENT_RUNTIME`):

HÍBRIDO (default) — la producción autónoma corre como Managed Agent en la plataforma
de Claude; LangGraph orquesta el resto:

    START → producer (Managed Agent) → illustrator → social_adapter → publisher → END

LOCAL — todo el pipeline corre como nodos LangGraph en este backend, con el bucle de
revalidación crítica writer ⇄ critic:

    START → scout → curator → fact_checker → writer → critic ─┐
                                               ▲              │ needs_revision
                                               └──────────────┘
                                                              │ approved
                                              illustrator → social_adapter → publisher → END
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .agents import (
    critic,
    curator,
    fact_checker,
    illustrator,
    produce,
    publisher,
    scout,
    social_adapter,
    writer,
)
from .config import get_settings
from .state import EditorialState


def route_after_review(state: EditorialState) -> str:
    review = state.get("review") or {}
    revisions = state.get("revision_count", 0)
    if review.get("verdict") == "needs_revision" and revisions < get_settings().max_revisions:
        return "revise"
    return "approve"


def build_graph():
    """Construye y compila el grafo según AGENT_RUNTIME. Devuelve una app invocable."""
    settings = get_settings()
    g = StateGraph(EditorialState)

    # Etapa de producción común a producción (distribución) ----------------
    g.add_node("illustrator", illustrator)
    g.add_node("social_adapter", social_adapter)
    g.add_node("publisher", publisher)

    if settings.agent_runtime == "hybrid":
        g.add_node("producer", produce)
        g.add_edge(START, "producer")
        g.add_edge("producer", "illustrator")
    else:  # local
        g.add_node("scout", scout)
        g.add_node("curator", curator)
        g.add_node("fact_checker", fact_checker)
        g.add_node("writer", writer)
        g.add_node("critic", critic)
        g.add_edge(START, "scout")
        g.add_edge("scout", "curator")
        g.add_edge("curator", "fact_checker")
        g.add_edge("fact_checker", "writer")
        g.add_edge("writer", "critic")
        g.add_conditional_edges(
            "critic", route_after_review, {"revise": "writer", "approve": "illustrator"}
        )

    g.add_edge("illustrator", "social_adapter")
    g.add_edge("social_adapter", "publisher")
    g.add_edge("publisher", END)

    return g.compile()
