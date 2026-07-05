import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.email_verifier import EmailVerifier
from app.services.website_verifier import WebsiteVerifier
from app.services.hiring_workflow_analyzer import HiringWorkflowAnalyzer
from app.services.company_verifier import CompanyVerifier
from app.services.confidence_calculator import ConfidenceCalculator
from app.services.risk_scorer import RiskScorer
from app.services.recommendation_engine import RecommendationEngine
from app.services.pipeline_orchestrator import PipelineOrchestrator

# ==========================================
# 1. EmailVerifier Tests
# ==========================================
def test_email_syntax_validation():
    assert EmailVerifier.validate_syntax("test@company.com") is True
    assert EmailVerifier.validate_syntax("invalid-email") is False
    assert EmailVerifier.validate_syntax("test@.com") is False

def test_email_domain_extraction():
    assert EmailVerifier.extract_domain("test@company.com") == "company.com"
    assert EmailVerifier.extract_domain("  USER@Sub.Company.Co.In  ") == "sub.company.co.in"
    assert EmailVerifier.extract_domain("no-at-sign") == ""

def test_email_type_checks():
    assert EmailVerifier.is_free("gmail.com") is True
    assert EmailVerifier.is_free("yahoo.com") is True
    assert EmailVerifier.is_free("mycorp.com") is False

    assert EmailVerifier.is_disposable("mailinator.com") is True
    assert EmailVerifier.is_disposable("tempmail.com") is True
    assert EmailVerifier.is_disposable("outlook.com") is False

def test_typosquatting_check():
    # Exact Match
    res1 = EmailVerifier.check_typosquatting("google.com", "google.com")
    assert res1["is_exact_match"] is True
    assert res1["is_suspicious_typosquatting"] is False

    # Typosquatting (Levenshtein distance 1)
    res2 = EmailVerifier.check_typosquatting("googel.com", "google.com")
    assert res2["is_exact_match"] is False
    assert res2["is_suspicious_typosquatting"] is True

    # Suffix typosquatting
    res3 = EmailVerifier.check_typosquatting("google-jobs.com", "google.com")
    assert res3["is_suspicious_typosquatting"] is True

@pytest.mark.asyncio
@patch("dns.resolver.resolve")
@patch("socket.gethostbyname")
async def test_email_dns_mx_check(mock_host, mock_resolve):
    mock_host.return_value = "1.2.3.4"
    mock_resolve.return_value = [MagicMock()]
    
    # We patch CacheEntry to skip database interactions
    with patch("app.models.cache.CacheEntry.find_one", return_value=None):
        res = await EmailVerifier.verify_dns_mx("legitdomain.com")
        assert res["dns_exists"] is True
        assert res["has_mx"] is True

# ==========================================
# 2. WebsiteVerifier Tests
# ==========================================
def test_url_extraction():
    text = "Visit our page at https://google.com/careers to apply."
    assert WebsiteVerifier.extract_url(text) == "https://google.com/careers"

    text2 = "Contact us via company.com or email us."
    assert WebsiteVerifier.extract_url(text2) == "https://company.com"

def test_domain_parsing():
    assert WebsiteVerifier.parse_domain("https://sub.company.co.in/path?q=1") == "company.co.in"
    assert WebsiteVerifier.parse_domain("http://www.google.com") == "google.com"

@pytest.mark.asyncio
@patch("whois.whois")
async def test_whois_age_calculation(mock_whois):
    w_mock = MagicMock()
    w_mock.creation_date = datetime.now() - timedelta(days=2000)
    w_mock.registrar = "GoDaddy"
    w_mock.country = "US"
    mock_whois.return_value = w_mock

    with patch("app.models.cache.CacheEntry.find_one", return_value=None):
        res = await WebsiteVerifier.get_whois_record("olddomain.com")
        assert res["whois_failed"] is False
        assert res["domain_age_days"] >= 1999
        assert res["registrar"] == "GoDaddy"

# ==========================================
# 3. HiringWorkflowAnalyzer Tests
# ==========================================
def test_workflow_stages_detection():
    text = "Apply on our portal, complete the online test, then attend the technical round. Selected candidates get joining next month."
    stages = HiringWorkflowAnalyzer.detect_stages(text)
    stage_names = [s[0] for s in stages]
    assert "Application" in stage_names
    assert "Online Assessment" in stage_names
    assert "Technical Interview" in stage_names
    assert "Joining" in stage_names

