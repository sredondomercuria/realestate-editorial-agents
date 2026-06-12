"""Servicios de orquestación de alto nivel.

Pegamento entre el grafo, la persistencia y la publicación. Lo usan el entrypoint
diario (`run_daily`) y la UI (`webapp`).
"""

from __future__ import annotations

from datetime import date

from . import storage
from .config import get_settings
from .graph import build_graph
from .publishing import do_publish


def run_pipeline(region: str | None = None, *, run_date: str | None = None) -> dict:
    """Corre el pipeline editorial completo y persiste la corrida. Devuelve {run_id, state}."""
    settings = get_settings()
    region = region or settings.region_focus
    run_date = run_date or date.today().isoformat()

    app = build_graph()
    initial = {"run_date": run_date, "region": region, "revision_count": 0, "log": []}
    state = app.invoke(initial, config={"recursion_limit": 50})

    # Estado de la corrida según si ya se publicó (DRY_RUN) o quedó para revisar.
    published = bool((state.get("publication") or {}).get("blog", {}) and
                     (state["publication"]["blog"] or {}).get("status") == "published")
    status = "published" if published else "generated"
    run_id = storage.create_run(run_date=run_date, region=region, status=status, state=state)
    return {"run_id": run_id, "state": state}


def publish_run(run_id: int) -> dict:
    """Publica de verdad (dry_run=False) una corrida ya guardada. Lo invoca la UI."""
    run = storage.get_run(run_id)
    if not run:
        raise ValueError(f"run {run_id} no existe")

    state = run["state"]
    draft = state.get("draft", {})
    images = state.get("images", [])
    social = state.get("social", [])

    pub = do_publish(draft=draft, images=images, social=social, dry_run=False)
    state["publication"] = pub
    storage.update_state(run_id, state)

    blog_ok = (pub.get("blog") or {}).get("status") == "published"
    social_ok = any(s.get("status") == "published" for s in pub.get("social", []))
    storage.set_status(run_id, "published" if (blog_ok or social_ok) else "failed")
    return pub


def save_draft_edits(run_id: int, *, title: str, dek: str, body_markdown: str) -> None:
    """Guarda ediciones humanas del borrador antes de publicar."""
    run = storage.get_run(run_id)
    if not run:
        raise ValueError(f"run {run_id} no existe")
    state = run["state"]
    draft = state.setdefault("draft", {})
    draft["title"] = title
    draft["dek"] = dek
    draft["body_markdown"] = body_markdown
    storage.update_state(run_id, state)
