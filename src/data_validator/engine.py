"""Core validation logic: schema loading, record checks, and CSV validation."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from data_validator.exceptions import SchemaError, ValidationError

#: Supported schema field types and the callables used to coerce raw strings.
_CASTERS: dict[str, type] = {
    "int": int,
    "float": float,
    "str": str,
}


@dataclass
class ValidationResult:
    """Outcome of validating an entire CSV file against a schema."""

    valid_records: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True when every row parsed cleanly."""
        return len(self.errors) == 0


def load_schema(schema_path: Path) -> dict[str, str]:
    """Load a JSON schema mapping column name -> type name ("int"/"float"/"str").

    Raises:
        SchemaError: if the file does not exist or is not valid JSON.
    """
    if not schema_path.exists():
        raise SchemaError(f"Schema file not found: {schema_path}")

    try:
        raw_text = schema_path.read_text()
        schema = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise SchemaError(f"Malformed JSON in schema: {schema_path}") from exc

    if not isinstance(schema, dict):
        raise SchemaError(f"Schema must be a JSON object: {schema_path}")

    for column, type_name in schema.items():
        if type_name not in _CASTERS:
            raise SchemaError(
                f"Unsupported type '{type_name}' for field '{column}'. "
                f"Expected one of {sorted(_CASTERS)}."
            )

    return schema


def validate_record(
    record: dict[str, str], schema: dict[str, str]
) -> tuple[bool, dict[str, Any] | None, list[str]]:
    """Validate a single row (as produced by csv.DictReader) against a schema.

    Returns:
        (is_valid, parsed_record_or_None, list_of_error_messages)
    """
    errors: list[str] = []
    parsed: dict[str, Any] = {}

    for column, type_name in schema.items():
        raw_value = record.get(column)

        if raw_value is None or raw_value.strip() == "":
            errors.append(f"Empty value for field: '{column}'")
            continue

        caster = _CASTERS[type_name]
        try:
            parsed[column] = caster(raw_value.strip())
        except (ValueError, TypeError):
            errors.append(
                f"Invalid type for '{column}'. Expected {type_name}, "
                f"got '{raw_value}'"
            )

    if errors:
        return False, None, errors
    return True, parsed, []


def validate_csv(csv_path: Path, schema_path: Path) -> ValidationResult:
    """Validate every row in a CSV file against a JSON schema.

    Raises:
        SchemaError: if the schema file is missing/malformed (see load_schema).
        ValidationError: if the CSV file is empty or has no header row.
    """
    schema = load_schema(schema_path)

    with csv_path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValidationError(f"CSV file is empty or missing headers: {csv_path}")

        result = ValidationResult()
        # Data rows start at line 2 (line 1 is the header).
        for line_number, row in enumerate(reader, start=2):
            is_valid, parsed, errors = validate_record(row, schema)
            if is_valid and parsed is not None:
                result.valid_records.append(parsed)
            else:
                result.errors.append({"line": line_number, "errors": errors})

    return result
