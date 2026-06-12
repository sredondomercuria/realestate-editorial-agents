#!/usr/bin/env bash
# Sube los secretos del .env local a GCP Secret Manager y le da acceso a la
# service account de Cloud Run. Corré esto ANTES del primer deploy con secretos.
set -euo pipefail

PROJECT="${GCP_PROJECT:-supple-framing-498515-a0}"
ENV_FILE="${1:-.env}"
gcloud config set project "$PROJECT"

# Secretos a publicar (deben existir en tu .env). Agregá/quitá según uses.
KEYS=(
  ANTHROPIC_API_KEY GEMINI_API_KEY OPENAI_API_KEY TAVILY_API_KEY
  WORDPRESS_URL WORDPRESS_USER WORDPRESS_APP_PASSWORD
  UPLOADPOST_API_KEY UPLOADPOST_USER CLOUDINARY_URL SCHEDULER_TOKEN
)

# Leer un valor del .env SIN sourcear (robusto ante valores con espacios).
get_env() { grep -E "^$1=" "$ENV_FILE" | head -1 | cut -d= -f2-; }

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')"
RUN_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for KEY in "${KEYS[@]}"; do
  VALUE="$(get_env "$KEY")"
  [ -z "$VALUE" ] && { echo "· $KEY vacío, salteado"; continue; }
  if gcloud secrets describe "$KEY" >/dev/null 2>&1; then
    printf '%s' "$VALUE" | gcloud secrets versions add "$KEY" --data-file=- >/dev/null
    echo "· $KEY actualizado"
  else
    printf '%s' "$VALUE" | gcloud secrets create "$KEY" --data-file=- --replication-policy=automatic >/dev/null
    echo "· $KEY creado"
  fi
  gcloud secrets add-iam-policy-binding "$KEY" \
    --member="serviceAccount:${RUN_SA}" \
    --role="roles/secretmanager.secretAccessor" >/dev/null 2>&1 || true
done

echo "✅ Secretos en Secret Manager. La SA de Cloud Run ($RUN_SA) puede leerlos."
