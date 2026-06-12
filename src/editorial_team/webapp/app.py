"""Dashboard FastAPI + HTMX: revisión y aprobación de editoriales.

Flujo human-in-the-loop:
  listar corridas → ver editorial + imagen + fact-check + crítica → editar →
  "aprobar y publicar" (o lanzar una corrida nueva).

Endpoints:
  GET  /                      panel con el historial de corridas
  GET  /runs/{id}             detalle de una corrida
  POST /runs/{id}/edit        guardar ediciones del borrador
  POST /runs/{id}/publish     publicar de verdad (blog + redes)
  POST /run                   lanzar una corrida nueva (background)
  POST /tasks/run-daily       lo invoca Cloud Scheduler (protegido por token)
  GET  /health                health check para Cloud Run (no usar /healthz: lo reserva GFE)
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .. import storage
from ..config import get_settings
from ..gcp_secrets import bootstrap_secrets
from ..publishing import md_to_html
from ..services import publish_run, run_pipeline, save_draft_edits

load_dotenv()
bootstrap_secrets()
storage.init_db()

# Carpetas para servir imágenes/artefactos locales.
for d in ("images", get_settings().output_dir):
    Path(d).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Equipo Editorial Real Estate")
app.mount("/images", StaticFiles(directory="images"), name="images")

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
TEMPLATES.env.filters["md"] = md_to_html


@app.get("/health")
def health() -> dict:
    # Nota: NO usar "/healthz": Google Front End reserva esa ruta y devuelve 404
    # antes de llegar al contenedor. "/health" sí llega a la app.
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    runs = storage.list_runs(limit=100)
    return TEMPLATES.TemplateResponse(
        request, "index.html", {"runs": runs, "settings": get_settings()}
    )


@app.get("/runs/{run_id}", response_class=HTMLResponse)
def run_detail(request: Request, run_id: int):
    run = storage.get_run(run_id)
    if not run:
        raise HTTPException(404, "Corrida no encontrada")
    return TEMPLATES.TemplateResponse(
        request, "run_detail.html", {"run": run, "settings": get_settings()}
    )


@app.post("/runs/{run_id}/edit")
def edit_run(
    run_id: int,
    title: str = Form(""),
    dek: str = Form(""),
    body_markdown: str = Form(""),
):
    save_draft_edits(run_id, title=title, dek=dek, body_markdown=body_markdown)
    return RedirectResponse(f"/runs/{run_id}", status_code=303)


@app.post("/runs/{run_id}/publish", response_class=HTMLResponse)
def publish(request: Request, run_id: int):
    pub = publish_run(run_id)
    run = storage.get_run(run_id)
    return TEMPLATES.TemplateResponse(
        request, "partials/publication.html", {"pub": pub, "run": run, "settings": get_settings()}
    )


def _kickoff() -> None:
    try:
        run_pipeline()
    except Exception as exc:  # noqa: BLE001
        print(f"[webapp] error en corrida: {exc}")


@app.post("/run")
def trigger_run(background: BackgroundTasks):
    background.add_task(_kickoff)
    return RedirectResponse("/", status_code=303)


@app.post("/tasks/run-daily")
def scheduled_run(background: BackgroundTasks, x_scheduler_token: str = Header(default="")):
    token = get_settings().scheduler_token
    if token and x_scheduler_token != token:
        raise HTTPException(401, "token inválido")
    background.add_task(_kickoff)
    return JSONResponse({"status": "accepted"}, status_code=202)


def run() -> None:
    """Entrypoint para `editorial-web` / contenedor."""
    import uvicorn

    settings = get_settings()
    port = int(os.environ.get("PORT", settings.web_port))
    uvicorn.run("editorial_team.webapp.app:app", host=settings.web_host, port=port)


if __name__ == "__main__":
    run()
