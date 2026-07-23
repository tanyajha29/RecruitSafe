import os
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger("recruitsafe")

# --- Configuration Models ---

class VerdictBoundaries(BaseModel):
    safe: int = 20
    suspicious: int = 50
    high_risk: int = 75

class VerificationDeductions(BaseModel):
    corp_email_invalid: int = 30
    website_unreachable: int = 20
    dns_unreachable: int = 15
    ssl_invalid: int = 15
    whois_not_found: int = 15
    domain_age_unknown: int = 5
    missing_signals: int = 5

class ConfidenceParameters(BaseModel):
    completeness_coefficient: float = 0.7
    agreement_boost: float = 15.0
    min_confidence: float = 50.0
    max_confidence: float = 100.0

class DecisionFusionConfig(BaseModel):
    rule_weight: float = 0.40
    verification_weight: float = 0.35
    ml_weight: float = 0.25
    verdict_boundaries: VerdictBoundaries = Field(default_factory=VerdictBoundaries)
    verification_deductions: VerificationDeductions = Field(default_factory=VerificationDeductions)
    confidence_parameters: ConfidenceParameters = Field(default_factory=ConfidenceParameters)

    @classmethod
    def load_from_file(cls) -> "DecisionFusionConfig":
        """Loads and parses dynamic weights and boundaries from fusion_config.json."""
        base_dir = os.path.dirname(__file__)
        config_path = os.path.abspath(os.path.join(base_dir, "..", "..", "config", "fusion_config.json"))

        if not os.path.exists(config_path):
            logger.warning(f"DecisionFusionConfig: Config file not found at {config_path}. Using default configuration.")
            return cls()

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("DecisionFusionConfig: Configuration loaded successfully.")
            return cls(**data)
        except Exception as e:
            logger.error(f"DecisionFusionConfig: Failed to load config file: {e}. Using defaults.")
            return cls()


# --- Decision Output Pydantic Models ---

class RuleEngineBreakdown(BaseModel):
    score: int
    reasons: List[str]

class VerificationBreakdown(BaseModel):
    score: int
    reasons: List[str]

class MLBreakdown(BaseModel):
    probability: float
    prediction: str

class DecisionBreakdown(BaseModel):
    rule_engine: RuleEngineBreakdown
    verification: VerificationBreakdown
    machine_learning: MLBreakdown

