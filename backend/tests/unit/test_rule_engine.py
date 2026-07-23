import os
import pytest
from app.services.rules.base_rule import BaseRule, RuleResult
from app.services.rules.builtin_rules import RegexPatternRule, PoorGrammarRule, MissingCompanyNameRule
from app.services.rules.registry import RuleRegistry, default_registry
from app.services.rules.pipeline import RuleExecutionPipeline
from app.services.scam_detector import ScamRuleEngine

class CustomTestRule(BaseRule):
    """Custom rule class for testing extensibility."""
    def __init__(self, rule_id: str = "custom_test_rule"):
        super().__init__(
            rule_id=rule_id,
            name="Custom Test Rule",
            description="Rule used strictly for unit testing framework extensibility.",
            category="testing",
            severity="low",
            weight_key="custom_test_key",
            default_weight=-15,
            explanation="Custom test explanation."
        )

    def evaluate(self, text: str, structured_evidence=None, context=None) -> RuleResult:
        if text and "custom_trigger" in text.lower():
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                triggered=True,
                category=self.category,
                severity=self.severity,
                weight=self.get_weight(),
                matched_text="custom_trigger",
                explanation=self.get_explanation(),
                description=self.description
            )
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            triggered=False,
            category=self.category,
            severity=self.severity,
            weight=self.get_weight(),
            explanation=self.get_explanation(),
            description=self.description
        )

def test_rule_registry_operations():
    """Tests registering, retrieving, filtering, and unregistering rules in RuleRegistry."""
    registry = RuleRegistry()
    assert len(registry.get_all_rules()) == 0

    rule1 = CustomTestRule("rule_1")
    rule2 = CustomTestRule("rule_2")
    
    registry.register(rule1)
    registry.register(rule2)
    assert len(registry.get_all_rules()) == 2
    assert registry.get_rule("rule_1") == rule1

    rules_testing = registry.get_rules_by_category("testing")
    assert len(rules_testing) == 2

    assert registry.unregister("rule_1") is True
    assert len(registry.get_all_rules()) == 1
    assert registry.get_rule("rule_1") is None

    registry.clear()
    assert len(registry.get_all_rules()) == 0

def test_regex_pattern_rule_evaluation():
    """Tests RegexPatternRule matching and result fields."""
    rule = RegexPatternRule(
        rule_id="test_payment",
        name="Test Payment Rule",
        description="Detects registration fee requests.",
        category="financial_fraud",
        severity="high",
        weight_key="payment_request",
        default_weight=-50,
        keywords=[r"\bregistration\s*fee\b"]
    )

    res_negative = rule.evaluate("Standard job posting with no fees.")
    assert res_negative.triggered is False

    res_positive = rule.evaluate("Please pay the registration fee of $50 to apply.")
    assert res_positive.triggered is True
    assert res_positive.rule_id == "test_payment"
    assert res_positive.category == "financial_fraud"
    assert res_positive.severity == "high"
    assert res_positive.weight == -50
    assert "registration fee" in res_positive.matched_text.lower()

def test_poor_grammar_and_missing_company_rules():
    """Tests specialized built-in rules (PoorGrammarRule and MissingCompanyNameRule)."""
    grammar_rule = PoorGrammarRule()
    assert grammar_rule.evaluate("Normal text").triggered is False
    assert grammar_rule.evaluate("Text with  double spaces").triggered is True
    assert grammar_rule.evaluate("Dear jobseeker, welcome!").triggered is True

    company_rule = MissingCompanyNameRule()
    assert company_rule.evaluate("Text", {"Company Name": {"value": "Acme Inc", "extraction_status": "extracted"}}).triggered is False
    assert company_rule.evaluate("Text", {"Company Name": {"value": "Unknown", "extraction_status": "not_found"}}).triggered is True

def test_json_config_loading():
    """Tests loading rule configurations dynamically from rules_config.json."""
    registry = RuleRegistry()
    count = registry.load_from_config()
    assert count > 10
    
    reg_fee_rule = registry.get_rule("registration_fee")
    assert reg_fee_rule is not None
    assert reg_fee_rule.category == "financial_fraud"
    assert reg_fee_rule.severity == "high"
    assert reg_fee_rule.get_weight() == -50

def test_rule_execution_pipeline_and_trace_logs():
    """Tests executing pipeline and generating detailed per-rule trace logs."""
    pipeline = RuleExecutionPipeline(default_registry)
    scam_text = "Urgent opening! Pay registration fee of Rs. 1000 via WhatsApp wa.me/919999999999 within 30 minutes!"
    
    evidence, red_flags, deductions, trace_logs = pipeline.execute(scam_text)
    
    assert deductions > 0
    assert len(evidence) >= 3
    assert len(red_flags) >= 3
    assert len(trace_logs) == len(default_registry.get_all_rules())

    # Check trace record keys
    for log_rec in trace_logs:
        assert "rule_id" in log_rec
        assert "name" in log_rec
        assert "triggered" in log_rec
        assert "latency_ms" in log_rec

def test_scam_rule_engine_backwards_compatibility():
    """Ensures ScamRuleEngine.analyze_text maintains backwards compatibility."""
    text = "Mandatory training fee of Rs 5000 required before onboarding."
    evidence, red_flags, deductions = ScamRuleEngine.analyze_text(text)
    
    assert deductions == 40
    assert len(evidence) == 1
    assert evidence[0]["id"] == "training_fee"
    assert evidence[0]["weight"] == -40
    assert len(red_flags) == 1
