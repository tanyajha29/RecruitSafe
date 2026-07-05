import pytest
from app.services.salary_analyzer import SalaryAnalyzer
from app.services.hiring_process import HiringProcessValidator
from app.services.psych_manipulation import PsychologicalDetector
from app.services.identity_theft import IdentityTheftDetector
from app.services.contradiction_detector import ContradictionDetector
from app.services.confidence_calculator import ConfidenceCalculator
from app.services.risk_scorer import RiskScorer
from app.services.recommendation_engine import RecommendationEngine

def test_salary_analyzer():
    # Case 1: Unrealistic fresher salary (₹2L/month)
    text_scam = "We are hiring freshers for trainee role. Earn ₹2,00,000 per month immediately."
    res_scam = SalaryAnalyzer.analyze_salary(text_scam)
    assert len(res_scam["evidence"]) == 1
    assert res_scam["evidence"][0]["id"] == "unrealistic_fresher_salary"
    assert res_scam["evidence"][0]["score"] == -25

    # Case 2: Normal senior salary (₹25 LPA)
    text_senior = "Looking for Senior Developer with 7 years experience. Offered salary is 25 LPA."
    res_senior = SalaryAnalyzer.analyze_salary(text_senior)
    assert len(res_senior["positive_findings"]) == 1
    assert res_senior["positive_findings"][0]["id"] == "realistic_senior_salary"
    assert res_senior["positive_findings"][0]["score"] == 5

    # Case 3: Normal junior salary (₹4 LPA)
    text_junior = "Junior intern opening for fresher. Stipend 4 Lakhs per annum."
    res_junior = SalaryAnalyzer.analyze_salary(text_junior)
    assert len(res_junior["positive_findings"]) == 1
    assert res_junior["positive_findings"][0]["id"] == "realistic_fresher_salary"

def test_hiring_process_validator():
    # Case 1: Structured funnel
    text_good = "Process: apply via link, clear coding assessment, attend technical panel interview, HR round, and receive offer letter."
    res_good = HiringProcessValidator.validate_process(text_good)
    assert len(res_good["positive_findings"]) == 1
    assert res_good["positive_findings"][0]["id"] == "structured_hiring_funnel"

    # Case 2: Shortcut hiring
    text_bad = "No interview required. Direct selection and spot joining. Just pay the deposit."
    res_bad = HiringProcessValidator.validate_process(text_bad)
    assert len(res_bad["evidence"]) == 1
    assert res_bad["evidence"][0]["id"] == "direct_joining_no_interview"

def test_psychological_detector():
    # Case 1: Urgency & Pressure
    text_manip = "Apply immediately! Only today! Limited seats filling fast! 100% placement guaranteed! Guaranteed job selection."
    res = PsychologicalDetector.analyze_manipulation(text_manip)
    assert res["urgency_score"] >= 50
    assert res["pressure_score"] >= 50
    assert len(res["evidence"]) == 2

def test_identity_theft_detector():
    # Case 1: Upfront document harvesting
    text_upfront = "To apply for registration, send your Aadhaar copy and bank account details."
    res_upfront = IdentityTheftDetector.analyze_identity_requests(text_upfront)
    assert len(res_upfront["evidence"]) == 2
    assert any(e["id"] == "upfront_aadhaar_request" for e in res_upfront["evidence"])
    assert any(e["id"] == "upfront_bank_details_request" for e in res_upfront["evidence"])

    # Case 2: Onboarding context (safe)
    text_onboard = "Selected candidates will undergo background check. Aadhaar details are required during onboarding after offer acceptance."
    res_onboard = IdentityTheftDetector.analyze_identity_requests(text_onboard)
    assert len(res_onboard["evidence"]) == 0

def test_contradiction_detector():
    # Case 1: Corporate claims vs brand new domain
    website_data = {
        "whois": {"domain_age_days": 12, "whois_failed": False},
        "ssl": {"has_valid_ssl": True}
    }
    text_contr = "We are an established multinational ISO certified corporation."
    res = ContradictionDetector.detect_contradictions(text_contr, None, website_data)
    assert len(res["contradictions"]) == 1
    assert res["evidence"][0]["id"] == "claim_vs_domain_age_contradiction"

def test_confidence_and_override():
    # Case 1: Low quality input -> Missing info override
    short_text = "Hiring freshers. Apply now."
    missing = ConfidenceCalculator.detect_missing_information(short_text, False, False)
    # Missing role name, company reference, contact info, salary info
    assert len(missing) >= 3
    
    confidence = ConfidenceCalculator.calculate_confidence(short_text, None, None, False, missing)
    assert confidence < 40

    # Risk Scorer overrides
    trust, scam, cat, agreement = RiskScorer.calculate_risk(
        evidence_list=[],
        positive_findings=[],
        ai_classification={"overall_risk": "Safe"},
        confidence_score=confidence,
        missing_info=missing
    )
    assert cat == "Review Required"

def test_dynamic_recommendations():
    evidence = [
        {"id": "registration_fee", "score": -25, "category": "financial_fraud"},
        {"id": "upfront_otp_request", "score": -30, "category": "identity_theft"}
    ]
    positives = []
    recs = RecommendationEngine.generate_recommendations(evidence, positives)
    assert any("registration" in r.lower() for r in recs)
    assert any("otp" in r.lower() for r in recs)
