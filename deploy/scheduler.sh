#!/usr/bin/env bash
# Crea el job de Cloud Scheduler que dispara el editorial todos los días a las 08:00
# (America/Argentina/Buenos_Aires), pegándole a /tasks/run-daily con el token.
set -euo pipefail

PROJECT="${GCP_PROJECT:-supple-framing-498515-a0}"
REGION="${REGION:-southamerica-east1}"
SERVICE="${SERVICE:-editorial-agents}"
JOB="${JOB:-editorial-daily}"
SCHED="${SCHED:-0 8 * * *}"

gcloud config set project "$PROJECT"
URL="$(gcloud run services describe "$SERVICE" --region "$REGION" --format='value(status.url)')/tasks/run-daily"

# El token debe coincidir con el secreto SCHEDULER_TOKEN del servicio.
TOKEN="${SCHEDULER_TOKEN:?Definí SCHEDULER_TOKEN en el entorno antes de correr este script}"

ARGS=(--schedule "$SCHED" --time-zone "America/Argentina/Buenos_Aires"
      --uri "$URL" --http-method POST
      --headers "X-Scheduler-Token=${TOKEN}" --location "$REGION")

if gcloud scheduler jobs describe "$JOB" --location "$REGION" >/dev/null 2>&1; then
  gcloud scheduler jobs update http "$JOB" "${ARGS[@]}"
else
  gcloud scheduler jobs create http "$JOB" "${ARGS[@]}"
fi
echo "✅ Cloud Scheduler '$JOB' → $URL ($SCHED, hora AR)"
