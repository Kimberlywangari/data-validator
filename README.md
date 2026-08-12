# Data Validator

A small Python CLI + library for validating CSV data against a JSON schema.
Given a schema like `{"id": "int", "name": "str", "score": "float"}`, it reads
a CSV file row by row, coerces each value to the declared type, and reports
exactly which rows/fields fail and why.

## Project layout

```
data-validator/
├── .venv
├── pyproject.toml
├── samples/
│   ├── schema.json          # example schema
│   └── users.csv            # example data (includes bad rows on purpose)
├── src/data_validator/
│   ├── __init__.py
│   ├── cli.py                # Typer CLI entry point
│   ├── engine.py              # core logic: load_schema, validate_record, validate_csv
│   ├── exceptions.py         # DataValidatorError, SchemaError, ValidationError
│   └── py.typed              # marks the package as typed for mypy
└── tests/
    ├── __init__.py
    ├── test_cli.py
    └── test_engine.py

```

## Setup

Requires Python 3.10+. Everything is installed into a local virtual
environment — nothing is installed globally.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# installs the package itself + dev tools (pytest, mypy, ruff, black)
pip install -e ".[dev]"
```

## Running the CLI

```bash
data-validator samples/users.csv samples/schema.json
```

or, without an editable install:

```bash
python -m data_validator.cli samples/users.csv samples/schema.json
```

Example output against `samples/users.csv` (which deliberately contains a bad
float, a missing id, a missing name, and a missing score):

```
Validation failed with 4 error(s).
  Line 3: Invalid type for 'score'. Expected float, got 'invalid_float'
  Line 4: Empty value for field: 'id'
  Line 5: Empty value for field: 'name'
  Line 6: Empty value for field: 'score'
```

Exit code is `0` when every row is valid, `1` when any row fails validation
or the schema/CSV can't be read at all.

### Schema format

A schema is a flat JSON object mapping column name → type name. Supported
types: `"int"`, `"float"`, `"str"`.

```json
{"id": "int", "name": "str", "score": "float"}
```

## Running the checks

```bash
ruff check .                        # lint
black --check .                     # formatting
mypy                                 # strict type checking
python -m pytest                    # tests + coverage (configured in pyproject.toml)
```

All four currently pass clean, with **94% test coverage** on `src/data_validator`.

