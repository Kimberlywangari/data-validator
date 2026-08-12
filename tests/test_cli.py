import json
from pathlib import Path

from typer.testing import CliRunner

from data_validator.cli import app

runner = CliRunner()


def test_cli_success(tmp_path: Path) -> None:
    """Happy path: CLI exits with 0 on valid data."""
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps({"id": "int"}))

    csv_file = tmp_path / "data.csv"
    csv_file.write_text("id\n1\n2\n")

    result = runner.invoke(app, [str(csv_file), str(schema)])

    assert result.exit_code == 0
    assert "Success! 2 records validated" in result.stdout


def test_cli_validation_failure(tmp_path: Path) -> None:
    """Failure path: CLI exits with 1 on invalid data."""
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps({"id": "int"}))

    csv_file = tmp_path / "data.csv"
    csv_file.write_text("id\nbad_int\n")

    result = runner.invoke(app, [str(csv_file), str(schema)])

    assert result.exit_code == 1
    assert "Validation failed" in result.stdout
    assert "Invalid type for 'id'" in result.stdout


def test_cli_missing_files() -> None:
    """Failure path: Typer intercepts missing files."""
    result = runner.invoke(app, ["missing.csv", "missing.json"])

    # Typer should automatically catch that the file doesn't exist.
    # Click 8.2+ CliRunner separates stdout/stderr, and usage errors go to
    # stderr, so check the combined output rather than stdout alone.
    assert result.exit_code != 0
    assert "does not exist" in result.output
