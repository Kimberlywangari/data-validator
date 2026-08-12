"""Domain-specific exceptions for data_validator."""


class DataValidatorError(Exception):
    """Base exception for all data-validator errors."""


class SchemaError(DataValidatorError):
    """Raised when the schema file is missing, unreadable, or malformed."""


class ValidationError(DataValidatorError):
    """Raised when a CSV file cannot be validated at all (e.g. empty/no headers)."""