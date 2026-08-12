from pathlib import Path

import typer

from data_validator.engine import validate_csv
from data_validator.exceptions import DataValidatorError

app = typer.Typer(
    help="CLI tool to parse and validate CSV data against a JSON schema.",
    no_args_is_help=True,
)


@app.command()
def validate(
    data_file: Path = typer.Argument(
        ..., help="Path to the CSV file.", exists=True, dir_okay=False
    ),
    schema_file: Path = typer.Argument(
        ..., help="Path to the JSON schema file.", exists=True, dir_okay=False
    ),
) -> None:
    """Validate a CSV file against a defined JSON schema."""
    try:
        result = validate_csv(data_file, schema_file)

        if result.is_valid:
            typer.secho(
                f"Success! {len(result.valid_records)} records validated.",
                fg=typer.colors.GREEN,
                bold=True,
            )
        else:
            typer.secho(
                f"Validation failed with {len(result.errors)} error(s).",
                fg=typer.colors.RED,
                bold=True,
            )
            for err in result.errors:
                err_msg = ", ".join(err["errors"])
                typer.echo(f"  Line {err['line']}: {err_msg}")

            raise typer.Exit(code=1)

    except DataValidatorError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
