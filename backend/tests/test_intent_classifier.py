import pytest
from app.services.nlp.nlp_service import NLPService
from app.services.nlp.context_analyzer import ContextAnalyzer
from app.services.nlp.intent_classifier import IntentClassifier, SeverityCalculator, RuleScoreMapper
from app.services.rules.registry import RuleRegistry
from app.services.rules.builtin_rules import RegexPatternRule

def test_intent_classification_scenarios():
    nlp = NLPService()

    # Rule mock setups (Payment and Telegram/WhatsApp)
    payment_rule = RegexPatternRule(
        rule_id="registration_fee",
        name="Registration Fee Requested",
        description="The job description requests a registration, application, or processing fee to apply or secure a spot.",
        category="financial_fraud",
        severity="high",
        weight_key="payment_request",
        default_weight=-50,
        keywords=[r"\bfee\b", r"\bpay\b"]
    )
    
    telegram_rule = RegexPatternRule(
        rule_id="telegram_only",
        name="Telegram-Only Recruiter Contact",
        description="Recruiter directs candidates to communicate exclusively via Telegram channels.",
        category="contact_anomalies",
        severity="medium",
        weight_key="telegram_only",
        default_weight=-40,
        keywords=[r"\btelegram\b"]
    )

    # Example 1: Pay INR 500 before interview.
    text1 = "Pay INR 500 registration fee before interview."
    res1 = payment_rule.evaluate(text1)
    print("\n\n=== Example 1 Output ===")
    print(f"Rule ID: {res1.rule_id} | Triggered: {res1.triggered}")
    print(f"Intent: {res1.intent} | Severity: {res1.severity} | Score: {res1.weight}")
    assert res1.triggered
    assert res1.intent == "MANDATORY_PAYMENT"
    assert res1.severity == "HIGH"
    assert res1.weight == -40

    # Example 2: Optional paid certification.
    text2 = "Optional paid certification."
    # Since certification is in TRAINING phrases, let's create a training rule to match it
    training_rule = RegexPatternRule(
        rule_id="training_fee",
        name="Training Fee Required",
        description="Requests payment for training materials.",
        category="financial_fraud",
        severity="high",
        weight_key="payment_request",
        default_weight=-50,
        keywords=[r"\bcertification\b"]
    )
    res2 = training_rule.evaluate(text2)
    print("\n=== Example 2 Output ===")
    print(f"Intent: {res2.intent} | Severity: {res2.severity} | Score: {res2.weight}")
    assert res2.triggered
    assert res2.intent == "OPTIONAL_TRAINING"
    assert res2.severity == "LOW"
    assert res2.weight == -5

    # Example 3: Certification cost reimbursed after joining.
    text3 = "Certification cost reimbursed after joining."
    res3 = training_rule.evaluate(text3)
    print("\n=== Example 3 Output ===")
    print(f"Intent: {res3.intent} | Severity: {res3.severity} | Score: {res3.weight}")
    assert res3.triggered
    assert res3.intent == "COMPANY_REIMBURSEMENT"
    assert res3.severity == "NONE"
    assert res3.weight == 0

    # Example 4: Contact us only through Telegram.
    text4 = "Contact us only through Telegram."
    res4 = telegram_rule.evaluate(text4)
    print("\n=== Example 4 Output ===")
    print(f"Intent: {res4.intent} | Severity: {res4.severity} | Score: {res4.weight}")
    assert res4.triggered
    assert res4.intent == "MANDATORY_COMMUNICATION"
    assert res4.severity == "HIGH"
    assert res4.weight == -40

    # Example 5: Telegram is also available.
    text5 = "Telegram is also available."
    res5 = telegram_rule.evaluate(text5)
    print("\n=== Example 5 Output ===")
    print(f"Intent: {res5.intent} | Severity: {res5.severity} | Score: {res5.weight}")
    assert res5.triggered
    assert res5.intent == "OPTIONAL_COMMUNICATION"
    assert res5.severity == "NONE"
    assert res5.weight == 0

if __name__ == "__main__":
    test_intent_classification_scenarios()
