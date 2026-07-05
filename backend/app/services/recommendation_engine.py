from typing import List, Dict, Any

class RecommendationEngine:
    """
    Generates dynamic, actionable safety recommendations for the job seeker
    based on the specific positive and negative evidence detected.
    """

    MAPPINGS = {
        # Financial Fraud
        "registration_fee": "Never pay any upfront registration, application, or processing fees to apply for a job or secure a position.",
        "training_fee": "Do not pay for mandatory training materials, courses, or certificates as a condition of starting work.",
        "security_deposit": "Refuse requests to pay refundable security deposits for corporate laptops, routers, or remote equipment.",
        "equipment_purchase": "Do not purchase remote work hardware or software under the promise of reimbursement via checks.",
        
        # Identity Theft
        "aadhaar_pan_request": "Do not submit scanned copies or numbers of your Aadhaar or PAN card during the initial application phase.",
        "upfront_aadhaar_request": "Do not submit copies of your Aadhaar card before the interview stage.",
        "upfront_pan_request": "Do not submit copies of your PAN card before the interview stage.",
        "upfront_passport_request": "Do not share passport photos or scans upfront; wait until you have a verified, signed contract.",
        "upfront_driving_licence_request": "Avoid uploading copies of your driver's license prior to formal selection checks.",
        "bank_account_request": "Do not share bank account details, routing numbers, or blank checks before background verification is complete.",
        "upfront_bank_details_request": "Refrain from providing bank account numbers or direct deposit details before a formal job offer is finalized.",
        "upfront_card_details_request": "Never share credit or debit card numbers, expiration dates, or CVVs with a recruiter.",
        "otp_request": "CRITICAL: Never share verification codes, OTPs, or transaction PINs. Legitimate HR systems never request private codes.",
        "upfront_otp_request": "CRITICAL: Under no circumstances share verification OTPs or UPI PINs with recruiters.",
        
        # Unrealistic Offers
        "no_interview": "Be highly skeptical of job selections issued without a formal face-to-face or video interview.",
        "direct_joining_no_interview": "Request a live virtual meeting with the hiring panel; avoid accepting direct selections without evaluations.",
        "unrealistic_fresher_salary": "Verify the compensation against industry baselines on glassdoor or AmbitionBox; this offer significantly exceeds market standard bounds.",
        "guaranteed_placement": "Legitimate jobs require testing and interviews; treat guaranteed hiring promises with caution.",
        
        # Pressure Tactics
        "high_urgency_tactics": "Do not rush. Fraudulent recruiters use artificial deadlines to pressure you into bypassing caution.",
        "urgency_urg": "Take your time to verify the recruiter's credentials. Real employers do not require immediate payments or decisions within hours.",
        "limited_offer": "Ignore artificial scarcity warnings ('only today', 'seats filling fast') designed to trigger emotional, rash decisions.",
        
        # Contact Anomalies
        "free_email_body": "Request the recruiter to email you from their official corporate email address rather than a public domain (like Gmail or Yahoo).",
        "whatsapp_only": "Avoid running job discussions exclusively on WhatsApp. Demand official email communication or phone calls.",
        
        # Contradictions
        "email_typosquatting_contradiction": "Double-check the spelling of the recruiter's email domain; it appears to lookalike/spoof a legitimate company's official domain.",
        "claim_vs_domain_age_contradiction": "Verify the business registration details; the recruiting domain is brand new despite claims of representing a long-standing firm.",
        "claim_vs_ssl_contradiction": "Do not enter passwords or personal details on the recruiter's website, as it lacks HTTPS encryption protocols.",
        
        # Website Failures
        "very_young_domain": "Diligently research the company's registration history. The website domain was created less than 30 days ago.",
        "young_domain": "Exercise caution as the recruiter's portal is very young, indicating it may be a temporary scam site.",
        "missing_ssl": "Avoid browsing or uploading files to the provided URL, as it lacks secure SSL/HTTPS encryption."
    }

    DEFAULT_RECOMMENDATIONS = [
        "Verify the recruiter's profile on LinkedIn to ensure they are currently employed with the claimed organization.",
        "Cross-check the official company careers portal to confirm if the vacancy is listed there.",
        "Do not submit sensitive document scans during the initial screening stages."
    ]

    @classmethod
    def generate_recommendations(cls, evidence_list: List[Dict[str, Any]], positive_findings: List[Dict[str, Any]]) -> List[str]:
        """
        Dynamically builds recommendations based on active evidence.
        """
        recommendations = []
        triggered_ids = set()

        # Collect rule/evidence IDs
        for item in evidence_list:
            r_id = item.get("id")
            if r_id:
                triggered_ids.add(r_id)

        # Map triggered IDs to recommendations
        for r_id in triggered_ids:
            if r_id in cls.MAPPINGS:
                recommendations.append(cls.MAPPINGS[r_id])

        # If no SSL was found in positive checks
        has_ssl = any(item.get("id") == "valid_ssl_certificate" for item in positive_findings)
        if not has_ssl and len(recommendations) < 3:
            recommendations.append("Ensure you only submit details to websites that enforce secure HTTPS protocols.")

        # Fill with default professional tips to guarantee 3-5 recommendations
        for tip in cls.DEFAULT_RECOMMENDATIONS:
            if len(recommendations) >= 4:
                break
            if tip not in recommendations:
                recommendations.append(tip)

        return recommendations
