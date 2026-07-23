import logging
from typing import Dict, Any
from app.services.extraction.raw_extractor import RawExtractor
from app.services.extraction.normalizer import Normalizer
from app.services.extraction.validator import EntityValidator

logger = logging.getLogger("recruitsafe")

class CanonicalExtractionPipeline:
    """
    Canonical Extraction Pipeline Orchestrator.
    Executes the 3-layer architecture:
    Document -> Raw Extractor (Layer 1) -> Normalizer (Layer 2) -> Validator & Metadata Enricher (Layer 3) -> Canonical Entity Schema.
    Maps legacy backward compatibility keys seamlessly.
    """

    @classmethod
    def run_pipeline(cls, text: str) -> Dict[str, Dict[str, Any]]:
        logger.info("CanonicalExtractionPipeline starting 3-layer extraction execution...")

        # Layer 1: Raw Extraction
        raw_entities = RawExtractor.extract_all_raw(text)

        # Layer 2: Normalization
        normalized_entities = Normalizer.normalize_all(raw_entities)

        # Layer 3: Validation & Metadata Enrichment
        validated_entities = EntityValidator.validate_all(normalized_entities)

        # Build final Canonical Schema dictionary
        canonical_schema: Dict[str, Dict[str, Any]] = {}
        for key, entity in validated_entities.items():
            canonical_schema[key] = entity.to_dict()

        # Legacy representation of Hiring Process as string
        hiring_steps_val = canonical_schema["hiring_steps"]["value"]
        hiring_process_str = ", ".join(hiring_steps_val) if isinstance(hiring_steps_val, list) else str(hiring_steps_val)

        legacy_hiring_process = dict(canonical_schema["hiring_steps"])
        legacy_hiring_process["value"] = hiring_process_str

        # Legacy Backward Compatibility Mappings
        legacy_mappings = {
            "Company Name": canonical_schema["company_name"],
            "Job Title": canonical_schema["job_title"],
            "Employment Type": canonical_schema["employment_type"],
            "Salary": canonical_schema["salary"],
            "Location": canonical_schema["location"],
            "Recruiter Email": canonical_schema["recruiter_email"],
            "Company Website": canonical_schema["website"],
            "Benefits": canonical_schema["benefits"],
            "Hiring Process": legacy_hiring_process,
            "Required Skills": canonical_schema["skills"],
            "Experience": canonical_schema["experience"],
            "Education": canonical_schema["education"],

            # Aliases for V2 entity keys
            "salary_range": canonical_schema["salary"],
            "experience_required": canonical_schema["experience"],
            "education_required": canonical_schema["education"],
            "recruiter_email_v2": canonical_schema["recruiter_email"],
            "official_website": canonical_schema["website"],
            "benefits_v2": canonical_schema["benefits"]
        }

        canonical_schema.update(legacy_mappings)
        logger.info("CanonicalExtractionPipeline completed successfully.")
        return canonical_schema
