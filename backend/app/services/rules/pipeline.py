import time
import logging
from typing import Dict, List, Tuple, Any, Optional
from pydantic import BaseModel, Field

from app.services.rules.registry import RuleRegistry, default_registry
from app.services.rules.base_rule import RuleResult

logger = logging.getLogger("recruitsafe")

# --- Dictionary-Like Backward Compatibility Base Model ---

class DictCompatibleBaseModel(BaseModel):
    """
    Subclass that provides dictionary compatibility (key lookups, get, iteration)
    to prevent breaking downstream callers expecting raw dictionaries.
    """
    def keys(self) -> Any:
        return self.model_fields.keys()

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def __contains__(self, key: str) -> bool:
        return key in self.model_fields

    def __iter__(self) -> Any:
        for key in self.model_fields.keys():
            yield key, getattr(self, key)


# --- Pydantic Data Record Schema ---

class EvidenceRecord(DictCompatibleBaseModel):
    category: str
    factor_name: str
    points_deducted: int
    severity: str
    id: str
    title: str
    score: int
    matched_text: Optional[str] = None
    explanation: Optional[str] = None
    weight: int

class RedFlagRecord(DictCompatibleBaseModel):
    title: str
    description: str
    severity: str

class RuleTraceRecord(DictCompatibleBaseModel):
    rule_id: str
    name: str
    triggered: bool
    category: str
    severity: str
    weight: int
    matched_text: Optional[str] = None
    latency_ms: float

class FailedRuleRecord(DictCompatibleBaseModel):
    rule_id: str
    error: str


# --- Core Pipeline Execution Class ---

class RuleExecutionPipeline:
    """
    Orchestrates the evaluation of registered rules against input text and evidence models.
    Provides detailed per-rule trace logging and aggregates outputs for scoring engines.
    
    Attributes:
        total_rules (int): Total count of rules registered.
        triggered_rules (int): Total count of triggered rules in execution.
        skipped_rules (int): Count of duplicate or redundant rules skipped.
        failed_rules (List[FailedRuleRecord]): List of rule evaluations that failed.
        total_execution_time_ms (float): Total execution duration in milliseconds.
    """
    def __init__(self, registry: Optional[RuleRegistry] = None):
        self.registry = registry or default_registry
        self.total_rules: int = 0
        self.triggered_rules: int = 0
        self.skipped_rules: int = 0
        self.failed_rules: List[FailedRuleRecord] = []
        self.total_execution_time_ms: float = 0.0

    def execute(
        self,
        text: str,
        structured_evidence: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[EvidenceRecord], List[RedFlagRecord], int, List[RuleTraceRecord]]:
        """
        Executes all registered rules in sequence.
        
        Args:
            text: Raw job details text to analyze.
            structured_evidence: Extracted canonical entity values.
            context: Execution context containing request_id/analysis_id for correlation tracking.

        Returns:
            evidence_list: List of typed EvidenceRecords
            red_flags_list: List of typed RedFlagRecords
            total_deductions: Sum of point deductions
            trace_logs: Per-rule execution trace log records
        """
        # Clear stats for new run
        self.total_rules = 0
        self.triggered_rules = 0
        self.skipped_rules = 0
        self.failed_rules = []
        self.total_execution_time_ms = 0.0

        # Structured context logging extract
        context = context or {}
        request_id = context.get("request_id")
        analysis_id = context.get("analysis_id")
        user_id = context.get("user_id")

        log_extra = {}
        if request_id:
            log_extra["request_id"] = request_id
        if analysis_id:
            log_extra["analysis_id"] = analysis_id
        if user_id:
            log_extra["user_id"] = user_id

        if not text and not structured_evidence:
            logger.info("RuleExecutionPipeline: Empty input received. Skipping execution.", extra=log_extra)
            return [], [], 0, []

        evidence_list: List[EvidenceRecord] = []
        red_flags_list: List[RedFlagRecord] = []
        trace_logs: List[RuleTraceRecord] = []
        total_deductions = 0
        matched_rule_ids = set()

        rules = self.registry.get_all_rules()
        self.total_rules = len(rules)
        logger.info(f"RuleExecutionPipeline starting evaluation of {self.total_rules} rules...", extra=log_extra)

        start_total = time.perf_counter()

        for rule in rules:
            # Deterministic duplicate execution prevention:
            # Iterating order is guaranteed by registry lists. Checking matched_rule_ids
            # ensures that if a duplicate rule ID is encountered, it is skipped consistently.
            if rule.rule_id in matched_rule_ids:
                self.skipped_rules += 1
                logger.debug(f"RuleExecutionPipeline: Skipping duplicate rule ID '{rule.rule_id}'", extra=log_extra)
                continue

            rule_start = time.perf_counter()
            try:
                res: RuleResult = rule.evaluate(
                    text=text,
                    structured_evidence=structured_evidence,
                    context=context
                )
            except Exception as e:
                # Capture failures for diagnostics and continue pipeline execution
                err_msg = str(e)
                logger.error(f"Error evaluating rule '{rule.rule_id}': {err_msg}", exc_info=True, extra=log_extra)
                self.failed_rules.append(FailedRuleRecord(rule_id=rule.rule_id, error=err_msg))
                continue

            latency_ms = round((time.perf_counter() - rule_start) * 1000, 3)

            # Record step trace
            trace_logs.append(RuleTraceRecord(
                rule_id=rule.rule_id,
                name=rule.name,
                triggered=res.triggered,
                category=res.category,
                severity=res.severity,
                weight=res.weight,
                matched_text=res.matched_text,
                latency_ms=latency_ms
            ))

            logger.debug(
                f"[Rule Trace] ID={rule.rule_id} | Name='{rule.name}' | Triggered={res.triggered} | "
                f"Weight={res.weight} | Latency={latency_ms}ms",
                extra=log_extra
            )

            if res.triggered:
                matched_rule_ids.add(rule.rule_id)
                self.triggered_rules += 1
                deduction = abs(res.weight)
                total_deductions += deduction

                # Evidence record
                evidence_list.append(EvidenceRecord(
                    category=res.category,
                    factor_name=res.rule_name,
                    points_deducted=deduction,
                    severity=res.severity,
                    id=res.rule_id,
                    title=res.rule_name,
                    score=res.weight,
                    matched_text=res.matched_text,
                    explanation=res.explanation,
                    weight=res.weight
                ))

                # Red Flag record
                red_flags_list.append(RedFlagRecord(
                    title=res.rule_name,
                    description=res.description,
                    severity=res.severity
                ))

        self.total_execution_time_ms = round((time.perf_counter() - start_total) * 1000, 2)
        logger.info(
            f"RuleExecutionPipeline finished evaluation in {self.total_execution_time_ms}ms. "
            f"Triggered {self.triggered_rules} rules, failed {len(self.failed_rules)}, total deductions={total_deductions}.",
            extra=log_extra
        )

        return evidence_list, red_flags_list, total_deductions, trace_logs
