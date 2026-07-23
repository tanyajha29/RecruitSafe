import pytest
from app.services.fusion.fusion_engine import (
    DecisionFusionEngine, DecisionFusionConfig, RuleScorer,
    VerificationScorer, VerdictMapper, ConfidenceCalculator,
    RecommendationCompiler, FusionOutput
)

def test_config_loader():
    """Verify config model parses and exposes scoring settings correctly."""
    config = DecisionFusionConfig.load_from_file()
    assert config.rule_weight == 0.40
    assert config.verification_weight == 0.35
    assert config.ml_weight == 0.25
    assert config.verdict_boundaries.safe == 20
    assert config.verification_deductions.ssl_invalid == 15
    assert config.confidence_parameters.agreement_boost == 15.0

def test_rule_scorer():
    """Verify RuleScorer calculates scam index from negative rule matched weights."""
    # Test valid threat rules
    rules = [
        {"title": "Registration Fee Required", "score": -50},
        {"title": "WhatsApp Contact", "score": -40},
        {"title": "Positive Legitimacy Sign", "score": 10}
    ]
    score, reasons = RuleScorer.calculate(rules)
    assert score == 90
    assert "Registration Fee Required" in reasons
    assert "WhatsApp Contact" in reasons
    assert "Positive Legitimacy Sign" not in reasons

    # Test invalid inputs
    score, reasons = RuleScorer.calculate(None)
    assert score == 0
    assert len(reasons) == 0

def test_verification_scorer():
    """Verify VerificationScorer applies deductions from configuration settings."""
    config = DecisionFusionConfig.load_from_file().verification_deductions
    verif = {
        "Corporate Email": "Disposable",
        "Website": "Unreachable",
        "DNS": "Unreachable",
        "SSL": "Invalid",
        "WHOIS": "Not Found",
        "LinkedIn": "Not Found",
        "Domain Age": "Unknown"
    }
    score, reasons = VerificationScorer.calculate(verif, config)
    # Deductions: Email(30) + Website(20) + DNS(15) + SSL(15) + WHOIS(15) + Age(5) + LinkedIn(5) = 105 -> Clamped to 100
    assert score == 100
    assert "Corporate Email validation returned 'Disposable'" in reasons
    assert "Website crawled content is missing standard 'LinkedIn' links" in reasons

    # Test invalid inputs
    score, reasons = VerificationScorer.calculate(None, config)
    assert score == 0
    assert len(reasons) == 0

def test_verdict_mapper():
    """Verify VerdictMapper maps risk categories matching configured boundaries."""
    boundaries = DecisionFusionConfig.load_from_file().verdict_boundaries
    
    assert VerdictMapper.map_score_to_verdict(10, boundaries) == "SAFE"
    assert VerdictMapper.map_score_to_verdict(25, boundaries) == "SUSPICIOUS"
    assert VerdictMapper.map_score_to_verdict(60, boundaries) == "HIGH_RISK"
    assert VerdictMapper.map_score_to_verdict(85, boundaries) == "SCAM"

def test_confidence_calculator():
    """Verify ConfidenceCalculator evaluates field completeness and agreement bounds."""
    params = DecisionFusionConfig.load_from_file().confidence_parameters
    entities = {
        "company_name": {"value": "Acme Corp"},
        "job_title": {"value": "Software Engineer"},
        "salary": {"value": "Unknown"}
    }
    
    # Agreement boost triggered (Rule and ML both low)
    conf = ConfidenceCalculator.calculate(entities, rule_score=10, ml_score=10, params=params)
    # 2/11 filled fields = 18.18% * 0.7 = 12.7 + 15 (boost) = 27.7 -> Clamped to min_confidence (50.0)
    assert conf == 50.0

    # High completeness
    all_entities = {f: {"value": "Valid"} for f in ["company_name", "job_title", "salary", "location", "employment_type", "recruiter_email", "website", "skills", "benefits", "hiring_steps", "experience"]}
    conf_high = ConfidenceCalculator.calculate(all_entities, rule_score=90, ml_score=90, params=params)
    # 11/11 filled fields = 100% * 0.7 = 70.0 + 15 (boost) = 85.0
    assert conf_high == 85.0

def test_recommendation_compiler():
    """Verify compile method aggregates correct warnings and guarantees at least 3 actions under risk."""
    actions = RecommendationCompiler.compile(
        rule_reasons=["Registration Fee"],
        verif_reasons=["Disposable Email"],
        rule_deductions=50,
        verif_deductions=30,
        ml_prediction=0,
        negative_rules=[{"id": "registration_fee", "score": -50}],
        corp_email_status="Disposable",
        website_status="Verified"
    )
    # Should include upfront payments action, corporate email warnings, and pad to 3
    assert len(actions) >= 3
    assert "Do not make upfront payments for registrations, certifications, or laptop setups." in actions

def test_fusion_output_dict_backwards_compatibility():
    """Verify Pydantic model serialization returns expected backwards compatible schemas."""
    canonical_entities = {"company_name": {"value": "Acme Corp"}}
    rules = [{"title": "Payment Requested", "score": -50}]
    verif = {"Corporate Email": "Disposable", "Website": "Verified"}
    
    res = DecisionFusionEngine.fuse_decision(
        canonical_entities=canonical_entities,
        rule_engine_result=rules,
        verification_result=verif,
        ml_prediction=1,
        ml_probability=0.95
    )

    assert isinstance(res, dict)
    assert "final_risk_score" in res
    assert "final_verdict" in res
    assert "confidence" in res
    assert "decision_breakdown" in res
    assert res["decision_breakdown"]["rule_engine"]["score"] == 50
