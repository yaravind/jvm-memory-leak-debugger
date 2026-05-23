"""
schema_validator.py
===================
Small dependency-free JSON Schema subset validator for this skill's public
contracts.

Supported schema features:
- type
- required
- properties
- items
- enum
- oneOf
- additionalProperties
- minimum
- local file $ref values such as "gc_analysis_result.json"
- internal $ref values such as "#/definitions/pattern"
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class SchemaValidationError(ValueError):
    """Raised when a value does not satisfy the supported schema subset."""


def load_schema(path: str) -> Dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def validate_file(data_path: str, schema_path: str) -> None:
    with open(data_path) as f:
        data = json.load(f)
    validate(data, load_schema(schema_path), schema_base=Path(schema_path).parent)


def validate(data: Any, schema: Dict[str, Any], schema_base: Optional[Path] = None, path: str = "$") -> None:
    """Validate data against the supported JSON Schema subset."""
    schema_base = schema_base or Path.cwd()
    root_schema = schema
    _validate(data, schema, schema_base=schema_base, path=path, root_schema=root_schema)


def _validate(
    data: Any,
    schema: Dict[str, Any],
    schema_base: Path,
    path: str,
    root_schema: Dict[str, Any],
) -> None:
    if "$ref" in schema:
        resolved, resolved_base, resolved_root = _resolve_ref(schema["$ref"], schema_base, root_schema)
        _validate(data, resolved, schema_base=resolved_base, path=path, root_schema=resolved_root)
        return

    if "oneOf" in schema:
        _validate_one_of(data, schema["oneOf"], schema_base, path, root_schema)

    if "enum" in schema and data not in schema["enum"]:
        raise SchemaValidationError(f"{path}: expected one of {schema['enum']!r}, got {data!r}")

    if "type" in schema:
        _validate_type(data, schema["type"], path)

    if "minimum" in schema and isinstance(data, (int, float)) and not isinstance(data, bool):
        if data < schema["minimum"]:
            raise SchemaValidationError(f"{path}: expected minimum {schema['minimum']!r}, got {data!r}")

    schema_type = schema.get("type")
    allowed_types = schema_type if isinstance(schema_type, list) else [schema_type]

    if "object" in allowed_types and isinstance(data, dict):
        _validate_object(data, schema, schema_base, path, root_schema)

    if "array" in allowed_types and isinstance(data, list):
        _validate_array(data, schema, schema_base, path, root_schema)


def _resolve_ref(ref: str, schema_base: Path, root_schema: Dict[str, Any]):
    if ref.startswith("#/"):
        target: Any = root_schema
        for part in ref[2:].split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            target = target[part]
        return target, schema_base, root_schema

    ref_path = schema_base / ref
    resolved = load_schema(str(ref_path))
    return resolved, ref_path.parent, resolved


def _validate_one_of(
    data: Any,
    options: List[Dict[str, Any]],
    schema_base: Path,
    path: str,
    root_schema: Dict[str, Any],
) -> None:
    errors = []
    matches = 0
    for option in options:
        try:
            _validate(data, option, schema_base=schema_base, path=path, root_schema=root_schema)
            matches += 1
        except SchemaValidationError as e:
            errors.append(str(e))
    if matches == 1:
        return
    if matches == 0:
        raise SchemaValidationError(f"{path}: expected exactly one matching schema, got none: {errors}")
    raise SchemaValidationError(f"{path}: expected exactly one matching schema, got {matches}")


def _validate_object(
    data: Dict[str, Any],
    schema: Dict[str, Any],
    schema_base: Path,
    path: str,
    root_schema: Dict[str, Any],
) -> None:
    for key in schema.get("required", []):
        if key not in data:
            raise SchemaValidationError(f"{path}: missing required property {key!r}")

    properties = schema.get("properties", {})
    if schema.get("additionalProperties") is False:
        extra = sorted(set(data) - set(properties))
        if extra:
            raise SchemaValidationError(f"{path}: unexpected properties {extra!r}")

    for key, subschema in properties.items():
        if key in data:
            _validate(data[key], subschema, schema_base=schema_base, path=f"{path}.{key}", root_schema=root_schema)


def _validate_array(
    data: List[Any],
    schema: Dict[str, Any],
    schema_base: Path,
    path: str,
    root_schema: Dict[str, Any],
) -> None:
    item_schema = schema.get("items")
    if not item_schema:
        return
    for idx, item in enumerate(data):
        _validate(item, item_schema, schema_base=schema_base, path=f"{path}[{idx}]", root_schema=root_schema)


def _validate_type(data: Any, expected: Any, path: str) -> None:
    expected_types = expected if isinstance(expected, list) else [expected]
    if any(_type_matches(data, t) for t in expected_types):
        return
    raise SchemaValidationError(
        f"{path}: expected type {expected_types!r}, got {type(data).__name__}"
    )


def _type_matches(data: Any, expected: str) -> bool:
    if expected == "null":
        return data is None
    if expected == "boolean":
        return isinstance(data, bool)
    if expected == "integer":
        return isinstance(data, int) and not isinstance(data, bool)
    if expected == "number":
        return isinstance(data, (int, float)) and not isinstance(data, bool)
    if expected == "string":
        return isinstance(data, str)
    if expected == "object":
        return isinstance(data, dict)
    if expected == "array":
        return isinstance(data, list)
    raise SchemaValidationError(f"Unsupported schema type: {expected!r}")
