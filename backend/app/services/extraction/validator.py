import re
from datetime import datetime, timezone
from typing import Dict, Any, List
from app.services.extraction.models import CanonicalEntity, ValidationResult, StatusEnum

class EntityValidator:
    """
    Layer 3: Validator & Metadata Enricher.
    Validates entities and enriches metadata without overwriting raw extracted values.
    Appends warnings, validation errors, and updates entity status to validated/partially_valid/invalid.
    """

    @classmethod
    def validate_company_name(cls, entity: CanonicalEntity) -> CanonicalEntity:
        if entity.value == "Unknown" or not entity.value:
            return entity

        val_str = str(entity.value).strip()
        val_lower = val_str.lower()
        errors: List[str] = []
        warnings: List[str] = []

        bad_keywords = ["hiring", "opportunity", "job opening", "vacancy", "careers", "apply now"]
        if any(kw in val_lower for kw in bad_keywords):
            errors.append(f"Company name '{val_str}' contains hiring CTA keywords.")

        is_valid = len(errors) == 0
        v_res = ValidationResult(
            is_valid=is_valid,
            validation_errors=errors,
            warnings=warnings,
            validator_name="CompanyNameValidator",
            validated_at=datetime.now(timezone.utc).isoformat()
        )

        entity.validation = v_res.to_dict()
        entity.status = StatusEnum.VALIDATED.value if is_valid else StatusEnum.INVALID.value
        return entity

    @classmethod
    def validate_job_title(cls, entity: CanonicalEntity) -> CanonicalEntity:
        if entity.value == "Unknown" or not entity.value:
            return entity

        val_str = str(entity.value).strip()
        val_lower = val_str.lower()
        errors: List[str] = []
        warnings: List[str] = []

        if len(val_str) > 80:
            errors.append(f"Job title exceeds 80 characters ({len(val_str)} chars).")

        bad_phrases = ["we need", "apply now", "click here", "looking for", "join our team"]
        if any(ph in val_lower for ph in bad_phrases):
            errors.append(f"Job title '{val_str}' contains generic conversational phrases.")

        is_valid = len(errors) == 0
        v_res = ValidationResult(
            is_valid=is_valid,
            validation_errors=errors,
            warnings=warnings,
            validator_name="JobTitleValidator",
            validated_at=datetime.now(timezone.utc).isoformat()
        )

        entity.validation = v_res.to_dict()
        entity.status = StatusEnum.VALIDATED.value if is_valid else StatusEnum.INVALID.value
        return entity

    @classmethod
    def validate_salary(cls, entity: CanonicalEntity) -> CanonicalEntity:
        if entity.value == "Unknown" or not entity.value:
            return entity

        meta = entity.metadata or {}
        min_val = meta.get("minimum")
        max_val = meta.get("maximum")
        period = meta.get("period", "YEARLY")

        errors: List[str] = []
        warnings: List[str] = []
        is_unrealistic = False

        if min_val is not None:
            if period == "YEARLY":
                if min_val < 500 or (max_val and max_val > 2000000):
                    is_unrealistic = True
            elif period == "MONTHLY":
                if min_val < 50 or (max_val and max_val > 150000):
                    is_unrealistic = True
            elif period == "HOURLY":
                if min_val < 2 or (max_val and max_val > 2000):
                    is_unrealistic = True

        if is_unrealistic:
            warnings.append(f"Unrealistic salary range for {period} period (min={min_val}, max={max_val}).")

        is_valid = len(errors) == 0
        status = StatusEnum.VALIDATED.value if (is_valid and not is_unrealistic) else StatusEnum.PARTIALLY_VALID.value

        v_res = ValidationResult(
            is_valid=is_valid,
            validation_errors=errors,
            warnings=warnings,
            validator_name="SalaryValidator",
            validated_at=datetime.now(timezone.utc).isoformat()
        )

        entity.validation = v_res.to_dict()
        entity.status = status
        return entity

    @classmethod
    def validate_email(cls, entity: CanonicalEntity) -> CanonicalEntity:
        if entity.value == "Unknown" or not entity.value:
            return entity

        val_str = str(entity.value).strip()
        errors: List[str] = []
        warnings: List[str] = []

        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_regex.match(val_str):
            errors.append(f"Email '{val_str}' fails RFC 5322 syntax validation.")

        if entity.metadata.get("is_free"):
            warnings.append(f"Recruiter email domain '{entity.metadata.get('domain')}' is a public free provider.")

        is_valid = len(errors) == 0
        v_res = ValidationResult(
            is_valid=is_valid,
            validation_errors=errors,
            warnings=warnings,
            validator_name="EmailValidator",
            validated_at=datetime.now(timezone.utc).isoformat()
        )

        entity.validation = v_res.to_dict()
        entity.status = StatusEnum.VALIDATED.value if is_valid else StatusEnum.INVALID.value
        return entity

    @classmethod
    def validate_website(cls, entity: CanonicalEntity) -> CanonicalEntity:
        if entity.value == "Unknown" or not entity.value:
            return entity

        val_str = str(entity.value).strip()
        errors: List[str] = []
        warnings: List[str] = []

        domain = entity.metadata.get("domain", "")
        if not domain or '.' not in domain or domain.startswith('.') or domain.endswith('.') or "localhost" in domain:
            errors.append(f"Website domain '{domain}' has an invalid structure.")

        is_valid = len(errors) == 0
        v_res = ValidationResult(
            is_valid=is_valid,
            validation_errors=errors,
            warnings=warnings,
            validator_name="WebsiteValidator",
            validated_at=datetime.now(timezone.utc).isoformat()
        )

        entity.validation = v_res.to_dict()
        entity.status = StatusEnum.VALIDATED.value if is_valid else StatusEnum.INVALID.value
        return entity

    @classmethod
    def validate_all(cls, entities: Dict[str, CanonicalEntity]) -> Dict[str, CanonicalEntity]:
        for key, entity in entities.items():
            if entity.value == "Unknown" or not entity.value:
                continue

            if key == "company_name":
                cls.validate_company_name(entity)
            elif key == "job_title":
                cls.validate_job_title(entity)
            elif key == "salary":
                cls.validate_salary(entity)
            elif key == "recruiter_email":
                cls.validate_email(entity)
            elif key == "website":
                cls.validate_website(entity)
            else:
                if entity.status == StatusEnum.NORMALIZED.value:
                    v_res = ValidationResult(
                        is_valid=True,
                        validator_name="GeneralValidator",
                        validated_at=datetime.now(timezone.utc).isoformat()
                    )
                    entity.validation = v_res.to_dict()
                    entity.status = StatusEnum.VALIDATED.value

        return entities
