"""Smoke tests: configuración, conversión Markdown y armado del grafo.

No hacen llamadas a la API ni a la red.
"""

from __future__ import annotations

import pytest


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("DRY_RUN", raising=False)
    from editorial_team.config import Settings

    s = Settings(_env_file=None)
    assert s.dry_run is True  # seguro por defecto
    assert s.model_writer == "claude-opus-4-8"
    assert s.social_platform_list == ["instagram", "linkedin", "facebook", "x"]


def test_markdown_to_html():
    from editorial_team.agents.publisher import md_to_html

    html = md_to_html(
        "# Título\n\nUn **dato** importante con [fuente](https://ej.com).\n\n- uno\n- dos"
    )
    assert "<h1>Título</h1>" in html
    assert "<strong>dato</strong>" in html
    assert '<a href="https://ej.com">fuente</a>' in html
    assert "<ul>" in html and "<li>uno</li>" in html


def test_graph_builds():
    pytest.importorskip("langgraph")
    from editorial_team.graph import build_graph

    app = build_graph()
    # El grafo compila y expone los nodos esperados.
    nodes = set(app.get_graph().nodes)
    for expected in (
        "scout",
        "curator",
        "fact_checker",
        "writer",
        "critic",
        "illustrator",
        "social_adapter",
        "publisher",
    ):
        assert expected in nodes


def test_routing_after_review(monkeypatch):
    from editorial_team import graph

    monkeypatch.setattr(graph, "get_settings", lambda: type("S", (), {"max_revisions": 2})())
    assert graph.route_after_review({"review": {"verdict": "approved"}, "revision_count": 1}) == "approve"
    assert (
        graph.route_after_review({"review": {"verdict": "needs_revision"}, "revision_count": 1})
        == "revise"
    )
    # Se agotaron las revisiones -> aprueba igual para no quedar en bucle.
    assert (
        graph.route_after_review({"review": {"verdict": "needs_revision"}, "revision_count": 2})
        == "approve"
    )
