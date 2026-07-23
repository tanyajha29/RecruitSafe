import pytest
from app.services.extraction import (
    CanonicalEntity, EvidenceRecord, ValidationResult, SourceEnum, StatusEnum,
    RawExtractor, Normalizer, EntityValidator, CanonicalExtractionPipeline
)

def test_canonical_entity_structure():
    """Validates that every canonical entity conforms to the standard 5-attribute structure."""
    entity = CanonicalEntity(
        value="Cyberdyne Systems",
        source=SourceEnum.LABEL.value,
        confidence=100,
        status=StatusEnum.EXTRACTED.value
    )
    d = entity.to_dict()

    assert "value" in d
    assert "normalized_value" in d
    assert "source" in d
    assert "confidence" in d
    assert "status" in d
    assert "validation" in d
    assert "metadata" in d
    assert "evidence" in d
    assert "timestamps" in d
    assert d["value"] == "Cyberdyne Systems"
    assert d["normalized_value"] == "Cyberdyne Systems"

def test_raw_extractor_layer1_offsets_and_lines():
    """Tests Layer 1 RawExtractor for line numbers, section tracking, and character offsets."""
    text = (
        "Company: Cyberdyne Systems\n"
        "Position: Senior Developer\n"
        "Salary: $150,000 per year\n"
    )
    entities = RawExtractor.extract_all_raw(text)

    assert entities["company_name"].value == "Cyberdyne Systems"
    assert entities["company_name"].source == SourceEnum.LABEL.value
    assert len(entities["company_name"].evidence) > 0

    ev = entities["company_name"].evidence[0]
    assert ev["line_number"] == 1
    assert ev["character_offsets"] is not None

def test_normalizer_layer2_salary_location_employment():
    """Tests Layer 2 Normalizer for non-destructive normalization and metadata enrichment."""
    raw_entities = {
        "employment_type": CanonicalEntity(value="Full Time", source="label", confidence=100, status="extracted"),
        "location": CanonicalEntity(value="Remote (India)", source="label", confidence=100, status="extracted"),
        "salary": CanonicalEntity(value="₹8L-11L", source="label", confidence=100, status="extracted"),
        "recruiter_email": CanonicalEntity(value="hr@gmail.com", source="regex", confidence=100, status="extracted"),
        "website": CanonicalEntity(value="nexora.com", source="regex", confidence=100, status="extracted")
    }

    norm_entities = Normalizer.normalize_all(raw_entities)

    # Employment Type
    assert norm_entities["employment_type"].normalized_value == "FULL_TIME"
    assert norm_entities["employment_type"].status == StatusEnum.NORMALIZED.value

    # Location
    assert norm_entities["location"].normalized_value == "REMOTE"
    assert norm_entities["location"].metadata["work_mode"] == "REMOTE"

    # Salary
    assert norm_entities["salary"].metadata["minimum"] == 800000
    assert norm_entities["salary"].metadata["maximum"] == 1100000
    assert norm_entities["salary"].metadata["currency"] == "₹"
    assert norm_entities["salary"].metadata["normalized_currency"] == "INR"

    # Email
    assert norm_entities["recruiter_email"].metadata["is_free"] is True
    assert norm_entities["recruiter_email"].metadata["domain"] == "gmail.com"

    # Website
    assert norm_entities["website"].normalized_value == "https://nexora.com"

def test_validator_layer3_warnings_and_errors():
    """Tests Layer 3 EntityValidator for appending warnings without overwriting raw values."""
    entities = {
        "company_name": CanonicalEntity(value="Apply Now Inc", source="label", confidence=100, status="normalized"),
        "salary": CanonicalEntity(value="$100 per year", metadata={"minimum": 100, "period": "YEARLY"}, source="label", confidence=100, status="normalized"),
        "recruiter_email": CanonicalEntity(value="invalid_email_format", source="regex", confidence=100, status="normalized")
    }

    val_entities = EntityValidator.validate_all(entities)

    # Company name invalid CTA
    assert val_entities["company_name"].validation["is_valid"] is False
    assert len(val_entities["company_name"].validation["validation_errors"]) > 0
    assert val_entities["company_name"].value == "Apply Now Inc"  # Preserves raw value!

    # Salary unrealistic warning
    assert len(val_entities["salary"].validation["warnings"]) > 0
    assert val_entities["salary"].status == StatusEnum.PARTIALLY_VALID.value

    # Email invalid syntax
    assert val_entities["recruiter_email"].validation["is_valid"] is False
    assert val_entities["recruiter_email"].status == StatusEnum.INVALID.value

def test_canonical_pipeline_full_and_backward_compatibility():
    """Tests CanonicalExtractionPipeline full 3-layer execution and legacy key mapping."""
    job_text = """
    Company: Nexora Technologies Pvt. Ltd.
    Position: Junior Software Developer
    Salary: ₹8,00,000 – ₹11,00,000
    Location: Remote (India)
    Employment Type: Full-Time
    Email: careers@nexora-tech.in
    Website: https://nexora-tech.in
    Hiring Process: Application, Screening, Technical Interview, HR Offer
    """

    res = CanonicalExtractionPipeline.run_pipeline(job_text)

    # V2 Canonical Entities
    assert res["company_name"]["value"] == "Nexora Technologies Pvt. Ltd."
    assert res["job_title"]["value"] == "Junior Software Developer"
    assert res["employment_type"]["normalized_value"] == "FULL_TIME"
    assert res["salary"]["metadata"]["minimum"] == 800000
    assert res["location"]["metadata"]["work_mode"] == "REMOTE"

    # Legacy Backward Compatibility Mappings
    assert res["Company Name"]["value"] == "Nexora Technologies Pvt. Ltd."
    assert res["Job Title"]["value"] == "Junior Software Developer"
    assert res["Salary"]["value"] == "₹8,00,000 – ₹11,00,000"
    assert isinstance(res["Hiring Process"]["value"], str)
    assert isinstance(res["hiring_steps"]["value"], list)
