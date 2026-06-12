"""Agentes del equipo editorial. Cada función es un nodo del grafo LangGraph.

Contrato de un nodo: recibe el `EditorialState` y devuelve un dict parcial con
las claves que actualiza. Nunca muta el estado en el lugar.
"""

from .critic import critic
from .curator import curator
from .fact_checker import fact_checker
from .illustrator import illustrator
from .publisher import publisher
from .scout import scout
from .social_adapter import social_adapter
from .writer import writer

__all__ = [
    "scout",
    "curator",
    "fact_checker",
    "writer",
    "critic",
    "illustrator",
    "social_adapter",
    "publisher",
]
