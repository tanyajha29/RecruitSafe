import logging
from typing import Tuple, Dict, Any, List

logger = logging.getLogger("recruitsafe")

class RiskScorer:
    """
    Computes composite trust scores, calculates agreement ratings between
    the rule engine and semantic AI, and applies verification clamps and 
    agreement overrides to return a balanced risk assessment.
    """

    @classmethod
    def calculate_agreement(
        cls,
        rule_trust_score: int,
        ai_classification: Dict[str, Any],
        has_financial: bool,
        has_identity: bool
    ) -> Tuple[int, str]:
        """
        Calculates consistency (0-100) between the rule engine and semantic AI results.
        Generates a detailed text explanation of the agreement/disagreement logic.
        """
        # 1. Map Rule Score to Rank
        if rule_trust_score >= 90:
            rule_rank = 4  # Safe
        elif rule_trust_score >= 60:
            rule_rank = 3  # Needs Verification
        elif rule_trust_score >= 40:
            rule_rank = 2  # Suspicious
        else:
            rule_rank = 1  # High Risk

        # 2. Map AI overall risk label to Rank
        ai_risk_label = str(ai_classification.get("overall_risk", "Safe")).strip()
        if ai_risk_label == "Safe":
            ai_rank = 4
        elif ai_risk_label == "Needs Verification":
            ai_rank = 3
        elif ai_risk_label == "Suspicious":
            ai_rank = 2
        else:
            ai_rank = 1  # High Risk

        # 3. Calculate rank distance
        diff = abs(rule_rank - ai_rank)
        if diff == 0:
            agreement = 100
        elif diff == 1:
            agreement = 80
        elif diff == 2:
            agreement = 50
        else:
            agreement = 10

        # 4. Check specific feature contradictions
        conflict_notes = []
        ai_payments = str(ai_classification.get("payment_requests", "None")).strip()
        if has_financial and ai_payments == "None":
            agreement -= 20
            conflict_notes.append("Rule engine flagged financial risk, but AI classified payment requests as 'None'.")

        ai_identity = str(ai_classification.get("identity_requests", "None")).strip()
        if has_identity and ai_identity == "None":
            agreement -= 20
            conflict_notes.append("Rule engine flagged identity risk, but AI classified identity requests as 'None'.")

        agreement_score = max(0, min(100, agreement))

        # 5. Generate Explanation
        rule_verdict_str = "Safe" if rule_rank == 4 else ("Needs Verification" if rule_rank == 3 else ("Suspicious" if rule_rank == 2 else "High Risk"))
        ai_verdict_str = ai_risk_label

        if agreement_score >= 80:
            explanation = f"Rule Engine ({rule_verdict_str}) and AI Model ({ai_verdict_str}) are in high alignment (Agreement: {agreement_score}%)."
            if conflict_notes:
                explanation += " Note: " + " ".join(conflict_notes)
        else:
            explanation = f"Divergence detected between Rule Engine ({rule_verdict_str}) and AI Model ({ai_verdict_str}) (Agreement: {agreement_score}%)."
            if conflict_notes:
                explanation += " " + " ".join(conflict_notes)
            else:
                explanation += " The models evaluated the semantic details vs technical evidence differently."

        return agreement_score, explanation

    @classmethod
    def calculate_risk(
        cls, 
        evidence_list: Any = None, 
        positive_findings: List[Dict[str, Any]] = None, 
        ai_classification: Dict[str, Any] = None, 
        is_verified_employer: bool = False
    ) -> Tuple[int, float, str, int, str]:
        """
        Combines positive and negative evidence into a composite trust score.
        Enforces a maximum score of 94 unless company footprint is Verified.
        Returns:
            Tuple[trust_score, scam_probability, risk_category, agreement_score, agreement_explanation]
        """
        # Handle legacy V1 signature call, e.g. calculate_risk(deductions_int)
        if isinstance(evidence_list, (int, float)):
            total_deductions = int(evidence_list)
            trust_score = max(0, min(100, 100 - total_deductions))
            scam_probability = float(100.0 - trust_score)
            if trust_score >= 90:
                risk_category = "Safe"
            elif trust_score >= 60:
                risk_category = "Needs Verification"
            elif trust_score >= 40:
                risk_category = "Suspicious"
            else:
                risk_category = "High Risk"
            return trust_score, scam_probability, risk_category

        evidence_list = evidence_list or []
        positive_findings = positive_findings or []
        ai_classification = ai_classification or {}

        # Start with a base trust score of 100
        trust_score = 100

        # 1. Apply negative evidence deductions (filter to confirmed negative items only)
        confirmed_negatives = [item for item in evidence_list if item.get("evidence_type", "negative") == "negative"]
        total_deductions = sum(abs(item.get("score", 0)) for item in confirmed_negatives)
        trust_score -= total_deductions

        # 2. Apply positive findings bonuses
        total_bonuses = sum(item.get("score", 0) for item in positive_findings)
        trust_score += total_bonuses

        # Clamp trust score between 0 and 100
        trust_score = max(0, min(100, trust_score))

        # 3. Enforce Verified Employer Clamp
        # Never award 95+ unless there is actual verification (is_verified_employer is True)
        if not is_verified_employer and trust_score >= 95:
            logger.info(f"Trust score {trust_score} clamped to 94 because employer footprint is unverified.")
            trust_score = 94

        scam_probability = float(100.0 - trust_score)

        # 4. Calculate consistency (Agreement Score & Explanation)
        has_financial = any(item.get("category") == "financial_fraud" for item in confirmed_negatives)
        has_identity = any(item.get("category") == "identity_theft" for item in confirmed_negatives)
        
        agreement_score, agreement_explanation = cls.calculate_agreement(
            rule_trust_score=trust_score,
            ai_classification=ai_classification,
            has_financial_rules=has_financial,
            has_identity_rules=has_identity
        )

        # 5. Determine Verdict (Risk Category)
        # Agreement below 60% overrides verdict to "Manual Review Recommended"
        if agreement_score < 60:
            risk_category = "Manual Review Recommended"
        else:
            if trust_score >= 90:
                risk_category = "Safe"
            elif trust_score >= 80:
                # 80-89 range is likely safe but verification is recommended
                risk_category = "Safe"
            elif trust_score >= 60:
                risk_category = "Needs Verification"
            elif trust_score >= 40:
                risk_category = "Suspicious"
            else:
                risk_category = "High Risk"

        return trust_score, scam_probability, risk_category, agreement_score, agreement_explanation
