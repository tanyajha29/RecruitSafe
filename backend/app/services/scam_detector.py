import logging
from typing import List, Dict, Tuple, Any
from app.services.rules.pipeline import RuleExecutionPipeline
from app.services.rules.registry import default_registry

logger = logging.getLogger("recruitsafe")

# Backwards compatibility RULES mapping derived dynamically from RuleRegistry
RULES = {}
for rule in default_registry.get_all_rules():
    RULES.setdefault(rule.category, []).append({
        "id": rule.rule_id,
        "name": rule.name,
        "description": rule.description,
        "score": rule.get_weight(),
        "severity": rule.severity,
        "explanation": rule.get_explanation()
    })

class ScamRuleEngine:
    @staticmethod
    def analyze_text(text: str, structured_evidence: Dict[str, Any] = None) -> Tuple[List[Dict], List[Dict], int]:
        """
        Scans a job description or email text for exact match rules via the modular RuleExecutionPipeline.
        Each match registers independently.
        Returns:
            evidence: List of dictionaries matching the V2 extended Evidence schema
            red_flags: List of matching red flags {title, description, severity}
            total_deductions: Sum of points to deduct (represented as positive value for scorer input)
        """
        pipeline = RuleExecutionPipeline(default_registry)
        evidence_list, red_flags_list, total_deductions, _ = pipeline.execute(
            text=text,
            structured_evidence=structured_evidence
        )
        return evidence_list, red_flags_list, total_deductions
