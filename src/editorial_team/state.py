"""Estado compartido del grafo LangGraph.

En LangGraph el estado es un diccionario tipado que va pasando de nodo en nodo.
Cada agente lee lo que necesita y devuelve un diccionario parcial con las claves
que actualiza (LangGraph las fusiona sobre el estado). Por eso casi todos los
campos son opcionales: se van completando a medida que avanza el pipeline.
"""

from __future__ import annotations

from typing import Annotated, Any, TypedDict


def _append(existing: list, new: list) -> list:
    """Reductor de LangGraph: acumula entradas de log en vez de sobrescribir."""
    return (existing or []) + (new or [])


class EditorialState(TypedDict, total=False):
    # Entrada
    run_date: str  # YYYY-MM-DD
    region: str

    # Producido por cada agente
    topics: list[dict[str, Any]]          # scout: noticias crudas encontradas
    selected: list[dict[str, Any]]        # curator: selección + ángulo
    factcheck: dict[str, Any]             # fact_checker: veredictos + recomendación
    draft: dict[str, Any]                 # writer: editorial
    review: dict[str, Any]                # critic: veredicto de calidad
    revision_count: int                   # cuántas veces se reescribió
    images: list[dict[str, Any]]          # illustrator: imágenes generadas
    social: list[dict[str, Any]]          # social_adapter: variantes por red
    publication: dict[str, Any]           # publisher: resultados de publicación

    # Diagnóstico
    log: Annotated[list[str], _append]
