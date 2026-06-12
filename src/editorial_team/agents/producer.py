"""Productor editorial (runtime híbrido).

Delega la producción autónoma (investigar → validar → redactar → revalidar) a un
**Managed Agent** en la plataforma de Claude. Si no está disponible, cae al
sub-pipeline **local** (los nodos scout→curator→fact_checker→writer→critic).

Devuelve las mismas claves que el camino local (`selected`, `factcheck`, `draft`,
`review`) para que el resto del grafo (ilustrador → redes → publicación) no cambie.
"""

from __future__ import annotations

from ..config import get_settings
from ..integrations.managed_agents import run_editorial_team
from ..state import EditorialState


def produce(state: EditorialState) -> dict:
    s = get_settings()
    region = state.get("region", s.region_focus)
    run_date = state.get("run_date", "")

    result = run_editorial_team(region=region, run_date=run_date)
    if result and result.get("draft"):
        return {
            "selected": result.get("selected", []),
            "factcheck": result.get("factcheck", {}),
            "draft": result.get("draft", {}),
            "review": result.get("review", {}),
            "revision_count": 1,
            "log": ["producer: editorial producido por Managed Agent (plataforma Claude)"],
        }
    return _produce_local(state)


def _produce_local(state: EditorialState) -> dict:
    """Fallback: corre el sub-pipeline local (mismos agentes, en este backend)."""
    from .critic import critic
    from .curator import curator
    from .fact_checker import fact_checker
    from .scout import scout
    from .writer import writer

    s = get_settings()
    work: dict = dict(state)
    logs: list[str] = []

    for node in (scout, curator, fact_checker):
        out = node(work)
        logs += out.pop("log", [])
        work.update(out)

    work["revision_count"] = 0
    while True:
        for node in (writer, critic):
            out = node(work)
            logs += out.pop("log", [])
            work.update(out)
        review = work.get("review", {})
        if review.get("verdict") == "needs_revision" and work.get("revision_count", 0) < s.max_revisions:
            continue
        break

    return {
        "selected": work.get("selected", []),
        "factcheck": work.get("factcheck", {}),
        "draft": work.get("draft", {}),
        "review": work.get("review", {}),
        "revision_count": work.get("revision_count", 1),
        "log": logs + ["producer: fallback local (Managed Agents no disponible)"],
    }
