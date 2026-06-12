"""Tests de la capa de persistencia (SQLite en un archivo temporal)."""

from __future__ import annotations


def test_storage_roundtrip(tmp_path, monkeypatch):
    from editorial_team import storage

    db = tmp_path / "test.db"

    class S:
        database_path = str(db)

    monkeypatch.setattr(storage, "get_settings", lambda: S())

    storage.init_db()
    state = {"draft": {"title": "Mercado en alza"}, "log": ["x"]}
    run_id = storage.create_run(run_date="2026-06-12", region="AR", status="generated", state=state)

    assert run_id == 1
    runs = storage.list_runs()
    assert runs[0]["title"] == "Mercado en alza"
    assert runs[0]["status"] == "generated"

    full = storage.get_run(run_id)
    assert full["state"]["draft"]["title"] == "Mercado en alza"

    state["draft"]["title"] = "Editado"
    storage.update_state(run_id, state)
    storage.set_status(run_id, "published")

    full = storage.get_run(run_id)
    assert full["title"] == "Editado"
    assert full["status"] == "published"
