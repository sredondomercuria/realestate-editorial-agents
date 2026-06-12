# 02 · Instalación y primer run

## Requisitos
- **Python 3.10+** (recomendado 3.11).
- Una **API key de Claude** (https://console.anthropic.com/).
- (Opcional) credenciales de WordPress y upload-post para publicar de verdad.
- (Opcional) `OPENAI_API_KEY` si querés generar imágenes con `gpt-image-1`.

## 1. Clonar e instalar

```bash
git clone https://github.com/sredondomercuria/realestate-editorial-agents.git
cd realestate-editorial-agents

python3 -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate

pip install -e ".[images]"       # o:  pip install -r requirements.txt
```

## 2. Configurar el entorno

```bash
cp .env.example .env
```

Editá `.env` y completá al menos `ANTHROPIC_API_KEY`. Dejá `DRY_RUN=true` para la
primera prueba (genera todo pero **no publica**).

> 🔐 `.env` está en `.gitignore`. **Nunca** lo commitees. En el repo público sólo
> vive `.env.example` con placeholders.

## 3. Primer run (modo seguro)

```bash
make dry-run        # equivalente a: DRY_RUN=true python -m editorial_team.run_daily
```

Vas a ver el log de cada agente y, al final, un resumen. Los artefactos quedan en:

```
output/<fecha>/editorial.md     # el editorial en Markdown
output/<fecha>/state.json       # estado completo (temas, fact-check, crítica, etc.)
images/<slug>.png               # imagen (si IMAGE_PROVIDER=openai)
```

## 4. Correr los tests

```bash
make test
```

## 5. Publicar de verdad (cuando estés listo)

Completá en `.env` las credenciales de WordPress y/o upload-post y poné
`DRY_RUN=false`. Empezá con `WORDPRESS_STATUS=draft` para revisar el post antes de
que salga en vivo. Ver [05-publicacion-redes.md](05-publicacion-redes.md).

## Estructura del proyecto

```
realestate-editorial-agents/
├── src/editorial_team/
│   ├── config.py          # configuración (lee .env)
│   ├── state.py           # estado del grafo
│   ├── schemas.py         # JSON Schemas (structured outputs)
│   ├── llm.py             # acceso a Claude (json + research)
│   ├── graph.py           # ensamblado del grafo LangGraph
│   ├── run_daily.py       # entrypoint diario
│   ├── agents/            # un archivo por agente
│   └── integrations/      # imágenes, WordPress, upload-post
├── skills/                # una Agent Skill por funcionalidad
├── cowork/PROMPT.md       # prompt para Claude Cowork
├── scheduling/            # cron / launchd
├── .github/workflows/     # GitHub Actions (run diario)
└── docs/                  # este tutorial
```

## Siguiente
→ [03-skills.md](03-skills.md)
