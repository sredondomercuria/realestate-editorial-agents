# 🏠 realestate-editorial-agents

**Tutorial completo: construí tu propio sistema multiagente con la plataforma
Claude + LangGraph.**

Un **equipo editorial autónomo** que, todos los días, busca noticias de **Real
Estate de Argentina y Latinoamérica**, **valida los datos** con fuentes
independientes, redacta un **editorial profesional**, lo somete a una
**revalidación crítica**, genera **imágenes** que acompañan cada post y lo
**publica en un blog y en todas las redes sociales** — coordinado por un grafo de
agentes especializados.

> Este repo es a la vez un **tutorial paso a paso** (`docs/`) y un **proyecto
> funcional** que podés correr y adaptar.

---

## ✨ Qué vas a aprender

- Diseñar un **equipo de agentes** con **LangGraph** (estado compartido, bucles,
  ramas condicionales).
- Usar **Claude** (`claude-opus-4-8` / `claude-sonnet-4-6`) con el SDK oficial:
  *structured outputs*, razonamiento adaptativo y **herramientas web server-side**
  (`web_search` / `web_fetch`) para investigar con citas.
- Encapsular cada función como **Claude Agent Skill** reutilizable.
- Implementar **validación de datos** y **revalidación crítica adversarial**.
- **Publicar** en WordPress (REST API) y en redes con **upload-post**, con
  imágenes generadas.
- **Programar** la ejecución diaria (cron / GitHub Actions / Cowork).
- Hacerlo todo **bajo mejores prácticas** (seguridad, costos, observabilidad).

## 🧠 El equipo (agentes)

```
START → 🔎 Scout → 🗂️ Curador → ✅ Fact-checker → ✍️ Redactor → 🧐 Crítico ─┐
                                                       ▲                      │ needs_revision
                                                       └──────────────────────┘
                                                                              │ approved
                                                                              ▼
                          🎨 Ilustrador → 📱 Adaptador de redes → 🚀 Publicador → END
```

Cada agente tiene **una responsabilidad** y una **skill** asociada. El bucle
`Redactor ⇄ Crítico` implementa la revalidación crítica que evita publicar datos
flojos. → Diagrama y detalle en [docs/01-arquitectura.md](docs/01-arquitectura.md).

## 🚀 Quickstart

```bash
# 1) Instalar
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[images]"

# 2) Configurar (al menos ANTHROPIC_API_KEY). DRY_RUN=true => no publica.
cp .env.example .env
$EDITOR .env

# 3) Primer run en modo seguro (genera todo, no publica)
make dry-run

# 4) Ver el resultado
cat output/$(date +%F)/editorial.md
```

Cuando estés listo para publicar de verdad: completá las credenciales de WordPress
/ upload-post en `.env`, poné `DRY_RUN=false` (empezá con `WORDPRESS_STATUS=draft`)
y programá la ejecución diaria. → [docs/06-scheduling.md](docs/06-scheduling.md).

## 📚 Tutorial (orden sugerido)

1. [Arquitectura](docs/01-arquitectura.md) — el diseño y por qué.
2. [Instalación](docs/02-instalacion.md) — setup y primer run.
3. [Skills](docs/03-skills.md) — una capacidad por funcionalidad.
4. [Agentes y LangGraph](docs/04-agentes-langgraph.md) — el código del equipo.
5. [Publicación: blog y redes](docs/05-publicacion-redes.md) — WordPress + upload-post.
6. [Scheduling](docs/06-scheduling.md) — correrlo todos los días.
7. [Claude Cowork](docs/07-cowork.md) — el mismo equipo como agente autónomo.
8. [Mejores prácticas](docs/08-mejores-practicas.md) — el resumen accionable.

## 🗂️ Estructura

```
src/editorial_team/      # el sistema multiagente (LangGraph + Claude)
  ├─ agents/             # un archivo por agente (scout, writer, critic, ...)
  ├─ integrations/       # imágenes, WordPress, upload-post
  ├─ llm.py schemas.py state.py graph.py config.py run_daily.py
skills/                  # 7 Claude Agent Skills (una por funcionalidad)
cowork/PROMPT.md         # prompt para correrlo en Claude Cowork
scheduling/              # cron + launchd
.github/workflows/       # GitHub Actions (run diario)
docs/                    # este tutorial
tests/                   # tests (sin red ni API key)
```

## 🔧 Stack

| | |
|---|---|
| Orquestación | LangGraph |
| Modelo | Claude (`claude-opus-4-8`, `claude-sonnet-4-6`) — SDK `anthropic` |
| Investigación | `web_search` + `web_fetch` (server-side, con citas) |
| Skills | Claude Agent Skills |
| Blog | WordPress REST API |
| Redes | upload-post.com |
| Imágenes | proveedor configurable (`gpt-image-1` por defecto) |

## 🔐 Seguridad

- Los secretos van **sólo** en `.env` (ignorado por git) o en *secrets* de CI.
  En este repo público sólo vive `.env.example` con placeholders.
- WordPress usa **Application Password** (no la contraseña real).
- **`DRY_RUN=true` por defecto**: nada se publica sin intención explícita.
- Estado `draft` en el blog para revisión humana antes de salir en vivo.

Más en [docs/08-mejores-practicas.md](docs/08-mejores-practicas.md).

## ⚠️ Aviso

Proyecto educativo. Verificá siempre el contenido antes de publicar: aunque el
sistema valida y revalida datos, la responsabilidad editorial final es humana. No
constituye consejo de inversión.

## 📄 Licencia

[MIT](LICENSE).
