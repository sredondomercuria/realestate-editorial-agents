"""Backend de búsqueda Tavily (alternativa a las herramientas web de Claude).

Tavily está optimizada para agentes: devuelve resultados ya filtrados y listos
para que el LLM los consuma. Lo usamos como fuente de resultados; la síntesis del
texto de hallazgos la hace Claude (en `llm.research`).

Devuelve una lista de resultados `{title, url, content}`.
"""

from __future__ import annotations

from ..config import get_settings


def tavily_search(query: str, *, max_results: int = 8, days: int = 7) -> list[dict]:
    settings = get_settings()
    try:
        from tavily import TavilyClient
    except ImportError:
        print("[search] falta `tavily-python`; instalá `pip install tavily-python`.")
        return []

    if not settings.tavily_api_key:
        print("[search] falta TAVILY_API_KEY.")
        return []

    try:
        client = TavilyClient(api_key=settings.tavily_api_key)
        resp = client.search(
            query=query,
            max_results=max_results,
            topic="news",
            days=days,
            search_depth="advanced",
        )
        return [
            {"title": r.get("title", ""), "url": r.get("url", ""), "content": r.get("content", "")}
            for r in resp.get("results", [])
        ]
    except Exception as exc:  # noqa: BLE001
        print(f"[search] fallo Tavily: {exc}")
        return []