def test_workflow_risks_detection():
    text = "Pay a training fee of 5000. Get direct selection without interview."
    risks = HiringWorkflowAnalyzer.detect_risks(text)
    risk_names = [r[0] for r in risks]
    assert "Pay Fee" in risk_names
    assert "No Interview" in risk_names

def test_workflow_logic_evaluation():
    # Good timeline
    res1 = HiringWorkflowAnalyzer.analyze_workflow(
        "First step: Apply with resume. Attend technical interview and HR interview. Receive offer letter and join."
    )
    assert res1["score"] >= 90
    assert res1["type"] == "Good"
    assert "Interview" in res1["diagram"]

    # Risky timeline (payment request)
    res2 = HiringWorkflowAnalyzer.analyze_workflow(
        "Submit resume. Pay registration fee deposit. Start training onboarding."
    )
    assert res2["score"] <= 50
    assert res2["type"] == "Risky"

# ==========================================
# 4. CompanyVerifier Tests
# ==========================================
def test_company_verification_status():
    # Verified: MX records valid, website verified, old domain
    email_data = {"sender_email": "recruiter@corp.com", "verification_status": "Verified", "is_free_email": False}
    website_data = {
        "dns": {"resolves": True},
        "ssl": {"has_valid_ssl": True},
        "whois": {"whois_failed": False, "domain_age_days": 2000},
        "has_linkedin": True, "has_privacy_policy": True, "has_terms_conditions": True, "has_careers": True
    }
    status, panel = CompanyVerifier.verify_company(email_data, website_data)
    assert status == "Verified"
    assert panel["Corporate Email"] == "Verified"
    assert panel["Website"] == "Verified"
    assert panel["SSL"] == "Valid"
    assert panel["Domain Age"] == "5 Years"

    # Partially Verified: public email address but site is good
    email_data_free = {"sender_email": "recruiter@gmail.com", "verification_status": "Unknown", "is_free_email": True}
    status_free, panel_free = CompanyVerifier.verify_company(email_data_free, website_data)
    assert status_free == "Partially Verified"
    assert panel_free["Corporate Email"] == "Unknown"

# ==========================================
# 5. ConfidenceCalculator Tests
# ==========================================
def test_input_quality_score_weights():
    # Full info text
    full_text = (
        "We are looking for a Software Engineer at Google. Location: Remote. Salary: 12 LPA. "
        "Responsibilities include designing code. Requirements: Python experience. "
        "Benefits: Health insurance. The hiring process will involve an interview. "
        "Contact: hiring@google.com. Website: www.google.com. Google is a leading tech firm."
    )
    score, missing = ConfidenceCalculator.calculate_input_quality(full_text, has_email=True, has_url=True)
    assert score == 100
    assert len(missing) == 0

    # Minimal text
    short_text = "Hiring developers immediately. Call now."
    score_short, missing_short = ConfidenceCalculator.calculate_input_quality(short_text, has_email=False, has_url=False)
    assert score_short < 50
    assert "Salary Details" in missing_short

def test_confidence_vs_trust_separation():
    # Missing website should decrease confidence, not trust
    email_data = {"sender_email": "recruiter@google.com", "verification_status": "Verified", "is_free_email": False}
    
    # Confidence calculation with missing site
    conf = ConfidenceCalculator.calculate_confidence(
        text="Software engineer role available at Google. Requirements: Python.",
        email_data=email_data,
        website_data=None, # Website is missing
        ocr_performed=False,
        missing_info=["Website URL"],
        agreement_score=100
    )
    assert conf < 70 # Confidence is reduced due to missing footprint elements

# ==========================================
# 6. RiskScorer & RecommendationEngine Tests
# ==========================================
def test_trust_score_ranges_and_recommendations():
    # Positive signals setup
    positives = [
        {"id": "verified_corporate_email", "score": 5, "evidence_type": "positive"},
        {"id": "valid_ssl_certificate", "score": 10, "evidence_type": "positive"},
        {"id": "established_domain", "score": 10, "evidence_type": "positive"}
    ]
    negatives = []
    
    trust, prob, cat, agreement, explanation = RiskScorer.calculate_risk(
        evidence_list=negatives,
        positive_findings=positives,
        ai_classification={"overall_risk": "Safe"},
        is_verified_employer=True
    )
    # Calibrated trust check
    assert trust >= 95
    assert cat == "Safe"

    # Contextual Recommendations check
    recs = RecommendationEngine.generate_recommendations(
        evidence_list=negatives,
        positive_findings=positives,
        verification_status={"Website": "Verified", "Corporate Email": "Verified"}
    )
    assert len(recs) > 0
    # No warnings since there are no risks
    assert "Never pay" not in recs[0]
