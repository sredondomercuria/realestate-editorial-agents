# 02 · Instalación y primer run

Objetivo de este capítulo: pasar de cero a **ver un editorial real en el dashboard**.

## Requisitos

- **Python 3.10 o superior** (probado en 3.12). ⚠️ Con **3.9 no funciona** (varias
  libs y `gcloud` lo requieren). ¿No tenés 3.10+? La forma más rápida sin `sudo`:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh   # instala uv
  uv python install 3.12
  ```
- **`ANTHROPIC_API_KEY`** (obligatoria) — https://console.anthropic.com/
- **`GEMINI_API_KEY`** (para las imágenes) — https://ai.studio/. Ojo: los modelos
  "Nano Banana" son **pagos**; necesitás **billing/crédito habilitado** en AI Studio
  (si no, la imagen falla con `429` y el resto del editorial igual se genera).
- (Opcional) credenciales de WordPress / upload-post para publicar de verdad.

**Costos** (orden de magnitud): cada corrida hace varias llamadas a Claude (modelo
Opus, con búsqueda web) y **una** imagen de Gemini (~US$0,13 con el modelo Pro).
Empezá con `DRY_RUN=true`: genera pero no publica.

## 1. Clonar e instalar

```bash
git clone https://github.com/sredondomercuria/realestate-editorial-agents.git
cd realestate-editorial-agents

python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
# (con uv:  uv venv --python 3.12 .venv && source .venv/bin/activate)

pip install -e .                  # núcleo (incluye Gemini, FastAPI, LangGraph...)
# pip install -e ".[integrations]"  # + Tavily y Cloudinary (opcionales)
```

> El `Makefile` usa `.venv/bin/python` si existe, así que `make web` / `make test`
> toman el venv automáticamente.

## 2. Configurar el entorno

```bash
cp .env.example .env
```

Editá `.env` y completá, como mínimo:

```
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
```

`DRY_RUN=true` y `AGENT_RUNTIME=hybrid` ya vienen por defecto.

> 🔐 `.env` está en `.gitignore`. **Nunca** lo commitees.

## 3. Verlo funcionar (lo más rápido: la UI)

```bash
make web        # levanta el dashboard en http://localhost:8080
```

Abrí http://localhost:8080 y tocá **“+ Generar editorial”**. Vas a ver:
- una fila **“generando…”** (la página se refresca sola),
- y en unos minutos el **editorial real**: texto, imagen, **fact-check** y
  **revalidación crítica**, con el botón **“Aprobar y publicar”**.

El botón corre el pipeline completo de verdad (no hay nada mockeado): Claude
investiga → valida → redacta → revalida, y Gemini ilustra.

## 4. Alternativa por CLI (lo que usa el scheduler)

```bash
make dry-run     # corre el pipeline una vez y guarda todo, sin publicar
```

Artefactos:
```
output/<fecha>/editorial.md     # el editorial en Markdown
output/<fecha>/state.json       # estado completo (temas, fact-check, crítica...)
images/<slug>.png               # imagen (si IMAGE_PROVIDER=gemini y hay crédito)
output/editorial.db             # base SQLite con el historial (la lee la UI)
```

## 5. ¿Híbrido o local? (opcional)

Por defecto `AGENT_RUNTIME=hybrid`. Para usar agentes en la plataforma de Claude:

```bash
make agent-setup      # crea el agente en Anthropic e imprime los IDs para el .env
```

Si tu cuenta **no** tiene la beta de Managed Agents, no pasa nada: el sistema
**cae a `local`** y corre igual. El log de cada corrida te dice cuál se usó. Ver
[11-managed-agents.md](11-managed-agents.md).

## 6. Tests

```bash
make test
```

## 7. Publicar de verdad (cuando estés listo)

Completá `WORDPRESS_*` y `UPLOADPOST_*` en `.env`, y publicá desde el dashboard con
**“Aprobar y publicar”** (o poné `DRY_RUN=false` para que publique solo). Empezá con
`WORDPRESS_STATUS=draft`. Ver [05-publicacion-redes.md](05-publicacion-redes.md).

## Troubleshooting

| Síntoma | Causa / solución |
|---|---|
| `make web` no levanta, `ModuleNotFoundError` | Estás usando un Python sin las deps. Activá el venv (`source .venv/bin/activate`) o instalá con `pip install -e .`. |
| `gcloud failed to load... Python 3.9` | Instalá Python 3.10+ (`uv python install 3.12`) y `export CLOUDSDK_PYTHON=$(uv python find 3.12)`. |
| Imagen no generada · `429 RESOURCE_EXHAUSTED` | La cuenta de Gemini no tiene crédito. Activá billing en https://ai.studio/. El editorial igual se genera (sin imagen). |
| Log dice `producer: fallback local` | Tu cuenta no tiene la beta de Managed Agents. Es normal; corre en modo local. |
| Tarda varios minutos | Normal: el agente investiga y revalida con búsquedas reales. La UI muestra “generando…”. |

## Estructura del proyecto

```
src/editorial_team/
  ├─ agents/             # nodos: producer (híbrido), scout, writer, critic, ...
  ├─ integrations/       # managed_agents, images (Gemini), image_host (Cloudinary),
  │                      #   search (Tavily), wordpress, upload_post
  ├─ webapp/             # dashboard FastAPI + HTMX (templates/)
  ├─ graph.py services.py storage.py publishing.py llm.py schemas.py config.py
  └─ gcp_secrets.py run_daily.py
skills/                  # 7 Claude Agent Skills
deploy/                  # scripts GCP (deploy, push-secrets, scheduler)
Dockerfile               # imagen para Cloud Run
cowork/PROMPT.md         # prompt para Claude Cowork
docs/                    # este tutorial
tests/                   # tests (sin red ni API key)
```

## Siguiente
→ [03-skills.md](03-skills.md)
