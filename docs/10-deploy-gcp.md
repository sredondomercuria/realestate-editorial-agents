# 10 · Despliegue en GCP (Cloud Run)

El proyecto corre 100% local, pero está **preparado para GCP**: contenedor para
**Cloud Run**, secretos en **Secret Manager** y cron en **Cloud Scheduler**.

## Topología en la nube

```
Cloud Scheduler ──(POST /tasks/run-daily + token)──► Cloud Run (FastAPI: dashboard + pipeline)
                                                          │   ▲
                                  Secret Manager ─────────┘   │ (modelo / Managed Agents)
                                  (ANTHROPIC_API_KEY, ...)    └──► API de Claude (Anthropic)
```

- **Cloud Run**: corre el dashboard y el pipeline (el mismo contenedor).
- **Secret Manager**: guarda las credenciales; el contenedor las carga al iniciar
  (`USE_GCP_SECRETS=true`, ver `gcp_secrets.py`).
- **Cloud Scheduler**: pega a `/tasks/run-daily` con `SCHEDULER_TOKEN` cada día.

## Requisitos

- `gcloud` autenticado (`gcloud auth login`) en el proyecto destino.
- Billing habilitado en el proyecto (ej. `supple-framing-498515-a0`).

## Paso a paso

```bash
# 0) Autenticarte y elegir proyecto
gcloud auth login
export GCP_PROJECT=supple-framing-498515-a0
export REGION=southamerica-east1            # São Paulo (cercano a AR)

# 1) Subir secretos a Secret Manager desde tu .env
bash deploy/push-secrets.sh .env

# 2) Deploy a Cloud Run (build remoto con Cloud Build; usa el Dockerfile)
bash deploy/deploy.sh

# 3) Programar la corrida diaria (08:00 hora AR)
export SCHEDULER_TOKEN="$(openssl rand -hex 16)"   # el mismo que pusiste como secreto
bash deploy/scheduler.sh
```

`deploy/deploy.sh` deja `DRY_RUN=true` por defecto: el pipeline genera y persiste,
y vos publicás desde el dashboard con **“Aprobar y publicar”**. Para publicación
totalmente automática, cambiá `DRY_RUN=false` en el deploy.

## Persistencia en Cloud Run (importante)

El filesystem de Cloud Run es **efímero**: la base SQLite y las imágenes locales no
sobreviven entre instancias. Para producción:

- **Datos**: usá **Cloud SQL (Postgres)** o **Firestore**. La capa `storage.py`
  está aislada para cambiar el backend sin tocar el resto.
- **Imágenes**: usá `IMAGE_HOST=cloudinary` (URLs públicas) o **GCS**.

Para el tutorial/demo, SQLite efímera alcanza (cada corrida se ve mientras viva la
instancia, y los posts ya quedan en el blog/redes).

## Secretos: por qué Secret Manager

No pongas API keys como env vars planas en Cloud Run. Guardalas en Secret Manager y
dejá que el servicio las lea al iniciar:

- `deploy/push-secrets.sh` crea/actualiza los secretos y le da `secretAccessor` a la
  service account de Cloud Run.
- El contenedor arranca con `USE_GCP_SECRETS=true` y `gcp_secrets.bootstrap_secrets()`
  los carga a `os.environ` antes de construir la config.

## Seguridad

- El dashboard se publica con `--allow-unauthenticated` para verlo funcionar. En
  producción, protegelo con **IAM** (quitá el acceso público y usá IAP, o un proxy
  con auth).
- `/tasks/run-daily` ya exige `SCHEDULER_TOKEN`.
- Nada de secretos en el repo ni en la imagen (ver `.dockerignore`).

## Costos

- Cloud Run escala a cero (pagás por uso). El cron diario son segundos/minutos.
- El grueso del costo es el modelo (Claude) + imágenes (Gemini) por corrida.

## Siguiente
→ [11-managed-agents.md](11-managed-agents.md)
