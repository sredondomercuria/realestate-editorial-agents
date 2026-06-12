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
    assert s.agent_runtime == "hybrid"
    assert s.image_provider == "gemini"
    assert s.image_model == "gemini-3-pro-image"
    assert s.social_platform_list == ["instagram", "linkedin", "facebook", "x"]


def test_markdown_to_html():
    from editorial_team.publishing import md_to_html

    html = md_to_html("# Título\n\nUn **dato** con [fuente](https://ej.com).")
    assert "Título" in html and "<strong>dato</strong>" in html
    assert 'href="https://ej.com"' in html


def test_graph_builds_hybrid():
    pytest.importorskip("langgraph")
    from editorial_team.graph import build_graph

    nodes = set(build_graph().get_graph().nodes)
    for expected in ("producer", "illustrator", "social_adapter", "publisher"):
        assert expected in nodes


def test_graph_builds_local(monkeypatch):
    pytest.importorskip("langgraph")
    from editorial_team import graph

    class S:
        agent_runtime = "local"
        max_revisions = 2

    monkeypatch.setattr(graph, "get_settings", lambda: S())
    nodes = set(graph.build_graph().get_graph().nodes)
    for expected in ("scout", "curator", "fact_checker", "writer", "critic"):
        assert expected in nodes


def test_routing_after_review(monkeypatch):
    from editorial_team import graph

    monkeypatch.setattr(graph, "get_settings", lambda: type("S", (), {"max_revisions": 2})())
    assert graph.route_after_review({"review": {"verdict": "approved"}, "revision_count": 1}) == "approve"
    assert (
        graph.route_after_review({"review": {"verdict": "needs_revision"}, "revision_count": 1})
        == "revise"
    )
    assert (
        graph.route_after_review({"review": {"verdict": "needs_revision"}, "revision_count": 2})
        == "approve"
    )
