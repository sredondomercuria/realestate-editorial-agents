# Atajos de desarrollo. Uso: `make <target>`
# Usa el venv .venv si existe; si no, python3 del sistema.
PY := $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)

.PHONY: help install dev run dry-run web agent-setup test lint fmt clean

help:  ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Instala el paquete en modo editable
	$(PY) -m pip install -e .

dev:  ## Instala dependencias de desarrollo + integraciones (Tavily, Cloudinary)
	$(PY) -m pip install -e ".[dev,integrations]"

run:  ## Ejecuta el workflow editorial completo (respeta DRY_RUN del .env)
	$(PY) -m editorial_team.run_daily

dry-run:  ## Fuerza modo simulación (no publica nada)
	DRY_RUN=true $(PY) -m editorial_team.run_daily

web:  ## Levanta el dashboard de revisión/aprobación (http://localhost:8080)
	$(PY) -m editorial_team.webapp.app

agent-setup:  ## Crea/encuentra el Managed Agent en la plataforma de Claude e imprime los IDs
	$(PY) -m editorial_team.integrations.managed_agents setup

test:  ## Corre los tests
	$(PY) -m pytest -q

lint:  ## Linter
	$(PY) -m ruff check src tests

fmt:  ## Formatea el código
	$(PY) -m ruff format src tests

clean:  ## Limpia artefactos
	rm -rf output images **/__pycache__ .pytest_cache .ruff_cache
