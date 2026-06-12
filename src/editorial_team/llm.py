"""Capa de acceso a Claude.

Dos patrones que usan los agentes del grafo:

1. `complete_json(...)` — llamada SIN herramientas que devuelve JSON validado
   contra un JSON Schema usando *structured outputs* (`output_config.format`).

2. `research(...)` — investigación web. Dos backends (config `RESEARCH_BACKEND`):
   - `claude`: herramientas server-side `web_search` + `web_fetch` (con citas).
   - `tavily`: API Tavily para los resultados + síntesis del texto con Claude.

Notas de la API (Claude Opus 4.8 / Sonnet 4.6):
* No se envían `temperature` / `top_p` (removidos en Opus 4.8 → 400).
* `thinking={"type": "adaptive"}` deja que el modelo decida cuánto razonar.
* `effort` se ubica dentro de `output_config`.
"""

from __future__ import annotations

import json
from typing import Any

import anthropic

from .config import get_settings

WEB_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
    {"type": "web_fetch_20260209", "name": "web_fetch"},
]


def get_client() -> anthropic.Anthropic:
    settings = get_settings()
    if settings.anthropic_api_key:
        return anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return anthropic.Anthropic()


def _first_text(content: list[Any]) -> str:
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
    return json.loads(_first_text(resp.content))


def research(
    *,
    system: str,
    user: str,
    model: str,
    max_tokens: int = 8000,
    max_uses: int = 8,
    max_continuations: int = 6,
) -> str:
    """Investiga en la web y devuelve texto con hallazgos. Backend según config."""
    settings = get_settings()
    if settings.research_backend == "tavily":
        return _research_tavily(system=system, user=user, model=model, max_tokens=max_tokens)
    return _research_claude(
        system=system,
        user=user,
        model=model,
        max_tokens=max_tokens,
        max_uses=max_uses,
        max_continuations=max_continuations,
    )


def _research_claude(
    *, system: str, user: str, model: str, max_tokens: int, max_uses: int, max_continuations: int
) -> str:
    client = get_client()
    tools = [{**t, "max_uses": max_uses} for t in WEB_TOOLS]
    messages: list[dict[str, Any]] = [{"role": "user", "content": user}]

    resp = None
    for _ in range(max_continuations):
        resp = client.messages.create(
            model=model, max_tokens=max_tokens, system=system, messages=messages, tools=tools
        )
        if resp.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": resp.content})
            continue
        break

    assert resp is not None
    return _first_text(resp.content)


def _research_tavily(*, system: str, user: str, model: str, max_tokens: int) -> str:
    """Usa Tavily para los resultados y Claude para sintetizar los hallazgos."""
    from .integrations.search import tavily_search

    results = tavily_search(user, max_results=10)
    if not results:
        return "(sin resultados de Tavily)"

    client = get_client()
    context = json.dumps(results, ensure_ascii=False, indent=2)
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{user}\n\nResultados de búsqueda (Tavily) — usá sólo estas fuentes y "
                    f"citá las URLs:\n\n{context}"
                ),
            }
        ],
    )
    return _first_text(resp.content)
