from typing import List, Dict, Any

class RecommendationEngine:
    """
    Generates dynamic, actionable safety recommendations based entirely
    on specific positive, negative, and unknown evidence elements detected.
    """

    @classmethod
    def generate_recommendations(
        cls, 
        evidence_list: List[Dict[str, Any]], 
        positive_findings: List[Dict[str, Any]],
        verification_status: Dict[str, str]
    ) -> List[str]:
        """
        Dynamically builds recommendations based on active evidence and verification statuses.
        Does not use generic fill recommendations when specific evidence is present.
        """
        recommendations = []

        # 1. Analyze Verification Statuses
        if verification_status:
            # Website Unreachable / Unknown
            dns_state = verification_status.get("DNS", "Not Found")
            web_state = verification_status.get("Website", "Not Found")
            if dns_state == "Invalid" or web_state == "Unknown":
                recommendations.append("Verify the employer through official public sources (like MCA registration or state corporate registries).")
            
            # Corporate Email Verified
            email_state = verification_status.get("Corporate Email", "Not Found")
            if email_state == "Verified":
                recommendations.append("Continue communication using the verified corporate domain email address only.")

        # 2. Analyze specific evidence IDs
        triggered_ids = {item.get("id") for item in evidence_list}

        # Financial Fraud / Fees
        has_fee = any("fee" in str(r_id).lower() or "deposit" in str(r_id).lower() for r_id in triggered_ids)
        if has_fee:
            recommendations.append("Never pay recruitment, application, or training onboarding fees under any circumstances.")

        # Young Domain
        has_young = "very_young_domain" in triggered_ids or "young_domain" in triggered_ids or "history_vs_domain_age_contradiction" in triggered_ids
        if has_young:
            recommendations.append("Verify company registration and business presence before sharing sensitive information; this domain is newly registered.")

        # Missing SSL
        if "missing_ssl" in triggered_ids or "https_vs_ssl_fail_contradiction" in triggered_ids:
            recommendations.append("Avoid submitting credentials or personal documents to this website as it lacks secure SSL/HTTPS encryption.")

        # Identity requests
        has_identity = any(item.get("category") == "identity_theft" for item in evidence_list)
        if has_identity:
            recommendations.append("Do not share scanned copies of government identifiers (like Aadhaar, PAN card, or passport) during initial application stages.")

        # Urgency pressure
        has_urgency = any(item.get("category") == "pressure_tactics" for item in evidence_list)
        if has_urgency:
            recommendations.append("Take your time to investigate. Legitimate recruiters do not impose immediate, high-pressure response deadlines.")

        # Brand spoofing
        if "brand_vs_free_email_contradiction" in triggered_ids:
            recommendations.append("Validate the posting directly on the official company careers site. Established corporate entities do not recruit via free email accounts.")

        # Fallback if no specific issues were flagged
        if not recommendations:
            recommendations = [
                "Verify the recruiter on professional networks like LinkedIn to ensure they work at the claimed company.",
                "Cross-check company openings directly on their official careers portal.",
                "Perform standard online research on the company to confirm their legitimacy."
            ]

        # De-duplicate while maintaining order
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recs.append(rec)

        return unique_recs
