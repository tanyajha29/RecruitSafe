from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class RuleResult:
    """
    Represents the output of evaluating a single rule.
    """
    rule_id: str
    rule_name: str
    triggered: bool
    category: str
    severity: str
    weight: int
    matched_text: str = ""
    explanation: str = ""
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    intent: Optional[str] = None
    dynamic_score: Optional[int] = None
    context_summary: Optional[str] = None
    confidence: Optional[float] = None

class BaseRule(ABC):
    """
    Abstract base class for all detection rules in RecruitSafe.
    Rule logic is independent, modular, and self-contained.
    """
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        category: str,
        severity: str,
        weight_key: str,
        default_weight: int,
        explanation: str = ""
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.category = category
        self.severity = severity
        self.weight_key = weight_key
        self.default_weight = default_weight
        self.custom_explanation = explanation

    def get_weight(self) -> int:
        from app.services.rules_config import RULE_WEIGHTS
        return RULE_WEIGHTS.get(self.weight_key, self.default_weight)

    def get_explanation(self) -> str:
        from app.services.rules_config import RULE_EXPLANATIONS
        if self.custom_explanation:
            return self.custom_explanation
        return RULE_EXPLANATIONS.get(self.weight_key, "")

    @abstractmethod
    def evaluate(
        self,
        text: str,
        structured_evidence: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RuleResult:
        """
        Evaluates the rule against the raw input text, structured evidence, or context.
        Returns a RuleResult object indicating whether the rule triggered.
        """
        pass
