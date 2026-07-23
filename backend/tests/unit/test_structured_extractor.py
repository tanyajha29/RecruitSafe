import pytest
from app.services.structured_extractor import StructuredExtractor

def test_explicit_extraction():
    job_text = """
    Company: Cyberdyne Systems
    Job Title: Senior Software Developer
    Location: Remote
    Employment Type: Full-time
    Salary: $150,000 - $180,000 per year
    Company Website: https://cyberdyne.com
    Email Address: careers@cyberdyne.com
    Phone Number: +1 (555) 019-9000
    Hiring Process: 3 technical rounds and HR review
    
    Required Skills:
    Python, FastAPI, Docker, and Kubernetes
    
    Experience:
    5+ years of experience in systems engineering
    
    Education:
    Bachelor's Degree in Computer Science or equivalent
    
    Benefits:
    Comprehensive dental, healthcare, and matching 401k
    """
    
    result = StructuredExtractor.extract_all(job_text)
    
    assert result["Company Name"]["value"] == "Cyberdyne Systems"
    assert result["Company Name"]["extraction_status"] == "extracted"
    assert result["Company Name"]["confidence"] == 100
    
    assert result["Job Title"]["value"] == "Senior Software Developer"
    assert result["Employment Type"]["value"] == "Full-time"
    assert result["Location"]["value"] == "Remote"
    assert result["Salary"]["value"] == "$150,000 - $180,000 per year"
    assert result["Recruiter Email"]["value"] == "careers@cyberdyne.com"
    assert result["Company Website"]["value"] == "https://cyberdyne.com"
    assert "comprehensive dental" in result["Benefits"]["value"].lower()
    assert "3 technical rounds" in result["Hiring Process"]["value"].lower()
    assert "python, fastapi" in result["Required Skills"]["value"].lower()
    assert "5+ years of experience" in result["Experience"]["value"].lower()
    assert "bachelor's degree" in result["Education"]["value"].lower()

def test_implicit_extraction():
    job_text = """
    At Stark Industries, we are looking for a lead mechanical engineer to work at our onsite facility. 
    The salary is $200,000 pm. Candidate must have a Master's degree in engineering. 
    Ideal developer must possess 8 years of experience. Contact us at tony@stark.com. 
    Benefits include medical and travel perks.
    """
    
    result = StructuredExtractor.extract_all(job_text)
    
    assert result["Company Name"]["value"] == "Stark Industries"
    assert result["Job Title"]["value"] == "lead mechanical engineer"
    assert result["Location"]["value"] == "onsite"
    assert result["Salary"]["value"] == "$200,000 pm"
    assert result["Recruiter Email"]["value"] == "tony@stark.com"
    assert result["Education"]["value"] == "Master's degree in engineering"
    assert result["Experience"]["value"] == "8 years of experience"

def test_professional_job():
    job_text = """
    Company Name: Nexora Technologies Pvt. Ltd.
    Position: Junior Software Developer
    Employment Type: Full-Time
    Location: Remote (India)
    Salary: ₹8,00,000–₹11,00,000 CTC
    Recruiter Email: careers@nexora-tech.in
    Website: https://careers.nexora-tech.in
    Work Mode: Remote
    """
    result = StructuredExtractor.extract_all(job_text)
    assert result["company_name"]["value"] == "Nexora Technologies Pvt. Ltd."
    assert result["job_title"]["value"] == "Junior Software Developer"
    assert result["employment_type"]["value"] == "Full-Time"
    assert result["location"]["value"] == "Remote (India)"
    assert "₹8,00,000–₹11,00,000 CTC" in result["salary_range"]["value"]
    assert result["recruiter_email_v2"]["value"] == "careers@nexora-tech.in"
    assert result["official_website"]["value"] == "https://careers.nexora-tech.in"
    assert result["work_mode"]["value"] == "Remote"

def test_government_job():
    job_text = """
    Organization: National Informatics Centre (NIC)
    Job Title: Scientific Assistant-A
    Salary: Pay Level 10 (₹56,100 - ₹1,77,500)
    Location: New Delhi, India
    Hiring Process: Written Exam, Personal Interview
    """
    result = StructuredExtractor.extract_all(job_text)
    assert result["company_name"]["value"] == "National Informatics Centre (NIC)"
    assert result["job_title"]["value"] == "Scientific Assistant-A"
    assert "₹56,100" in result["salary_range"]["value"]
    assert "New Delhi" in result["location"]["value"]
    assert "Written Exam" in result["Hiring Process"]["value"]

def test_startup_job():
    job_text = """
    Firm: Zoomer Media Inc
    Role: Backend Developer Intern
    Job Type: Internship
    Work Mode Type: Hybrid
    Joining Date: Immediate selection
    """
    result = StructuredExtractor.extract_all(job_text)
    assert result["company_name"]["value"] == "Zoomer Media Inc"
    assert result["job_title"]["value"] == "Backend Developer Intern"
    assert result["employment_type"]["value"] == "Internship"
    assert result["work_mode"]["value"] == "Hybrid"
    assert "Immediate" in result["joining_timeline"]["value"]

def test_scam_job():
    job_text = """
    Work from home data entry helpers.
    Contact us via WhatsApp wa.me/919999999999 for registration!
    Immediate joining. Paying Rs. 5,000 per day cash. No experience needed!
    """
    result = StructuredExtractor.extract_all(job_text)
    assert result["company_name"]["value"] == "Unknown"
    assert "wa.me" in result["official_website"]["value"]
    assert "919999999999" in result["recruiter_phone"]["value"]

def test_minimal_text():
    job_text = "Hiring Python Coder at Microsoft."
    result = StructuredExtractor.extract_all(job_text)
    assert result["company_name"]["value"] == "Microsoft"
    assert "Coder" in result["job_title"]["value"]

def test_poor_formatting():
    job_text = """
    Company     :      Hooli Inc.
    Job-Title   : ---  Staff SRE ---
    Location    :   Remote (US/Canada)
    """
    result = StructuredExtractor.extract_all(job_text)
    assert result["company_name"]["value"] == "Hooli Inc."
    assert "Staff SRE" in result["job_title"]["value"]
    assert "Remote" in result["location"]["value"]

def test_no_labels():
    job_text = """
    At Apple Corp, we are seeking a senior ios engineer to design mobile apps.
    Work is remote. Compensation matches standard rates.
    Contact recruiters at careers@apple.com.
    """
    result = StructuredExtractor.extract_all(job_text)
    assert result["company_name"]["value"] == "Apple Corp"
    assert result["job_title"]["value"] == "senior ios engineer"
    assert result["location"]["value"] == "remote"
    assert result["recruiter_email_v2"]["value"] == "careers@apple.com"

def test_mixed_labels():
    job_text = """
    Employer:   Tesla Motors
    Job Title:   Autopilot Software Engineer
    Worksite Type: Onsite
    Salary:   $180,000 yearly
    """
    result = StructuredExtractor.extract_all(job_text)
    assert result["company_name"]["value"] == "Tesla Motors"
    assert result["job_title"]["value"] == "Autopilot Software Engineer"
    assert result["work_mode"]["value"] == "Onsite"
    assert "$180,000" in result["salary_range"]["value"]
