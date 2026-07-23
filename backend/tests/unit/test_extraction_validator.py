import pytest
from app.services.extraction_validator import ExtractionValidator

def test_company_name_validation():
    # Valid
    ok, conf, val = ExtractionValidator.validate_company_name("Google Inc.")
    assert ok is True
    assert conf == 100
    assert val == "Google Inc."
    
    # Generic
    ok, conf, val = ExtractionValidator.validate_company_name("unknown")
    assert ok is False
    assert val == "Unknown"
    
    # Bad keyword
    ok, conf, val = ExtractionValidator.validate_company_name("Careers Opportunity")
    assert ok is False

def test_job_title_validation():
    # Valid
    ok, conf, val = ExtractionValidator.validate_job_title("Senior Python Developer")
    assert ok is True
    
    # Unrealistic long sentence
    ok, conf, val = ExtractionValidator.validate_job_title("A very long job title that describes how we need someone to work for us immediately click here to apply")
    assert ok is False

def test_salary_validation():
    # Valid range monthly
    ok, conf, val, meta = ExtractionValidator.validate_salary("$5,000 to $7,000 pm")
    assert ok is True
    assert meta["period"] == "monthly"
    assert meta["is_range"] is True
    assert meta["min"] == 5000
    assert meta["max"] == 7000
    
    # Unrealistic yearly
    ok, conf, val, meta = ExtractionValidator.validate_salary("$10 yearly")
    assert ok is False
    assert conf == 20
    
    ok, conf, val, meta = ExtractionValidator.validate_salary("$5,000,000 annual")
    assert ok is False
    assert conf == 20

def test_location_validation():
    ok, conf, val = ExtractionValidator.validate_location("Remote (New York, NY)")
    assert ok is True
    assert val == "Remote (New York, NY)"

def test_employment_type_validation():
    ok, conf, val = ExtractionValidator.validate_employment_type("full-time employment")
    assert ok is True
    assert val == "Full Time"
    
    ok, conf, val = ExtractionValidator.validate_employment_type("intern ship")
    assert ok is True
    assert val == "Internship"

def test_email_validation():
    # Corporate
    ok, conf, val, meta = ExtractionValidator.validate_email("hr@google.com")
    assert ok is True
    assert meta["is_free"] is False
    
    # Free
    ok, conf, val, meta = ExtractionValidator.validate_email("recruiter@gmail.com")
    assert ok is True
    assert meta["is_free"] is True
    
    # Invalid RFC
    ok, conf, val, meta = ExtractionValidator.validate_email("not-an-email")
    assert ok is False

def test_website_validation():
    # Normalizing scheme and stripping trailing slash
    ok, conf, val = ExtractionValidator.validate_website("google.com/")
    assert ok is True
    assert val == "https://google.com"
    
    # Invalid domain
    ok, conf, val = ExtractionValidator.validate_website("google")
    assert ok is False
    
    ok, conf, val = ExtractionValidator.validate_website("localhost:3000")
    assert ok is False
