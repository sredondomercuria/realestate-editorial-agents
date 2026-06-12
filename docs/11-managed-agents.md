# 11 · Runtime híbrido: agentes en la plataforma de Claude (Managed Agents)

Hay dos formas de correr el equipo (config `AGENT_RUNTIME`):

- **`local`** — todo el pipeline corre como nodos LangGraph en tu backend. Claude
  se usa como modelo + tools server-side. Simple y portable.
- **`hybrid`** (por defecto) — la **producción autónoma** (investigar → validar →
  redactar → revalidar) corre como un **Managed Agent** en la infraestructura de
  Anthropic; LangGraph orquesta el resto (imágenes, redes, persistencia, publicación,
  UI). Así los agentes "viven en la plataforma de Claude".

## Cómo funciona el híbrido

```
LangGraph (tu backend / Cloud Run)
   START → producer ──────────────► Managed Agent  (Anthropic corre el loop + sandbox)
              │  abre una session,        │  usa agent_toolset (web_search, read, write...)
              │  manda el objetivo,       │  sigue las SKILLS como manual operativo,
              │  escucha el stream  ◄──────┘  devuelve {selected, factcheck, draft, review}
              ▼
        illustrator → social_adapter → publisher → END   (todo local)
```

`src/editorial_team/integrations/managed_agents.py`:
1. **`ensure_environment`** — crea/reusa un *environment* cloud (con red para buscar).
2. **`ensure_agent`** — crea/reusa el *agent*: modelo + `agent_toolset_20260401` +
   un **system prompt que carga las 4 skills** (`news-research`, `fact-check`,
   `editorial-writing`, `critical-review`) como manual operativo.
3. **`run_editorial_team`** — abre una *session*, envía el objetivo del día (con el
   contrato de salida JSON), consume el stream de eventos hasta `idle` y parsea el
   editorial estructurado.

> **Fallback defensivo**: si Managed Agents no está disponible/configurado,
> `run_editorial_team` devuelve `None` y el nodo `producer` corre el sub-pipeline
> **local**. Así el tutorial funciona siempre, con o sin acceso a la beta.

## Setup (crear el agente una vez)

```bash
# Crea/encuentra el environment y el agent, e imprime los IDs:
python -m editorial_team.integrations.managed_agents setup
# Pegá MANAGED_ENV_ID y MANAGED_AGENT_ID en tu .env para cachearlos.
```

Probarlo aislado:

```bash
python -m editorial_team.integrations.managed_agents   # corre una producción de prueba
```

## Skills en la plataforma

Hoy el agente carga el **contenido** de las skills en su system prompt (las lee de
`skills/*/SKILL.md`). Si querés adjuntarlas como **Agent Skills formales** de la
plataforma (Skills API), subilas y referencialas por `skill_id` en `ensure_agent`
(`skills=[{"type":"custom","skill_id":...}]`). Ver la doc de la plataforma Claude →
*Skills* y *Managed Agents*.

## Cuándo usar cada runtime

| | `local` (LangGraph) | `hybrid` (Managed Agents) |
|---|---|---|
| Quién corre el loop | Tu backend | Anthropic |
| Sandbox de tools | — | Contenedor gestionado por Anthropic |
| Control fino del flujo | Máximo | El agente decide su trayectoria |
| Mejor para | Determinismo, costo predecible | Tareas abiertas, menos código de orquestación |

Las dos comparten las **mismas skills** y el **mismo pipeline de distribución**
(imágenes → redes → publicación → UI).

## Alternativa avanzada: Outcomes

En vez de un mensaje, podés arrancar la session con un **Outcome**
(`user.define_outcome` + rúbrica): Anthropic corre un loop iterar→evaluar→corregir
hasta cumplir la rúbrica. Útil para subir el piso de calidad sin escribir el bucle.

## Fin del tutorial
Volvé al [índice](01-arquitectura.md) o al [README](../README.md).
