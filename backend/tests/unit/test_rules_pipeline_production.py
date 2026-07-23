import pytest
from unittest.mock import MagicMock
from app.services.rules.pipeline import RuleExecutionPipeline, EvidenceRecord, RedFlagRecord, RuleTraceRecord
from app.services.rules.registry import RuleRegistry
from app.services.rules.base_rule import BaseRule, RuleResult

class MockTriggeredRule(BaseRule):
    def __init__(self, rule_id, name, category, severity, weight):
        super().__init__(
            rule_id=rule_id,
            name=name,
            description="Mock description",
            category=category,
            severity=severity,
            weight_key=f"mock_{rule_id}",
            default_weight=weight,
            explanation="Mock explanation"
        )
        self.weight = weight

    def evaluate(self, text, structured_evidence=None, context=None):
        return RuleResult(
            triggered=True,
            rule_id=self.rule_id,
            rule_name=self.name,
            category=self.category,
            severity=self.severity,
            weight=self.get_weight(),
            matched_text="Matched Mock text",
            explanation="Explanation text",
            description="Description text"
        )

class MockFailingRule(BaseRule):
    def __init__(self, rule_id, name, category, severity, weight):
        super().__init__(
            rule_id=rule_id,
            name=name,
            description="Mock description",
            category=category,
            severity=severity,
            weight_key=f"mock_{rule_id}",
            default_weight=weight,
            explanation="Mock explanation"
        )
        self.weight = weight

    def evaluate(self, text, structured_evidence=None, context=None):
        raise ValueError("Simulated rule failure exception")

def test_pipeline_normal_execution():
    """Verify normal sequence evaluation, backward compatibility dict mapping, and output schemas."""
    registry = RuleRegistry()
    registry.register(MockTriggeredRule(
        rule_id="rule_mock_01",
        name="Mock Triggered Rule",
        category="general",
        severity="medium",
        weight=-20
    ))
    
    pipeline = RuleExecutionPipeline(registry)
    evidence, flags, deductions, traces = pipeline.execute("test text context")

    assert len(evidence) == 1
    assert len(flags) == 1
    assert len(traces) == 1
    assert deductions == 20

    # Test Pydantic types
    assert isinstance(evidence[0], EvidenceRecord)
    assert isinstance(flags[0], RedFlagRecord)
    assert isinstance(traces[0], RuleTraceRecord)

    # Test backward compatibility dict-like conversion and get/contains lookups
    ev_item = evidence[0]
    assert ev_item["id"] == "rule_mock_01"
    assert ev_item.get("category") == "general"
    assert "points_deducted" in ev_item
    assert dict(ev_item)["points_deducted"] == 20

def test_pipeline_duplicate_rule_prevention():
    """Verify that duplicate rule IDs are skipped deterministically and increment skipped stats."""
    registry = RuleRegistry()
    rule1 = MockTriggeredRule(
        rule_id="duplicate_rule",
        name="Duplicate Rule",
        category="general",
        severity="low",
        weight=-5
    )
    rule2 = MockTriggeredRule(
        rule_id="duplicate_rule",
        name="Duplicate Rule",
        category="general",
        severity="low",
        weight=-5
    )
    
    # Mock registry.get_all_rules to bypass registry dict overwrites
    registry.get_all_rules = MagicMock(return_value=[rule1, rule2])

    pipeline = RuleExecutionPipeline(registry)
    evidence, flags, deductions, traces = pipeline.execute("test text")

    # Should only run and trigger once
    assert len(evidence) == 1
    assert pipeline.skipped_rules == 1
    assert pipeline.total_rules == 2
    assert pipeline.triggered_rules == 1

def test_pipeline_rule_exception_handling():
    """Verify that exceptions in a single rule are caught, logged, and registered without aborting the pipeline."""
    registry = RuleRegistry()
    registry.register(MockFailingRule(
        rule_id="failing_rule",
        name="Failing Rule",
        category="critical",
        severity="high",
        weight=-50
    ))
    registry.register(MockTriggeredRule(
        rule_id="healthy_rule",
        name="Healthy Triggered Rule",
        category="general",
        severity="low",
        weight=-5
    ))

    pipeline = RuleExecutionPipeline(registry)
    evidence, flags, deductions, traces = pipeline.execute("test text")

    # Pipeline should recover and execute the second healthy rule
    assert len(evidence) == 1
    assert deductions == 5
    assert len(pipeline.failed_rules) == 1
    assert pipeline.failed_rules[0].rule_id == "failing_rule"
    assert "Simulated rule failure exception" in pipeline.failed_rules[0].error

def test_pipeline_latency_recording():
    """Verify that execute logs overall duration and per-rule step trace durations."""
    registry = RuleRegistry()
    registry.register(MockTriggeredRule(
        rule_id="latency_rule",
        name="Latency Rule",
        category="general",
        severity="low",
        weight=-5
    ))

    pipeline = RuleExecutionPipeline(registry)
    evidence, flags, deductions, traces = pipeline.execute("test text")

    assert pipeline.total_execution_time_ms >= 0.0
    assert traces[0].latency_ms >= 0.0

def test_pipeline_empty_input_handling():
    """Verify that passing empty input skips checks and returns immediately with clean statistics."""
    pipeline = RuleExecutionPipeline()
    evidence, flags, deductions, traces = pipeline.execute("")
    
    assert len(evidence) == 0
    assert len(flags) == 0
    assert len(traces) == 0
    assert deductions == 0
    assert pipeline.total_rules == 0
    assert pipeline.triggered_rules == 0
