from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

class FieldType(str, Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    EMAIL = "email"

@dataclass(frozen=True)
class FieldRule:
    name: str
    field_type: FieldType
    required: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    regex_pattern: Optional[str] = None

@dataclass
class RowError:
    row_number: int
    column_name: str
    rejected_value: Any
    reason: str

@dataclass
class ValidationReport:
    total_rows: int = 0
    valid_rows: int = 0
    errors: List[RowError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0