class FusionOutput(BaseModel):
    final_risk_score: int
    final_verdict: str
    confidence: float
    decision_breakdown: DecisionBreakdown
    top_reasons: List[str]
    recommended_actions: List[str]
    confidence_contributors: Dict[str, float] = Field(default_factory=dict)
    weights: Dict[str, float] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the pydantic model to a standard dictionary for backward compatibility."""
        return self.model_dump()


# --- Focused Logic Components ---

class RuleScorer:
    """Computes the scam score based on negative rule matches and returns matching triggers."""
    @staticmethod
    def calculate(rule_engine_result: List[Dict[str, Any]]) -> Tuple[int, List[str]]:
        if not isinstance(rule_engine_result, list):
            logger.warning("RuleScorer: Input rule engine result is not a list. Defaulting score to 0.")
            return 0, []

        negative_rules = [item for item in rule_engine_result if isinstance(item, dict) and item.get("score", 0) < 0]
        deductions = sum(abs(item.get("score", 0)) for item in negative_rules)
        score = min(100, deductions)
        reasons = [item.get("title", "Unknown Rule") for item in negative_rules]
        return score, reasons


class VerificationScorer:
    """Computes a composite infrastructure trust risk score from active validation signals."""
    @staticmethod
    def calculate(verification_result: Dict[str, Any], config: VerificationDeductions) -> Tuple[int, List[str]]:
        if not isinstance(verification_result, dict):
            logger.warning("VerificationScorer: Input verification result is not a dictionary. Defaulting score to 0.")
            return 0, []

        deductions = 0
        reasons = []

        corp_email = verification_result.get("Corporate Email", "Unknown")
        if corp_email in ["Invalid", "Disposable", "Verification Pending"]:
            deductions += config.corp_email_invalid
            reasons.append(f"Corporate Email validation returned '{corp_email}'")

        website = verification_result.get("Website", "Unknown")
        if website in ["Unreachable", "Partially Verified"]:
            deductions += config.website_unreachable
            reasons.append(f"Website reachability returned '{website}'")

        if verification_result.get("DNS") == "Unreachable":
            deductions += config.dns_unreachable
            reasons.append("DNS A records could not be resolved")

        if verification_result.get("SSL") == "Invalid":
            deductions += config.ssl_invalid
            reasons.append("SSL certificate is invalid or expired")

        if verification_result.get("WHOIS") == "Not Found":
            deductions += config.whois_not_found
            reasons.append("WHOIS registry contains no active registration records")

        if verification_result.get("Domain Age") == "Unknown":
            deductions += config.domain_age_unknown
            reasons.append("Domain registration age could not be calculated")

        for key in ["Privacy Policy", "Terms", "Careers Page", "LinkedIn"]:
            if verification_result.get(key) in ["Missing", "Not Found"]:
                deductions += config.missing_signals
                reasons.append(f"Website crawled content is missing standard '{key}' links")

        score = min(100, deductions)
        return score, reasons


class VerdictMapper:
    """Classifies risk verdicts using composite scores and configured boundaries."""
    @staticmethod
    def map_score_to_verdict(score: int, boundaries: VerdictBoundaries) -> str:
        if score < boundaries.safe:
            return "SAFE"
        elif score < boundaries.suspicious:
            return "SUSPICIOUS"
        elif score < boundaries.high_risk:
            return "HIGH_RISK"
        return "SCAM"


class ConfidenceCalculator:
    """Calculates evaluation confidence ratings from input entity metrics and agreements."""
    @staticmethod
    def calculate(
        canonical_entities: Dict[str, Any],
        rule_score: int,
        ml_score: int,
        params: ConfidenceParameters,
        verification_result: Optional[Dict[str, Any]] = None,
        return_contributors: bool = False
    ) -> Any:
        if not isinstance(canonical_entities, dict):
            canonical_entities = {}

        # Completeness based on 11 key fields
        key_fields = ["company_name", "job_title", "salary", "location", "employment_type", "recruiter_email", "website", "skills", "benefits", "hiring_steps", "experience"]
        filled_count = 0
        for f in key_fields:
            val = canonical_entities.get(f, {}).get("value")
            if val is not None:
                val_str = str(val).strip()
                if val_str and val_str not in ["Unknown", "Unknown Value", "not_found", "not found", "None"]:
                    filled_count += 1
        completeness_pct = (filled_count / len(key_fields)) * 100

        # Agreement boost
        agreement_triggered = (rule_score > 40 and ml_score > 40) or (rule_score <= 40 and ml_score <= 40)
        agreement_boost = params.agreement_boost if agreement_triggered else 0.0

        # Verification Coverage (Percent of non-Unknown verification signals)
        verification_result = verification_result or {}
        verif_keys = ["Website", "Corporate Email", "DNS", "SSL", "WHOIS", "LinkedIn", "Privacy Policy", "Terms", "Careers Page", "Domain Age"]
        known_verif_count = sum(1 for k in verif_keys if verification_result.get(k, "Unknown") != "Unknown")
        verif_coverage = (known_verif_count / len(verif_keys)) * 100

        # ML Confidence (Normalized distance from boundary threshold 50.0)
        ml_confidence = abs(float(ml_score) - 50.0) * 2

        confidence = (completeness_pct * params.completeness_coefficient) + agreement_boost
        final_confidence = max(params.min_confidence, min(params.max_confidence, confidence))

        contributors = {
            "extraction_completeness": round(completeness_pct, 1),
            "rule_agreement_boost": round(agreement_boost, 1),
            "verification_coverage": round(verif_coverage, 1),
            "ml_confidence": round(ml_confidence, 1)
        }

        if return_contributors:
            return round(final_confidence, 2), contributors
        return round(final_confidence, 2)


class RecommendationCompiler:
    """Compiles actionable security mitigation recommendations based on risk classification."""
    @staticmethod
    def compile(
        verdict: str = "HIGH_RISK",
        rule_reasons: List[str] = None,
        verif_reasons: List[str] = None,
        rule_deductions: int = 0,
        verif_deductions: int = 0,
        ml_prediction: int = 0,
        negative_rules: List[Dict[str, Any]] = None,
        corp_email_status: str = "Unknown",
        website_status: str = "Unknown"
    ) -> List[str]:
        rule_reasons = rule_reasons or []
        verif_reasons = verif_reasons or []
        negative_rules = negative_rules or []
        actions = []

        # Context-aware verdict recommendations
        if verdict == "SAFE":
            actions.append("Continue using the official careers portal.")
            actions.append("Communicate only through verified corporate email.")
            actions.append("Verify the offer letter before sharing personal documents.")
        elif verdict == "SUSPICIOUS":
            actions.append("Verify the recruiter profile directly on official professional networks like LinkedIn.")
            actions.append("Cross-check company contact phone numbers and office locations independently.")
            actions.append("Request a live video interview before sharing any sensitive personal documents.")
        elif verdict == "HIGH_RISK":
            actions.append("Pause your application immediately and validate the company's existence independently.")
            actions.append("Do not click external links or download file attachments from unverified emails.")
            actions.append("Contact the company's official HR department to verify the job posting's validity.")
        else:  # SCAM
            actions.append("Stop all communication immediately with the sender or recruiter.")
            actions.append("Do not make any payments for registrations, certifications, or laptop setups.")
            actions.append("Report the job listing to the hosting platform and local cyber fraud authorities.")

        # Check verifications (Only for non-SAFE or warning signals)
        if verdict != "SAFE":
            if any("Corporate Email" in r for r in verif_reasons) or corp_email_status == "Unknown":
                actions.append("Verify recruiter domain and check for typosquatting variations against official brands.")
            if any("Website" in r for r in verif_reasons) or website_status == "Unreachable":
                actions.append("Avoid clicking external links or downloading materials from unverified recruiter websites.")
            if rule_deductions > 0:
                actions.append("Do not make upfront payments for registrations, certifications, or laptop setups.")

            # Check specific rule IDs
            rule_ids = [item.get("id", "") for item in negative_rules if isinstance(item, dict)]
            if any(r in rule_ids for r in ["telegram_only", "whatsapp_only"]):
                actions.append("Insist on official corporate communication channels and avoid personal messaging apps.")
            if any(r in rule_ids for r in ["no_interview", "guaranteed_placement"]):
                actions.append("Be skeptical of immediate hiring decisions without structured interview processes.")
            if any(r in rule_ids for r in ["urgency_urg", "limited_offer"]):
                actions.append("Take time to verify credentials; avoid high-pressure, short-deadline onboarding calls.")

            # Guarantee at least 3 distinct actions under risk
            if "Verify job offer legitimacy using official company directories." not in actions:
                actions.append("Verify job offer legitimacy using official company directories.")
            if len(actions) < 3:
                actions.append("Never share sensitive personal credentials (like OTPs or PAN) before formal contract offers.")

        return actions


# --- Main Orchestration Class ---

class DecisionFusionEngine:
    """
    Orchestration layer combining outputs of the modular Rule Engine, Network
    Verification panel, and Machine Learning Text Classifiers into a single, Pydantic-backed
    legitimacy verdict and detailed audit breakdowns.
    """

    @classmethod
    def fuse_decision(
        cls,
        canonical_entities: Dict[str, Any],
        rule_engine_result: List[Dict[str, Any]],
        verification_result: Dict[str, Any],
        ml_prediction: int,
        ml_probability: float
    ) -> Dict[str, Any]:
        """
        Calculates weighted composite scores, maps verdicts, calculates confidence,
        compiles recommendations, and returns a backward-compatible dictionary.
        """
        logger.info("DecisionFusionEngine: Starting weighted decision fusion execution...")

        # 1. Load config settings
        config = DecisionFusionConfig.load_from_file()

        # 2. Score Rule Engine
        rule_score, rule_reasons = RuleScorer.calculate(rule_engine_result)

        # 3. Score Verification
        verif_score, verif_reasons = VerificationScorer.calculate(
            verification_result, config.verification_deductions
        )

        # 4. Score ML Classifier
        ml_score = ml_probability * 100
        ml_pred_label = "Scam" if ml_prediction == 1 else "Safe"

        # 5. Composite score calculation
        fused_score_float = (
            (rule_score * config.rule_weight) +
            (verif_score * config.verification_weight) +
            (ml_score * config.ml_weight)
        )
        final_risk_score = int(round(max(0.0, min(100.0, fused_score_float))))

        # 6. Map Verdict Category
        final_verdict = VerdictMapper.map_score_to_verdict(
            final_risk_score, config.verdict_boundaries
        )

        # 7. Calculate Confidence
        confidence, confidence_contributors = ConfidenceCalculator.calculate(
            canonical_entities, rule_score, int(ml_score), config.confidence_parameters, verification_result, return_contributors=True
        )

        # 8. Compile Reasons
        top_reasons = []
        top_reasons.extend(rule_reasons[:2])
        top_reasons.extend(verif_reasons[:2])
        if ml_prediction == 1:
            top_reasons.append("ML text classification flagged listing content patterns as scam")

        if not top_reasons:
            top_reasons = ["No high-risk threat or verification indicators were triggered."]

        # 9. Compile Action Recommendations
        corp_email_status = verification_result.get("Corporate Email", "Unknown") if isinstance(verification_result, dict) else "Unknown"
        website_status = verification_result.get("Website", "Unknown") if isinstance(verification_result, dict) else "Unknown"
        
        actions = RecommendationCompiler.compile(
            verdict=final_verdict,
            rule_reasons=rule_reasons,
            verif_reasons=verif_reasons,
            rule_deductions=rule_score,
            verif_deductions=verif_score,
            ml_prediction=ml_prediction,
            negative_rules=rule_engine_result,
            corp_email_status=corp_email_status,
            website_status=website_status
        )

        # 10. Instantiate Pydantic Fusion Output Model
        output = FusionOutput(
            final_risk_score=final_risk_score,
            final_verdict=final_verdict,
            confidence=round(confidence, 2),
            decision_breakdown=DecisionBreakdown(
                rule_engine=RuleEngineBreakdown(score=rule_score, reasons=rule_reasons),
                verification=VerificationBreakdown(score=verif_score, reasons=verif_reasons),
                machine_learning=MLBreakdown(probability=round(float(ml_probability), 4), prediction=ml_pred_label)
            ),
            top_reasons=top_reasons,
            recommended_actions=actions,
            confidence_contributors=confidence_contributors,
            weights={
                "rule_weight": config.rule_weight,
                "verification_weight": config.verification_weight,
                "ml_weight": config.ml_weight
            }
        )

        logger.info(f"DecisionFusionEngine: Completed. Verdict={final_verdict}, Risk Score={final_risk_score}")
        return output.to_dict()
