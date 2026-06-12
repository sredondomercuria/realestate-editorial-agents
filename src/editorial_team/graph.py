"""Definición del grafo LangGraph del equipo editorial.

Flujo:

    START → scout → curator → fact_checker → writer → critic ─┐
                                                ▲              │ (needs_revision
                                                └──────────────┘  y quedan revisiones)
                                                               │ (approved / sin revisiones)
                                                               ▼
                          illustrator → social_adapter → publisher → END

El borde condicional después de `critic` implementa el bucle de revalidación
crítica: si el editor pide cambios y no se agotaron las revisiones, vuelve al
redactor; si no, sigue a producción.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .agents import (
    critic,
    curator,
    fact_checker,
    illustrator,
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
    """Construye y compila el grafo. Devuelve una app invocable."""
    g = StateGraph(EditorialState)

    g.add_node("scout", scout)
    g.add_node("curator", curator)
    g.add_node("fact_checker", fact_checker)
    g.add_node("writer", writer)
    g.add_node("critic", critic)
    g.add_node("illustrator", illustrator)
    g.add_node("social_adapter", social_adapter)
    g.add_node("publisher", publisher)

    g.add_edge(START, "scout")
    g.add_edge("scout", "curator")
    g.add_edge("curator", "fact_checker")
    g.add_edge("fact_checker", "writer")
    g.add_edge("writer", "critic")
    g.add_conditional_edges(
        "critic",
        route_after_review,
        {"revise": "writer", "approve": "illustrator"},
    )
    g.add_edge("illustrator", "social_adapter")
    g.add_edge("social_adapter", "publisher")
    g.add_edge("publisher", END)

    return g.compile()
