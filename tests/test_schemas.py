"""Los JSON Schemas deben ser válidos para structured outputs de Claude:
objetos con additionalProperties=false y campos required presentes en properties.
"""

from __future__ import annotations

import pytest

from editorial_team import schemas

ALL_SCHEMAS = [
    schemas.TOPICS_SCHEMA,
    schemas.CURATION_SCHEMA,
    schemas.FACTCHECK_SCHEMA,
    schemas.EDITORIAL_SCHEMA,
    schemas.REVIEW_SCHEMA,
    schemas.IMAGE_PROMPT_SCHEMA,
    schemas.SOCIAL_SCHEMA,
]


def _check_object(node: dict) -> None:
    assert node["type"] == "object"
    assert node.get("additionalProperties") is False
    props = node["properties"]
    for req in node.get("required", []):
        assert req in props, f"required '{req}' no está en properties"
    # Recursión sobre objetos anidados / items de arrays
    for value in props.values():
        if value.get("type") == "object":
            _check_object(value)
        if value.get("type") == "array" and value["items"].get("type") == "object":
            _check_object(value["items"])


@pytest.mark.parametrize("schema", ALL_SCHEMAS)
def test_schema_is_well_formed(schema):
    _check_object(schema)
