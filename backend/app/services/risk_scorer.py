import logging
from typing import Tuple, Dict, Any, List

logger = logging.getLogger("recruitsafe")

class RiskScorer:
    """
    Computes composite trust scores, calculates agreement ratings between
    the rule engine and semantic AI, and applies overrides to return the
    'Review Required' verdict when confidence is low or inputs are incomplete.
    """

    @staticmethod
    def calculate_agreement_score(
        rule_trust_score: int, 
        ai_classification: Dict[str, Any], 
        has_financial_rules: bool, 
        has_identity_rules: bool
    ) -> int:
        """
        Calculates consistency (0-100) between the rule engine and semantic AI results.
        """
        # 1. Map Rule Score to Rank
        if rule_trust_score >= 80:
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
        # If rules flagged financial fraud but AI classified payment requests as "None"
        ai_payments = str(ai_classification.get("payment_requests", "None")).strip()
        if has_financial_rules and ai_payments == "None":
            agreement -= 20
            logger.info("Conflict: Rule engine flagged financial fraud but AI reports no payment request.")

        # If rules flagged identity harvesting but AI classified identity requests as "None"
        ai_identity = str(ai_classification.get("identity_requests", "None")).strip()
        if has_identity_rules and ai_identity == "None":
            agreement -= 20
            logger.info("Conflict: Rule engine flagged identity harvesting but AI reports no identity request.")

        return max(0, min(100, agreement))

    @classmethod
    def calculate_risk(
        cls, 
        evidence_list: Any = None, 
        positive_findings: List[Dict[str, Any]] = None, 
        ai_classification: Dict[str, Any] = None, 
        confidence_score: int = 100, 
        missing_info: List[str] = None
    ) -> Tuple[int, float, str, int]:
        """
        Combines positive and negative evidence into a composite trust score.
        Supports both V2 multi-layer input and V1 legacy calls (where evidence_list is total_deductions).
        Returns:
            Tuple[trust_score, scam_probability, risk_category, agreement_score]
        """
        # Handle legacy V1 signature call, e.g. calculate_risk(deductions_int)
        if isinstance(evidence_list, (int, float)):
            total_deductions = int(evidence_list)
            trust_score = max(0, min(100, 100 - total_deductions))
            scam_probability = float(100.0 - trust_score)
            if trust_score >= 80:
                risk_category = "Safe"
            elif trust_score >= 60:
                risk_category = "Needs Verification"
            elif trust_score >= 40:
                risk_category = "Suspicious"
            else:
                risk_category = "High Risk"
            return trust_score, scam_probability, risk_category

        # V2.0 logic
        evidence_list = evidence_list or []
        positive_findings = positive_findings or []
        ai_classification = ai_classification or {}
        missing_info = missing_info or []

        # Start with a base trust score of 100
        trust_score = 100

        # 1. Apply negative evidence deductions
        total_deductions = sum(abs(item.get("score", 0)) for item in evidence_list)
        trust_score -= total_deductions

        # 2. Apply positive findings bonuses
        total_bonuses = sum(item.get("score", 0) for item in positive_findings)
        trust_score += total_bonuses

        # Clamp trust score between 0 and 100
        trust_score = max(0, min(100, trust_score))
        scam_probability = float(100.0 - trust_score)

        # 3. Calculate consistency (Agreement Score)
        has_financial = any(item.get("category") == "financial_fraud" for item in evidence_list)
        has_identity = any(item.get("category") == "identity_theft" for item in evidence_list)
        
        agreement_score = cls.calculate_agreement_score(
            rule_trust_score=trust_score,
            ai_classification=ai_classification,
            has_financial_rules=has_financial,
            has_identity_rules=has_identity
        )

        # 4. Check for 'Review Required' overrides
        is_low_confidence = confidence_score < 40
        is_conflicting = agreement_score < 40
        is_incomplete = len(missing_info) >= 2

        if is_low_confidence or is_conflicting or is_incomplete:
            risk_category = "Review Required"
            logger.info(
                f"Override to 'Review Required' active. Reason: "
                f"low_confidence={is_low_confidence} ({confidence_score}), "
                f"conflicting={is_conflicting} ({agreement_score}), "
                f"incomplete={is_incomplete} ({len(missing_info)} items)"
            )
        else:
            # Map standard trust score to risk category
            if trust_score >= 80:
                risk_category = "Safe"
            elif trust_score >= 60:
                risk_category = "Needs Verification"
            elif trust_score >= 40:
                risk_category = "Suspicious"
            else:
                risk_category = "High Risk"

        return trust_score, scam_probability, risk_category, agreement_score
