"""Publicador / Distribución (nodo del grafo).

Thin wrapper sobre `editorial_team.publishing.do_publish`, que contiene la lógica
real (reutilizada por la UI al aprobar y publicar). Respeta `DRY_RUN` de la config.
Skills: `skills/blog-publishing`, `skills/social-publishing`.
"""

from __future__ import annotations

from ..config import get_settings
from ..publishing import do_publish
from ..state import EditorialState


def publisher(state: EditorialState) -> dict:
    s = get_settings()
    pub = do_publish(
        draft=state.get("draft", {}),
        images=state.get("images", []),
        social=state.get("social", []),
        dry_run=s.dry_run,
    )
    if s.dry_run:
        return {"publication": pub, "log": ["publisher: DRY_RUN activo, no se publicó nada"]}

    blog_ok = (pub.get("blog") or {}).get("status") == "published"
    return {
        "publication": pub,
        "log": [f"publisher: blog={'ok' if blog_ok else 'fallo'}, redes={len(pub['social'])}"],
    }
