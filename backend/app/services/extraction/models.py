from enum import Enum
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field

class SourceEnum(str, Enum):
    LABEL = "label"
    REGEX = "regex"
    SECTION = "section"
    OCR = "ocr"
    AI = "ai"
    MANUAL = "manual"
    NONE = "none"

class StatusEnum(str, Enum):
    EXTRACTED = "extracted"
    NORMALIZED = "normalized"
    VALIDATED = "validated"
    PARTIALLY_VALID = "partially_valid"
    INVALID = "invalid"
    NOT_FOUND = "not_found"

@dataclass
class EvidenceRecord:
    matched_text: str = ""
    matched_pattern: str = ""
    page_number: Optional[int] = None
    line_number: Optional[int] = None
    section_name: Optional[str] = None
    character_offsets: Optional[List[int]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matched_text": self.matched_text,
            "matched_pattern": self.matched_pattern,
            "page_number": self.page_number,
            "line_number": self.line_number,
            "section_name": self.section_name,
            "character_offsets": self.character_offsets
        }

@dataclass
class ValidationResult:
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validator_name: str = "StandardValidator"
    validated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "warnings": self.warnings,
            "validator_name": self.validator_name,
            "validated_at": self.validated_at or datetime.now(timezone.utc).isoformat()
        }

@dataclass
class CanonicalEntity:
    value: Any = "Unknown"
    normalized_value: Any = None
    source: str = SourceEnum.NONE.value
    confidence: int = 0
    status: str = StatusEnum.NOT_FOUND.value
    validation: Dict[str, Any] = field(default_factory=lambda: ValidationResult().to_dict())
    metadata: Dict[str, Any] = field(default_factory=dict)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    timestamps: Dict[str, str] = field(default_factory=lambda: {"extracted_at": datetime.now(timezone.utc).isoformat()})

    def to_dict(self) -> Dict[str, Any]:
        normalized = self.normalized_value if self.normalized_value is not None else self.value
        is_found = self.status in [
            StatusEnum.EXTRACTED.value,
            StatusEnum.NORMALIZED.value,
            StatusEnum.VALIDATED.value,
            StatusEnum.PARTIALLY_VALID.value
        ] and self.value != "Unknown"

        return {
            "value": self.value,
            "normalized_value": normalized,
            "source": self.source,
            "confidence": self.confidence,
            "status": self.status,
            "extraction_status": "extracted" if is_found else "not_found",  # Legacy backward compatibility key
            "validation": self.validation,
            "metadata": self.metadata,
            "evidence": self.evidence,
            "timestamps": self.timestamps
        }
