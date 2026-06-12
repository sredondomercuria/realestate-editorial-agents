"""Carga de secretos desde GCP Secret Manager.

En local usás `.env`. En GCP (Cloud Run) lo recomendado es no pasar secretos como
variables de entorno planas sino guardarlos en **Secret Manager**. Si
`USE_GCP_SECRETS=true`, esta función carga los secretos a `os.environ` ANTES de
construir la configuración, para que `Settings` los tome de forma transparente.

Convención: el nombre del secreto en Secret Manager == el nombre de la variable de
entorno (ej. secreto `ANTHROPIC_API_KEY`).

Llamar `bootstrap_secrets()` al arrancar (run_daily / webapp), antes de get_settings().
"""

from __future__ import annotations

import os

# Secretos que intentamos cargar desde Secret Manager (si existen).
SECRET_KEYS = [
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "TAVILY_API_KEY",
    "WORDPRESS_URL",
    "WORDPRESS_USER",
    "WORDPRESS_APP_PASSWORD",
    "UPLOADPOST_API_KEY",
    "UPLOADPOST_USER",
    "CLOUDINARY_URL",
    "SCHEDULER_TOKEN",
]


def bootstrap_secrets() -> None:
    if os.environ.get("USE_GCP_SECRETS", "").lower() not in ("1", "true", "yes"):
        return
    project = os.environ.get("GCP_PROJECT", "")
    if not project:
        print("[secrets] USE_GCP_SECRETS=true pero falta GCP_PROJECT.")
        return

    try:
        from google.cloud import secretmanager
    except ImportError:
        print("[secrets] falta `google-cloud-secret-manager`; `pip install` el extra gcp.")
        return

    client = secretmanager.SecretManagerServiceClient()
    loaded = []
    for key in SECRET_KEYS:
        name = f"projects/{project}/secrets/{key}/versions/latest"
        try:
            resp = client.access_secret_version(name=name)
            os.environ[key] = resp.payload.data.decode("utf-8")
            loaded.append(key)
        except Exception:  # noqa: BLE001 — secreto inexistente o sin permiso: se ignora
            continue
    if loaded:
        print(f"[secrets] cargados desde Secret Manager: {', '.join(loaded)}")
