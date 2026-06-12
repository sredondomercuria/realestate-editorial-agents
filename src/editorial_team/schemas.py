"""JSON Schemas para *structured outputs* de Claude.

Cada agente pide a Claude una salida que cumple uno de estos esquemas. Se usan
los subconjuntos soportados por structured outputs: tipos básicos, `enum`,
arrays, objetos con `additionalProperties: false` y `required`. No se usan
restricciones no soportadas (minLength, minimum, etc.).
"""

from __future__ import annotations


def _obj(properties: dict, required: list[str]) -> dict:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


# --- Scout: noticias candidatas --------------------------------------------
TOPICS_SCHEMA = _obj(
    {
        "topics": {
            "type": "array",
            "items": _obj(
                {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "source_name": {"type": "string"},
                    "source_url": {"type": "string"},
                    "published_hint": {"type": "string"},
                    "region": {"type": "string"},
                    "relevance": {"type": "integer"},
                },
                ["title", "summary", "source_name", "source_url", "region", "relevance"],
            ),
        }
    },
    ["topics"],
)

# --- Curador: selección + ángulo editorial ---------------------------------
CURATION_SCHEMA = _obj(
    {
        "selected": {
            "type": "array",
            "items": _obj(
                {
                    "title": {"type": "string"},
                    "angle": {"type": "string"},
                    "why_it_matters": {"type": "string"},
                    "key_points": {"type": "array", "items": {"type": "string"}},
                    "primary_source": {"type": "string"},
                    "related_sources": {"type": "array", "items": {"type": "string"}},
                },
                ["title", "angle", "why_it_matters", "key_points", "primary_source"],
            ),
        }
    },
    ["selected"],
)

# --- Fact-checker: veredictos por afirmación -------------------------------
FACTCHECK_SCHEMA = _obj(
    {
        "verdicts": {
            "type": "array",
            "items": _obj(
                {
                    "claim": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["verified", "uncertain", "refuted"],
                    },
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "sources": {"type": "array", "items": {"type": "string"}},
                    "note": {"type": "string"},
                },
                ["claim", "status", "sources"],
            ),
        },
        "recommendation": {
            "type": "string",
            "enum": ["proceed", "revise", "drop"],
        },
        "summary": {"type": "string"},
    },
    ["verdicts", "recommendation", "summary"],
)

# --- Redactor: editorial completo ------------------------------------------
EDITORIAL_SCHEMA = _obj(
    {
        "title": {"type": "string"},
        "slug": {"type": "string"},
        "dek": {"type": "string"},
        "body_markdown": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "seo_description": {"type": "string"},
        "sources": {"type": "array", "items": {"type": "string"}},
        "image_brief": {"type": "string"},
    },
    ["title", "slug", "dek", "body_markdown", "tags", "seo_description", "sources", "image_brief"],
)

# --- Crítico: control de calidad y revalidación ----------------------------
REVIEW_SCHEMA = _obj(
    {
        "verdict": {"type": "string", "enum": ["approved", "needs_revision"]},
        "score": {"type": "integer"},
        "issues": {
            "type": "array",
            "items": _obj(
                {
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "type": {
                        "type": "string",
                        "enum": ["factual", "sourcing", "clarity", "bias", "legal", "style"],
                    },
                    "detail": {"type": "string"},
                    "fix": {"type": "string"},
                },
                ["severity", "type", "detail", "fix"],
            ),
        },
        "notes": {"type": "string"},
    },
    ["verdict", "score", "issues", "notes"],
)

# --- Ilustrador: prompt de imagen + alt-text -------------------------------
IMAGE_PROMPT_SCHEMA = _obj(
    {
        "prompt": {"type": "string"},
        "negative_prompt": {"type": "string"},
        "alt_text": {"type": "string"},
        "caption": {"type": "string"},
        "style": {"type": "string"},
    },
    ["prompt", "alt_text", "caption"],
)

# --- Social: variantes por red ---------------------------------------------
SOCIAL_SCHEMA = _obj(
    {
        "variants": {
            "type": "array",
            "items": _obj(
                {
                    "platform": {"type": "string"},
                    "text": {"type": "string"},
                    "hashtags": {"type": "array", "items": {"type": "string"}},
                },
                ["platform", "text", "hashtags"],
            ),
        }
    },
    ["variants"],
)
