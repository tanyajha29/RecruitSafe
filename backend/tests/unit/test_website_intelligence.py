import pytest

from app.services.website_intelligence import WebsiteIntelligence
from app.services.email_analyzer import EmailAnalyzer, levenshtein_distance

def test_extract_domain_variations():
    """
    Verifies domain extraction formats (http, https, www, subdomains, ports, query params, email).
    """
    assert WebsiteIntelligence.extract_domain("https://www.google.com/path?query=1") == "google.com"
    assert WebsiteIntelligence.extract_domain("http://infosys.co.in/careers") == "infosys.co.in"
    assert WebsiteIntelligence.extract_domain("infosys-careers.xyz") == "infosys-careers.xyz"
    assert WebsiteIntelligence.extract_domain("recruiter@tcs.com") == "tcs.com"
    assert WebsiteIntelligence.extract_domain("http://localhost:8000/docs") == "localhost"

def test_levenshtein_distance_algorithm():
    """
    Verifies that our custom Levenshtein distance function correctly calculates
    edit distances.
    """
    assert levenshtein_distance("google.com", "go0gle.com") == 1
    assert levenshtein_distance("infosys.com", "infosvs.com") == 1
    assert levenshtein_distance("microsoft.com", "microsoft-careers.com") == 8
    assert levenshtein_distance("apple.com", "apple.com") == 0
    assert levenshtein_distance("", "test") == 4

def test_email_analyzer_domain_parsing():
    """
    Verifies that email domains are extracted and validated correctly.
    """
    assert EmailAnalyzer.parse_domain("hr-team@google.com") == "google.com"
    assert EmailAnalyzer.parse_domain("invalid-email") == ""

@pytest.mark.asyncio
async def test_email_analyzer_free_disposable_detection():
    """
    Verifies that public free email accounts and temp/disposable emails are identified.
    """
    res_gmail = await EmailAnalyzer.analyze_recruiter_email("recruiter.job@gmail.com")
    assert res_gmail["is_free_email"] is True
    assert res_gmail["is_disposable"] is False
    
    res_temp = await EmailAnalyzer.analyze_recruiter_email("scammer@mailinator.com")
    assert res_temp["is_free_email"] is False
    assert res_temp["is_disposable"] is True
    
    res_corporate = await EmailAnalyzer.analyze_recruiter_email("careers@accenture.com")
    assert res_corporate["is_free_email"] is False
    assert res_corporate["is_disposable"] is False

@pytest.mark.asyncio
async def test_email_analyzer_typosquatting_detection():
    """
    Verifies that looking-alike recruiter domains (typosquatting or unofficial suffix)
    are successfully flagged relative to company domains.
    """
    # 1. Exact match
    typo1 = await EmailAnalyzer.check_typosquatting("infosys.com", "infosys.com")
    assert typo1["is_exact_match"] is True
    assert typo1["is_suspicious_typosquatting"] is False
    
    # 2. Public email (should not trigger typosquatting check directly)
    typo2 = await EmailAnalyzer.check_typosquatting("gmail.com", "infosys.com")
    assert typo2["is_exact_match"] is False
    assert typo2["is_suspicious_typosquatting"] is False
    
    # 3. Typosquatting (Edit distance <= 3)
    typo3 = await EmailAnalyzer.check_typosquatting("infosvs.com", "infosys.com")
    assert typo3["is_exact_match"] is False
    assert typo3["is_suspicious_typosquatting"] is True
    assert "closely resembles" in typo3["reason"]
    
    # 4. Unofficial subdomain/suffix containing company name
    typo4 = await EmailAnalyzer.check_typosquatting("infosys-careers.com", "infosys.com")
    assert typo4["is_exact_match"] is False
    assert typo4["is_suspicious_typosquatting"] is True
    assert "unofficial domain suffix" in typo4["reason"]

@pytest.mark.asyncio
async def test_whois_fallback_graceful_handling():
    """
    Verifies that WHOIS lookup handles exceptions gracefully (e.g. invalid domains)
    and returns a structured dict rather than crashing.
    """
    res = await WebsiteIntelligence.get_domain_whois("non-existent-domain-12345-xyz.invalid")
    assert res["whois_failed"] is True
    assert res["domain_age_days"] is None
    assert res["registrar"] is None
