import json
from pathlib import Path

import pytest

from data_validator.engine import load_schema, validate_csv, validate_record
from data_validator.exceptions import SchemaError, ValidationError


def test_load_schema_success(tmp_path: Path) -> None:
    """Happy path: Loading a valid JSON schema."""
    schema_file = tmp_path / "schema.json"
    schema_file.write_text('{"name": "str", "age": "int"}')

    schema = load_schema(schema_file)
    assert schema == {"name": "str", "age": "int"}


def test_load_schema_missing_file() -> None:
    """Failure path: File doesn't exist."""
    with pytest.raises(SchemaError, match="Schema file not found"):
        load_schema(Path("does_not_exist.json"))


def test_load_schema_invalid_json(tmp_path: Path) -> None:
    """Failure path: Malformed JSON."""
    schema_file = tmp_path / "schema.json"
    schema_file.write_text("{invalid_json:")

    with pytest.raises(SchemaError, match="Malformed JSON in schema"):
        load_schema(schema_file)


def test_validate_record_happy_path() -> None:
    """Happy path: Correct types."""
    schema = {"id": "int", "name": "str", "score": "float"}
    record = {"id": "1", "name": "Alice", "score": "95.5"}

    is_valid, parsed, errors = validate_record(record, schema)

    assert is_valid is True
    assert errors == []
    assert parsed == {"id": 1, "name": "Alice", "score": 95.5}


def test_validate_record_bad_types() -> None:
    """Edge case: Types do not match schema."""
    schema = {"id": "int", "name": "str"}
    record = {"id": "not_an_int", "name": "Bob"}

    is_valid, parsed, errors = validate_record(record, schema)

    assert is_valid is False
    assert parsed is None
    assert "Invalid type for 'id'. Expected int, got 'not_an_int'" in errors[0]


def test_validate_record_empty_fields() -> None:
    """Edge case: Field exists but is empty."""
    schema = {"id": "int"}
    record = {"id": "   "}

    is_valid, _parsed, errors = validate_record(record, schema)

    assert is_valid is False
    assert "Empty value for field: 'id'" in errors[0]


def test_validate_csv_integration(tmp_path: Path) -> None:
    """Integration: Validating a full CSV file."""
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps({"id": "int", "value": "float"}))

    csv_file = tmp_path / "data.csv"
    csv_file.write_text("id,value\n" "1,10.5\n" "2,bad_float\n" ",20.0\n")

    result = validate_csv(csv_file, schema_file)

    assert result.is_valid is False
    assert len(result.valid_records) == 1  # Only row 1 is valid
    assert len(result.errors) == 2  # Row 2 and 3 have errors

    # Check specific errors mapped to line numbers (starts at 2 for data rows)
    assert result.errors[0]["line"] == 3
    assert "Invalid type for 'value'" in result.errors[0]["errors"][0]

    assert result.errors[1]["line"] == 4
    assert "Empty value for field: 'id'" in result.errors[1]["errors"][0]


def test_validate_csv_empty_file(tmp_path: Path) -> None:
    """Edge case: Completely empty CSV."""
    schema_file = tmp_path / "schema.json"
    schema_file.write_text('{"id": "int"}')

    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("")

    with pytest.raises(ValidationError, match="CSV file is empty or missing headers"):
        validate_csv(csv_file, schema_file)
