"""Persistencia de corridas editoriales en SQLite.

Cada corrida del pipeline se guarda como una fila con el estado final completo en
JSON, más algunas columnas indexables. Esto habilita la UI (listar / revisar /
aprobar / publicar) y un historial auditable.

SQLite es perfecto para local y para el tutorial. En Cloud Run el filesystem es
EFÍMERO: para producción usá Cloud SQL (Postgres) o Firestore — esta capa está
aislada para poder cambiar el backend sin tocar el resto (ver docs/10-deploy-gcp.md).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .config import get_settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date    TEXT NOT NULL,
    region      TEXT,
    status      TEXT NOT NULL DEFAULT 'generated',
    title       TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    state_json  TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    path = Path(get_settings().database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    return conn


def init_db() -> None:
    _connect().close()


def create_run(*, run_date: str, region: str, status: str, state: dict) -> int:
    title = (state.get("draft") or {}).get("title", "")
    now = _now()
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO runs (run_date, region, status, title, created_at, updated_at, state_json)"
            " VALUES (?,?,?,?,?,?,?)",
            (run_date, region, status, title, now, now, json.dumps(state, ensure_ascii=False, default=str)),
        )
        return cur.lastrowid


def list_runs(limit: int = 50) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, run_date, region, status, title, created_at, updated_at"
            " FROM runs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_run(run_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    if not row:
        return None
    data = dict(row)
    data["state"] = json.loads(data.pop("state_json"))
    return data


def update_state(run_id: int, state: dict) -> None:
    title = (state.get("draft") or {}).get("title", "")
    with _connect() as conn:
        conn.execute(
            "UPDATE runs SET state_json = ?, title = ?, updated_at = ? WHERE id = ?",
            (json.dumps(state, ensure_ascii=False, default=str), title, _now(), run_id),
        )


def set_status(run_id: int, status: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE runs SET status = ?, updated_at = ? WHERE id = ?", (status, _now(), run_id)
        )
