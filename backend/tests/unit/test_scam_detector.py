import pytest

from app.services.scam_detector import ScamRuleEngine
from app.services.risk_scorer import RiskScorer

def test_safe_job_description_no_matches():
    """
    Verifies that a standard job description triggers zero rules
    and yields a perfect Safe score.
    """
    text = (
        "We are looking for a Senior Software Engineer to join our engineering department. "
        "Requirements: 5+ years experience in Python, experience with FastAPI, SQL databases, "
        "and cloud platforms (AWS). Benefits: Health insurance, 401(k), paid time off."
    )
    
    evidence, red_flags, deductions = ScamRuleEngine.analyze_text(text)
    assert len(evidence) == 0
    assert len(red_flags) == 0
    assert deductions == 0
    
    score, prob, category = RiskScorer.calculate_risk(deductions)
    assert score == 100
    assert prob == 0.0
    assert category == "Safe"

def test_scam_financial_fraud_matches():
    """
    Verifies that financial requests (e.g. training fee) are correctly flagged
    and deduct points appropriately.
    """
    text = (
        "Join ABC Technologies! Software Developer internship role. "
        "Kindly note that there is a mandatory training fee of Rs 5000 required before onboarding. "
        "Please send your resume to our hiring team."
    )
    
    evidence, red_flags, deductions = ScamRuleEngine.analyze_text(text)
    assert len(evidence) == 1
    assert evidence[0]["category"] == "financial_fraud"
    assert evidence[0]["points_deducted"] == 20
    assert deductions == 20
    
    score, prob, category = RiskScorer.calculate_risk(deductions)
    assert score == 80
    assert prob == 20.0
    assert category == "Safe" # still safe at exactly 80

def test_multiple_scam_patterns():
    """
    Verifies that multiple scam indicators (financial request, identity document,
    unrealistic salary, and urgency pressure) compound and result in a High Risk verdict.
    """
    text = (
        "Urgent job opening for a fresher! Earn ₹3 lakh/month remote work from home! "
        "Guaranteed job placement with direct selection and no interview. "
        "To register, email your pan card scan and bank details to hr-care-recruits@gmail.com "
        "and pay the registration fee of ₹2500 within 30 minutes! Only today!"
    )
    
    evidence, red_flags, deductions = ScamRuleEngine.analyze_text(text)
    
    # Check that we caught multiple indicators
    rule_ids = [e["factor_name"] for e in evidence]
    assert any("Registration Fee" in name for name in rule_ids)
    assert any("Identity Document" in name for name in rule_ids)
    assert any("Direct Hiring" in name for name in rule_ids)
    assert any("Urgent" in name for name in rule_ids)
    assert any("Public Domain Recruiter" in name for name in rule_ids)
    
    assert deductions > 50
    
    score, prob, category = RiskScorer.calculate_risk(deductions)
    assert score < 40
    assert prob > 60.0
    assert category == "High Risk"

def test_risk_scorer_boundaries():
    """
    Verifies that Trust Score ranges are mapped to correct Risk Categories.
    """
    # Safe boundary
    assert RiskScorer.calculate_risk(10) == (90, 10.0, "Safe")
    assert RiskScorer.calculate_risk(20) == (80, 20.0, "Safe")
    
    # Needs Verification boundary
    assert RiskScorer.calculate_risk(21) == (79, 21.0, "Needs Verification")
    assert RiskScorer.calculate_risk(40) == (60, 40.0, "Needs Verification")
    
    # Suspicious boundary
    assert RiskScorer.calculate_risk(41) == (59, 41.0, "Suspicious")
    assert RiskScorer.calculate_risk(60) == (40, 60.0, "Suspicious")
    
    # High Risk boundary
    assert RiskScorer.calculate_risk(61) == (39, 61.0, "High Risk")
    assert RiskScorer.calculate_risk(120) == (0, 100.0, "High Risk") # clamped
