# Imagen para Cloud Run: sirve el dashboard FastAPI (que también expone
# /tasks/run-daily para Cloud Scheduler). Instalación editable para que el agente
# pueda leer las skills desde /app/skills.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

COPY pyproject.toml requirements.txt README.md ./
COPY src ./src
COPY skills ./skills

RUN pip install -e ".[integrations,gcp]"

EXPOSE 8080

# Cloud Run inyecta PORT; webapp.app:run() lo respeta.
CMD ["python", "-m", "editorial_team.webapp.app"]
