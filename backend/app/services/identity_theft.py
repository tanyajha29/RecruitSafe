import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("recruitsafe")

class IdentityTheftDetector:
    """
    Identifies sensitive identity information harvesting requests.
    Differentiates between high-risk upfront requests (before interviews)
    and standard onboarding references (after hiring).
    """

    # Upfront request patterns (e.g. "send your Aadhaar to apply", "PAN required for registration")
    UPFRONT_PATTERNS = [
        r'\b(?:send|email|share|upload|provide|submit|whatsapp)\s+(?:your\s+|copy\s+of\s+|details\s+of\s+)?(?:aadhaar|pan|passport|driving\s+licence|bank\s+details|debit\s+card|credit\s+card|passbook)\b',
        r'\b(?:aadhaar|pan|passport|driving\s+licence|bank\s+details|debit\s+card|credit\s+card|passbook)\s+(?:is\s+)?required\s+(?:to\s+apply|for\s+registration|before\s+interview|for\s+screening)\b'
    ]

    # Onboarding context patterns (e.g. "after offer", "upon hiring")
    ONBOARDING_KEYWORDS = [
        r'\b(?:after\s+hiring|upon\s+selection|after\s+offer\s+letter|during\s+onboarding|post\s+selection|after\s+joining)\b'
    ]

    @classmethod
    def analyze_identity_requests(cls, text: str) -> Dict[str, Any]:
        """
        Scans text for government ID and bank detail requests.
        Differentiates based on context.
        """
        evidence = []
        
        if not text:
            return {
                "evidence": [],
                "detected_items": []
            }

        detected_items = []
        
        # Base terms to scan
        id_terms = {
            "aadhaar": r'\baadhaar\b',
            "pan": r'\bpan\s*(?:card|number)?\b',
            "passport": r'\bpassport\b',
            "driving_licence": r'\bdriving\s*licence\b',
            "bank_details": r'\b(?:bank\s+account|routing\s+number|bank\s+details|passbook)\b',
            "card_details": r'\b(?:debit\s+card|credit\s+card|cvv|card\s+number)\b',
            "otp_security": r'\b(?:otp|one-time\s+password|verification\s+code|upi\s+pin)\b'
        }

        for item_key, regex in id_terms.items():
            match = re.search(regex, text, re.IGNORECASE)
            if match:
                detected_items.append(item_key)

        # Check if the text contains onboarding keywords
        is_onboarding_context = False
        for pattern in cls.ONBOARDING_KEYWORDS:
            if re.search(pattern, text, re.IGNORECASE):
                is_onboarding_context = True
                break

        # Analyze each detected item
        for item in detected_items:
            # Check if this is an upfront request
            is_upfront = False
            matched_str = ""
            for pattern in cls.UPFRONT_PATTERNS:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    is_upfront = True
                    matched_str = m.group(0)
                    break
            
            # If it is NOT explicitly onboarding and matched upfront patterns OR no onboarding keywords exist at all
            if (is_upfront or not is_onboarding_context):
                if item in ["aadhaar", "pan", "passport", "driving_licence"]:
                    evidence.append({
                        "id": f"upfront_{item}_request",
                        "title": f"Upfront {item.replace('_', ' ').title()} Requested",
                        "category": "identity_theft",
                        "severity": "high",
                        "score": -20,
                        "description": f"The job posting requests sensitive government identification documents ({item.replace('_', ' ').title()}) upfront before any screening. Legitimate recruiters only request government IDs after a formal job offer is accepted.",
                        "matched_text": matched_str or item.upper(),
                        "explanation": f"Detected upfront request for sensitive identifier '{item}' prior to hiring/interview stage."
                    })
                elif item in ["bank_details", "card_details"]:
                    evidence.append({
                        "id": f"upfront_{item}_request",
                        "title": f"Upfront {item.replace('_', ' ').title()} Requested",
                        "category": "identity_theft",
                        "severity": "high",
                        "score": -20,
                        "description": f"Requests financial credentials or bank account details prior to selection or standard payroll setup. Sharing banking info upfront poses a high threat of financial skimming.",
                        "matched_text": matched_str or item.upper(),
                        "explanation": f"Financial credentials '{item}' requested upfront without post-hiring/payroll context."
                    })
                elif item == "otp_security":
                    evidence.append({
                        "id": "upfront_otp_request",
                        "title": "OTP / Security Code Requested",
                        "category": "identity_theft",
                        "severity": "high",
                        "score": -30,
                        "description": "Asks candidates to share OTPs, security verification codes, or UPI PINs. This is a critical indicator of account hacking and credential harvesting.",
                        "matched_text": matched_str or "OTP",
                        "explanation": "Security verification code request identified. Critical threat of credential harvesting."
                    })
            else:
                # Standard onboarding reference - log notice but no deduction
                logger.info(f"Identity document '{item}' references found in normal post-hiring onboarding context. No deduction applied.")

        return {
            "evidence": evidence,
            "detected_items": detected_items
        }
