"""Punto de entrada del workflow editorial diario.

Ejecuta el grafo completo y guarda los artefactos (editorial en Markdown, estado
JSON y resultados de publicación) en `OUTPUT_DIR/<fecha>/`. Este es el script que
invoca el scheduler (cron / GitHub Actions / Cowork).

Uso:
    python -m editorial_team.run_daily
    editorial-daily            # si instalaste el paquete (pip install -e .)
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from .config import get_settings
from .graph import build_graph


def _save_artifacts(state: dict, run_date: str) -> Path:
    settings = get_settings()
    out_dir = Path(settings.output_dir) / run_date
    out_dir.mkdir(parents=True, exist_ok=True)

    draft = state.get("draft", {})
    if draft:
        md = f"# {draft.get('title', '')}\n\n_{draft.get('dek', '')}_\n\n{draft.get('body_markdown', '')}"
        (out_dir / "editorial.md").write_text(md, encoding="utf-8")

    (out_dir / "state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    return out_dir


def _print_summary(state: dict, out_dir: Path) -> None:
    settings = get_settings()
    draft = state.get("draft", {})
    review = state.get("review", {})
    pub = state.get("publication", {})

    print("\n" + "=" * 70)
    print(" RESUMEN DE LA EJECUCIÓN EDITORIAL")
    print("=" * 70)
    for line in state.get("log", []):
        print(f"  · {line}")
    print("-" * 70)
    print(f"  Título     : {draft.get('title', '(sin borrador)')}")
    print(f"  Crítica    : verdict={review.get('verdict')} score={review.get('score')}")
    print(f"  Iteraciones: {state.get('revision_count', 0)}")
    print(f"  DRY_RUN    : {settings.dry_run}")
    if pub:
        blog = pub.get("blog") or {}
        print(f"  Blog       : {blog.get('status')} {blog.get('link', '')}")
        for s in pub.get("social", []):
            print(f"  Red        : {s.get('platform')} -> {s.get('status')}")
        if pub.get("errors"):
            print(f"  Errores    : {pub['errors']}")
    print(f"\n  Artefactos guardados en: {out_dir}/")
    print("=" * 70 + "\n")


def main() -> int:
    load_dotenv()
    settings = get_settings()

    if not (settings.anthropic_api_key or _env_has_anthropic_key()):
        print("ERROR: falta ANTHROPIC_API_KEY (configurá tu .env). Ver .env.example.")
        return 1

    run_date = date.today().isoformat()
    print(f"▶ Ejecutando equipo editorial para {run_date} ({settings.region_focus})...")

    app = build_graph()
    initial = {
        "run_date": run_date,
        "region": settings.region_focus,
        "revision_count": 0,
        "log": [],
    }
    final_state = app.invoke(initial, config={"recursion_limit": 50})

    out_dir = _save_artifacts(final_state, run_date)
    _print_summary(final_state, out_dir)
    return 0


def _env_has_anthropic_key() -> bool:
    import os

    return bool(os.environ.get("ANTHROPIC_API_KEY"))


if __name__ == "__main__":
    sys.exit(main())
