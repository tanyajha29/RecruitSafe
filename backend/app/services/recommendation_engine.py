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
        triggered_ids = {item.get("id") for item in evidence_list}

        # 1. WhatsApp Contact Warning
        if "whatsapp_only" in triggered_ids:
            recommendations.append("Use WhatsApp only after verifying the recruiter through their official corporate email or LinkedIn profile.")

        # 2. Certification Partner Warning
        has_certification = any("certification" in str(r_id).lower() or "training" in str(r_id).lower() for r_id in triggered_ids)
        if has_certification:
            recommendations.append("Verify whether the training organization is officially listed on the employer's website.")

        # 3. Website Missing
        website_state = verification_status.get("Website", "Unknown") if verification_status else "Unknown"
        if website_state == "Unknown" or "website_missing" in triggered_ids or "website_unsupplied" in triggered_ids:
            recommendations.append("Request the employer's official careers page before sharing sensitive information.")

        # 4. Financial Fraud / Fees
        has_fee = any("fee" in str(r_id).lower() or "deposit" in str(r_id).lower() for r_id in triggered_ids)
        if has_fee:
            recommendations.append("Never pay recruitment, application, or training onboarding fees under any circumstances.")

        # 5. Young Domain
        has_young = "very_young_domain" in triggered_ids or "young_domain" in triggered_ids
        if has_young:
            recommendations.append("Verify company registration and business presence before sharing sensitive information; this domain is newly registered.")

        # 6. Missing SSL
        if "missing_ssl" in triggered_ids:
            recommendations.append("Avoid submitting credentials or personal documents to this website as it lacks secure SSL/HTTPS encryption.")

        # 7. Identity requests
        has_identity = any(item.get("category") == "identity_theft" for item in evidence_list)
        if has_identity:
            recommendations.append("Do not share scanned copies of government identifiers (like Aadhaar, PAN card, or passport) during initial application stages.")

        # 8. OTP / PIN requests
        has_otp = any("otp" in str(item.get("id", "")).lower() for item in evidence_list)
        if has_otp:
            recommendations.append("CRITICAL: Under no circumstances share verification OTPs, passwords, or transaction PINs with recruiters.")

        # If no specific recommendations are triggered, fall back to default safety protocols
        if not recommendations:
            recommendations = [
                "Verify the recruiter's official corporate profile on LinkedIn to ensure validity.",
                "Cross-check company openings directly on their official careers portal.",
                "Perform standard web search research on the company registry name."
            ]

        # De-duplicate while maintaining order
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recs.append(rec)

        return unique_recs
