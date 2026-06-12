"""Capa de acceso a Claude.

Encapsula dos patrones que usan los agentes del grafo:

1. `complete_json(...)` — llamada SIN herramientas que devuelve JSON validado
   contra un JSON Schema usando *structured outputs* (`output_config.format`).
   Ideal para redacción, curaduría, crítica, etc.

2. `research(...)` — llamada CON las herramientas server-side de Claude
   (`web_search` + `web_fetch`) para investigar en la web con citas. No se puede
   combinar con structured outputs (las citas y el formato JSON son
   incompatibles), por eso el resultado es texto y se estructura en un segundo
   paso con `complete_json`.

Notas de la API (Claude Opus 4.8 / Sonnet 4.6):
* No se envían `temperature` / `top_p` (fueron removidos en Opus 4.8 → 400).
* `thinking={"type": "adaptive"}` deja que el modelo decida cuánto razonar.
* `effort` se ubica dentro de `output_config`.
"""

from __future__ import annotations

import json
from typing import Any

import anthropic

from .config import get_settings

# Herramientas server-side: Claude ejecuta la búsqueda/fetch en su infraestructura
# y devuelve resultados con citas. La versión _20260209 incluye filtrado dinámico.
WEB_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
    {"type": "web_fetch_20260209", "name": "web_fetch"},
]


def get_client() -> anthropic.Anthropic:
    settings = get_settings()
    # Si anthropic_api_key viene vacío, el SDK toma ANTHROPIC_API_KEY del entorno.
    if settings.anthropic_api_key:
        return anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return anthropic.Anthropic()


def _first_text(content: list[Any]) -> str:
    """Concatena los bloques de texto de una respuesta (ignora thinking/tool_use)."""
    return "".join(b.text for b in content if getattr(b, "type", None) == "text")


def complete_json(
    *,
    system: str,
    user: str,
    schema: dict,
    model: str,
    max_tokens: int = 8000,
    effort: str = "high",
    thinking: bool = False,
) -> dict:
    """Pide a Claude una respuesta que cumple `schema` (structured outputs)."""
    client = get_client()
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "output_config": {
            "format": {"type": "json_schema", "schema": schema},
            "effort": effort,
        },
    }
    if thinking:
        kwargs["thinking"] = {"type": "adaptive"}

    resp = client.messages.create(**kwargs)

    if resp.stop_reason == "refusal":
        raise RuntimeError(f"Claude rechazó la solicitud: {resp.stop_details}")

    text = _first_text(resp.content)
    return json.loads(text)


def research(
    *,
    system: str,
    user: str,
    model: str,
    max_tokens: int = 8000,
    max_uses: int = 8,
    max_continuations: int = 6,
) -> str:
    """Investiga en la web con `web_search` + `web_fetch` y devuelve texto con hallazgos.

    Maneja `stop_reason == "pause_turn"`: cuando el bucle server-side de
    herramientas llega a su límite, se reenvía la conversación para continuar.
    """
    client = get_client()
    tools = [{**t, "max_uses": max_uses} for t in WEB_TOOLS]
    messages: list[dict[str, Any]] = [{"role": "user", "content": user}]

    resp = None
    for _ in range(max_continuations):
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            tools=tools,
        )
        if resp.stop_reason == "pause_turn":
            # El servidor pausó tras varias iteraciones de herramientas: reanudar.
            messages.append({"role": "assistant", "content": resp.content})
            continue
        break

    assert resp is not None
    return _first_text(resp.content)
