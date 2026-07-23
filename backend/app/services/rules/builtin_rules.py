import re
import logging
from typing import List, Dict, Any, Optional
from app.services.rules.base_rule import BaseRule, RuleResult

logger = logging.getLogger("recruitsafe")

class RegexPatternRule(BaseRule):
    """
    Extensible rule evaluating regular expression keyword patterns against input text.
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
        keywords: List[str],
        explanation: str = ""
    ):
        super().__init__(
            rule_id=rule_id,
            name=name,
            description=description,
            category=category,
            severity=severity,
            weight_key=weight_key,
            default_weight=default_weight,
            explanation=explanation
        )
        self.keywords = keywords
        self.compiled_patterns = [re.compile(pat, re.IGNORECASE) for pat in keywords]

    def evaluate(
        self,
        text: str,
        structured_evidence: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RuleResult:
        if not text:
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

        context_aware_rules = {
            "payment", "registration_fee", "training_fee", "paid_certification",
            "telegram_only", "whatsapp_only", "telegram", "whatsapp",
            "no_interview", "guaranteed_placement", "urgency_urg"
        }

        for pattern in self.compiled_patterns:
            match = pattern.search(text)
            if match:
                # 1. Base legacy details
                matched_text = match.group(0)
                final_severity = self.severity
                final_weight = self.get_weight()
                final_desc = self.description
                final_expl = self.get_explanation()
                
                intent_val = None
                dynamic_score_val = None
                context_summary_val = None
                confidence_val = None

                # 2. Context-aware overrides
                if self.rule_id in context_aware_rules:
                    try:
                        from app.services.nlp.nlp_service import NLPService
                        from app.services.nlp.context_analyzer import ContextAnalyzer
                        from app.services.nlp.intent_classifier import IntentClassifier, SeverityCalculator, RuleScoreMapper
                        
                        nlp = NLPService()
                        doc = nlp.analyze(text)
                        
                        # Find the spaCy span corresponding to the regex match character bounds
                        span = doc.char_span(match.start(), match.end(), alignment_mode="expand")
                        if span is not None:
                            context_meta = ContextAnalyzer.analyze_context(doc, span)
                            intent_val = IntentClassifier.classify(context_meta)
                            final_severity = SeverityCalculator.calculate(intent_val)
                            dynamic_score_val = RuleScoreMapper.map_severity_to_score(final_severity)
                            final_weight = -dynamic_score_val
                            
                            # Custom descriptions and explanations based on intent
                            if intent_val == "MANDATORY_PAYMENT":
                                final_desc = "Mandatory upfront payment requested before the interview."
                                final_expl = "This is a high-risk scam pattern. Never pay registration or processing fees to secure a job interview."
                            elif intent_val == "OPTIONAL_TRAINING":
                                final_desc = "Optional paid certification or training course detected."
                                final_expl = "The surrounding language indicates participation is optional rather than mandatory. Verify whether the training provider is officially affiliated with the employer."
                            elif intent_val == "COMPANY_REIMBURSEMENT":
                                final_desc = "Upfront cost reimbursed by the company."
                                final_expl = "The employer indicates certification or training fees will be paid back upon joining. Confirm this policy during official interview channels."
                            elif intent_val == "MANDATORY_TRAINING":
                                final_desc = "Mandatory paid training required before candidate onboarding."
                                final_expl = "Verify credentials and training providers independently before committing to any upfront expenses."
                            elif intent_val == "MANDATORY_COMMUNICATION":
                                final_desc = "Mandatory communication requested exclusively through personal chat platforms."
                                final_expl = "Recruiter requests communication solely on Telegram/WhatsApp, which prevents official candidate verification."
                            elif intent_val == "OPTIONAL_COMMUNICATION":
                                final_desc = "Optional personal chat application link provided."
                                final_expl = "The channel is offered for general inquiries but is not mandatory."

                            context_summary_val = context_meta.sentence
                            confidence_val = 0.95

                            # Add logging
                            logger.info(
                                f"Context-Aware Match Triggered | Rule ID: {self.rule_id} | "
                                f"Intent: {intent_val} | Severity: {final_severity} | "
                                f"Dynamic Score: {final_weight} | Confidence: {confidence_val} | "
                                f"Context Summary: {context_summary_val}"
                            )
                    except Exception as e:
                        logger.error(f"Failed parsing context-aware metadata for rule '{self.rule_id}': {e}", exc_info=True)

                return RuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    triggered=True,
                    category=self.category,
                    severity=final_severity,
                    weight=final_weight,
                    matched_text=matched_text,
                    explanation=final_expl,
                    description=final_desc,
                    intent=intent_val,
                    dynamic_score=-dynamic_score_val if dynamic_score_val is not None else None,
                    context_summary=context_summary_val,
                    confidence=confidence_val
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

class PoorGrammarRule(BaseRule):
    """
    Evaluates heuristic formatting and styling anomalies in raw posting text.
    """
    def __init__(self):
        super().__init__(
            rule_id="poor_grammar",
            name="Poor Grammar and Formatting",
            description="Job posting text contains systemic grammatical errors and spelling anomalies.",
            category="pressure_tactics",
            severity="low",
            weight_key="poor_grammar",
            default_weight=-10
        )

    def evaluate(
        self,
        text: str,
        structured_evidence: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RuleResult:
        if not text:
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

        text_lower = text.lower()
        if "  " in text or "dear jobseeker" in text_lower:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                triggered=True,
                category=self.category,
                severity=self.severity,
                weight=self.get_weight(),
                matched_text="Grammatical styling issues",
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

class MissingCompanyNameRule(BaseRule):
    """
    Evaluates missing corporate identity from structured extraction evidence.
    """
    def __init__(self):
        super().__init__(
            rule_id="no_company_name",
            name="No Company Name Specified",
            description="Employer name is omitted or anonymous, preventing standard candidate checks.",
            category="identity_theft",
            severity="medium",
            weight_key="no_company_name",
            default_weight=-20
        )

    def evaluate(
        self,
        text: str,
        structured_evidence: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RuleResult:
        if structured_evidence:
            company_detail = structured_evidence.get("Company Name", {})
            val = company_detail.get("value")
            status = company_detail.get("extraction_status")
            if val == "Unknown" or status == "not_found":
                return RuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    triggered=True,
                    category=self.category,
                    severity=self.severity,
                    weight=self.get_weight(),
                    matched_text="Company name is empty or unknown",
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
