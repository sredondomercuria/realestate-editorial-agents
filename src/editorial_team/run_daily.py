"""Punto de entrada del workflow editorial diario.

Corre el pipeline (híbrido o local), persiste la corrida en SQLite y guarda los
artefactos en `OUTPUT_DIR/<fecha>/`. Es el script que invoca el scheduler (cron /
GitHub Actions / Cloud Scheduler / Cowork).

Uso:
    python -m editorial_team.run_daily
    editorial-daily            # si instalaste el paquete (pip install -e .)
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from .config import get_settings
from .gcp_secrets import bootstrap_secrets
from .services import run_pipeline


def _save_artifacts(state: dict, run_date: str) -> Path:
    out_dir = Path(get_settings().output_dir) / run_date
    out_dir.mkdir(parents=True, exist_ok=True)

    draft = state.get("draft", {})
    if draft:
        md = f"# {draft.get('title', '')}\n\n_{draft.get('dek', '')}_\n\n{draft.get('body_markdown', '')}"
        (out_dir / "editorial.md").write_text(md, encoding="utf-8")

    (out_dir / "state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    return out_dir


def _print_summary(state: dict, run_id: int, out_dir: Path) -> None:
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
    print(f"  Runtime    : {settings.agent_runtime}")
    print(f"  Título     : {draft.get('title', '(sin borrador)')}")
    print(f"  Crítica    : verdict={review.get('verdict')} score={review.get('score')}")
    print(f"  DRY_RUN    : {settings.dry_run}")
    if pub:
        blog = pub.get("blog") or {}
        print(f"  Blog       : {blog.get('status')} {blog.get('link', '')}")
        for s in pub.get("social", []):
            print(f"  Red        : {s.get('platform')} -> {s.get('status')}")
    print(f"\n  Run #{run_id} guardado en la base ({settings.database_path})")
    print(f"  Artefactos en: {out_dir}/")
    print("=" * 70 + "\n")


def main() -> int:
    load_dotenv()
    bootstrap_secrets()
    settings = get_settings()

    if not (settings.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")):
        print("ERROR: falta ANTHROPIC_API_KEY (configurá tu .env). Ver .env.example.")
        return 1

    run_date = date.today().isoformat()
    print(f"▶ Equipo editorial [{settings.agent_runtime}] para {run_date} ({settings.region_focus})...")

    result = run_pipeline(settings.region_focus, run_date=run_date)
    out_dir = _save_artifacts(result["state"], run_date)
    _print_summary(result["state"], result["run_id"], out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
