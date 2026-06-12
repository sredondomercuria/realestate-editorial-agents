# 04 · Los agentes y el grafo LangGraph

## Idea central

En LangGraph un **nodo** es una función que recibe el estado y devuelve un dict con
las claves que actualiza. Las **aristas** definen el orden; una **arista
condicional** permite ramas y bucles.

```python
def writer(state: EditorialState) -> dict:
    ...
    return {"draft": draft, "revision_count": state.get("revision_count", 0) + 1}
```

## El acceso a Claude (`llm.py`)

Dos patrones cubren todo el equipo:

### 1. `complete_json(...)` — salida estructurada sin herramientas

Usa *structured outputs* (`output_config.format`) para garantizar JSON válido
contra un esquema. Lo usan curador, redactor, crítico, ilustrador y social.

```python
resp = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=12000,
    system=SYSTEM,
    messages=[{"role": "user", "content": user}],
    output_config={"format": {"type": "json_schema", "schema": EDITORIAL_SCHEMA},
                   "effort": "high"},
    thinking={"type": "adaptive"},   # razonamiento adaptativo (opcional)
)
```

> ⚠️ En Claude Opus 4.8 **no** se envían `temperature` / `top_p` (fueron removidos).
> El razonamiento se controla con `thinking: {type: "adaptive"}` y `effort`.

### 2. `research(...)` — investigación web con citas

Usa las herramientas server-side `web_search` + `web_fetch`. Claude ejecuta las
búsquedas en su infraestructura y devuelve texto con citas. No se combina con
structured outputs (las citas y el formato JSON son incompatibles), así que el
resultado se **estructura en un segundo paso** con `complete_json`.

```python
tools = [
    {"type": "web_search_20260209", "name": "web_search", "max_uses": 10},
    {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 10},
]
# Maneja stop_reason == "pause_turn" reenviando la conversación.
```

Lo usan scout, fact-checker y la revalidación del crítico.

## Patrón "investigar → estructurar"

Los nodos con web hacen dos llamadas: una potente con herramientas (Opus) para
investigar, y una liviana (Sonnet) para estructurar el texto en JSON. Esto separa
razonamiento de formato y abarata el paso de estructuración.

```python
findings = research(system=SYSTEM, user=user, model=settings.model_scout)
topics  = complete_json(system=STRUCT, user=findings,
                        schema=TOPICS_SCHEMA, model=settings.model_curator)["topics"]
```

## Modelos por agente

Cada rol usa el modelo más adecuado (configurable en `.env`):

| Agente | Modelo por defecto | Por qué |
|--------|--------------------|---------|
| scout / fact-checker / writer / critic | `claude-opus-4-8` | Razonamiento e investigación exigentes |
| curator / illustrator / social | `claude-sonnet-4-6` | Tareas más acotadas, mejor costo/latencia |

## El grafo (`graph.py`)

`build_graph()` arma el grafo **según `AGENT_RUNTIME`**:

- **`hybrid`** (default): `START → producer → illustrator → social_adapter → publisher`.
  El nodo `producer` delega en un Managed Agent (ver [11-managed-agents.md](11-managed-agents.md)).
- **`local`**: el sub-pipeline completo con el bucle de revalidación crítica:

```python
# Variante local (en hybrid, estos 5 nodos los reemplaza `producer`)
g.add_edge(START, "scout")
g.add_edge("scout", "curator")
g.add_edge("curator", "fact_checker")
g.add_edge("fact_checker", "writer")
g.add_edge("writer", "critic")
g.add_conditional_edges("critic", route_after_review,
                        {"revise": "writer", "approve": "illustrator"})
# Distribución (común a ambos runtimes):
g.add_edge("illustrator", "social_adapter")
g.add_edge("social_adapter", "publisher")
g.add_edge("publisher", END)
```

`route_after_review` devuelve `revise` (vuelve al redactor) o `approve` (sigue),
según el veredicto del crítico y cuántas revisiones quedan. El nodo `producer` del
modo híbrido tiene **fallback**: si Managed Agents no está disponible, corre el
sub-pipeline local internamente y devuelve el mismo resultado.

## Ejecutar

```python
from editorial_team import build_graph
app = build_graph()
final = app.invoke({"region": "Argentina y Latinoamérica", "revision_count": 0, "log": []},
                   config={"recursion_limit": 50})
```

`run_daily.py` hace exactamente esto, agrega la fecha, guarda artefactos e imprime
el resumen.

## Extender el equipo

- **Nuevo agente**: creá `agents/mi_agente.py`, exportalo en `agents/__init__.py`,
  agregalo al grafo con `add_node` y conectá aristas.
- **Nueva rama**: usá `add_conditional_edges` con tu función de ruteo.
- **Memoria entre días**: agregá un *checkpointer* de LangGraph para persistir
  estado.

## Siguiente
→ [05-publicacion-redes.md](05-publicacion-redes.md)
