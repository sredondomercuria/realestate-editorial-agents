#!/usr/bin/env bash
# Despliega el dashboard a Cloud Run desde el código fuente (usa el Dockerfile).
# Requisitos: gcloud autenticado (gcloud auth login) y APIs habilitadas (las habilita abajo).
set -euo pipefail

PROJECT="${GCP_PROJECT:-supple-framing-498515-a0}"
REGION="${REGION:-southamerica-east1}"          # São Paulo (cercano a AR)
SERVICE="${SERVICE:-editorial-agents}"

echo "▶ Proyecto: $PROJECT · Región: $REGION · Servicio: $SERVICE"
gcloud config set project "$PROJECT"

echo "▶ Habilitando APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudscheduler.googleapis.com

echo "▶ Deploy a Cloud Run (build remoto con Cloud Build)..."
gcloud run deploy "$SERVICE" \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 1Gi --cpu 1 --timeout 900 \
  --set-env-vars "USE_GCP_SECRETS=true,GCP_PROJECT=${PROJECT},AGENT_RUNTIME=hybrid,DRY_RUN=true,IMAGE_PROVIDER=gemini,RESEARCH_BACKEND=claude"

echo "✅ Listo. URL:"
gcloud run services describe "$SERVICE" --region "$REGION" --format="value(status.url)"
echo
echo "Recordá: el dashboard queda público (--allow-unauthenticated). Para producción"
echo "protegelo con IAM/IAP. El endpoint /tasks/run-daily ya exige SCHEDULER_TOKEN."
