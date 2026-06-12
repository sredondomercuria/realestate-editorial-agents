# Atajos de desarrollo. Uso: `make <target>`
.PHONY: help install dev run dry-run test lint fmt clean

help:  ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Instala el paquete en modo editable
	python3 -m pip install -e .

dev:  ## Instala dependencias de desarrollo + imágenes
	python3 -m pip install -e ".[dev,images]"

run:  ## Ejecuta el workflow editorial completo (respeta DRY_RUN del .env)
	python3 -m editorial_team.run_daily

dry-run:  ## Fuerza modo simulación (no publica nada)
	DRY_RUN=true python3 -m editorial_team.run_daily

web:  ## Levanta el dashboard de revisión/aprobación (http://localhost:8080)
	python3 -m editorial_team.webapp.app

agent-setup:  ## Crea/encuentra el Managed Agent en la plataforma de Claude e imprime los IDs
	python3 -m editorial_team.integrations.managed_agents setup

test:  ## Corre los tests
	python3 -m pytest -q

lint:  ## Linter
	python3 -m ruff check src tests

fmt:  ## Formatea el código
	python3 -m ruff format src tests

clean:  ## Limpia artefactos
	rm -rf output images **/__pycache__ .pytest_cache .ruff_cache
