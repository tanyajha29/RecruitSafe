import re
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger("recruitsafe")

# Define rule sets for scan categories with Version 2.0 scores and explanations
RULES = {
    "financial_fraud": [
        {
            "id": "registration_fee",
            "keywords": [r"\bregistration\s*fee\b", r"\bprocessing\s*fee\b", r"\bapplication\s*fee\b", r"\brefundable\s*deposit\b"],
            "name": "Registration Fee Requested",
            "description": "The job description requests a registration, application, or processing fee to apply or secure a spot. Legitimate employers never charge candidates.",
            "score": -25,
            "severity": "high",
            "explanation": "Legitimate employers never require candidates to pay registration or onboarding fees to secure employment."
        },
        {
            "id": "training_fee",
            "keywords": [r"\btraining\s*fee\b", r"\bmandatory\s*training\s*cost\b", r"\bpay\s*for\s*training\b", r"\bcertification\s*fee\b"],
            "name": "Training Fee Required",
            "description": "Requests payment for training materials or mandatory certifications before starting employment.",
            "score": -20,
            "severity": "high",
            "explanation": "Corporate entities absorb onboarding and training costs for valid employees, rather than asking for payment upfront."
        },
        {
            "id": "security_deposit",
            "keywords": [r"\bsecurity\s*deposit\b", r"\brefundable\s*security\b", r"\brefundable\s*caution\s*deposit\b"],
            "name": "Security Deposit Requested",
            "description": "Requests an upfront refundable security deposit for equipment, laptops, or remote work setups.",
            "score": -25,
            "severity": "high",
            "explanation": "Requesting security deposits for laptops or training materials is a signature tactic of recruitment fraud."
        },
        {
            "id": "equipment_purchase",
            "keywords": [r"\bequipment\s*purchase\b", r"\bbuy\s*your\s*own\s*laptop\b", r"\bcheck\s*for\s*equipment\b", r"\bsend\s*check\b", r"\bpurchase\s*software\b"],
            "name": "Upfront Equipment Purchase",
            "description": "Instructs candidates to purchase their own laptops or equipment with promised reimbursement checks.",
            "score": -20,
            "severity": "high",
            "explanation": "Established companies purchase and ship devices directly; they do not ask candidates to route funds or cash checks."
        }
    ],
    "identity_theft": [
        {
            "id": "aadhaar_pan_request",
            "keywords": [r"\baadhaar\b", r"\bpan\s*(?:card|number)?\b", r"\bpassport\s*(?:details|copy)\b", r"\bidentity\s*document\b"],
            "name": "Identity Document Requested Upfront",
            "description": "Requests sensitive government identifiers (like Aadhaar, PAN card, or Passport) before any interview or official hiring process.",
            "score": -20,
            "severity": "high",
            "explanation": "Government ID numbers should only be collected during background checks after a formal contract is offered."
        },
        {
            "id": "bank_account_request",
            "keywords": [r"\bbank\s*account\b", r"\baccount\s*details\b", r"\brouting\s*number\b", r"\bcard\s*details\b", r"\bbank\s*details\b"],
            "name": "Bank Details Requested",
            "description": "Requests bank accounts, card numbers, or direct deposit setup details prior to formal background checks or contract execution.",
            "score": -20,
            "severity": "high",
            "explanation": "Sharing direct deposit details prior to formal selection raises a high risk of identity theft and bank fraud."
        },
        {
            "id": "otp_request",
            "keywords": [r"\botp\b", r"\bone-time\s*password\b", r"\bone\s*time\s*password\b", r"\bverification\s*code\b", r"\bupi\s*pin\b"],
            "name": "OTP / Security Code Request",
            "description": "Asks candidates to share verification codes, OTPs, or UPI PINs, a critical indicator of credential harvesting and account hijacking.",
            "score": -30,
            "severity": "high",
            "explanation": "One-Time Passwords (OTPs) and UPI PINs are strictly private and sharing them exposes candidates to financial hacking."
        }
    ],
    "unrealistic_offers": [
        {
            "id": "no_interview",
            "keywords": [r"\bno\s*interview\b", r"\bdirect\s*joining\b", r"\bdirect\s*selection\b", r"\bwithout\s*interview\b", r"\bspot\s*selection\b"],
            "name": "Direct Hiring Without Interview",
            "description": "Guarantees job offers or direct placement without any formal screening, technical round, or recruiter conversations.",
            "score": -15,
            "severity": "medium",
            "explanation": "Legitimate organizations evaluate competency through testing and interviews before making formal job offers."
        },
        {
            "id": "guaranteed_placement",
            "keywords": [r"\bguaranteed\s*job\b", r"\b100%\s*guaranteed\s*placement\b", r"\bjob\s*assurance\b", r"\bguaranteed\s*placement\b"],
            "name": "Guaranteed Employment Promise",
            "description": "Guarantees employment regardless of experience or qualification. Real recruitment processes always involve evaluation.",
            "score": -15,
            "severity": "medium",
            "explanation": "Employment promises without skill screening indicate generic placement mills or fee-harvesting operations."
        }
    ],
    "pressure_tactics": [
        {
            "id": "urgency_urg",
            "keywords": [r"\bwithin\s*30\s*minutes\b", r"\bconfirm\s*within\s*2\s*hours\b", r"\bpay\s*immediately\b", r"\bimmediate\s*payment\b", r"\bquick\s*action\s*required\b", r"\bhurry\s*up\b"],
            "name": "Urgent Action Required",
            "description": "Creates synthetic panic by demanding payment or replies within an extremely short, restrictive window.",
            "score": -15,
            "severity": "medium",
            "explanation": "High-urgency responses are demanded to pressure candidates into bypassing caution and safety audits."
        },
        {
            "id": "limited_offer",
            "keywords": [r"\bonly\s*today\b", r"\boffer\s*expires\s*today\b", r"\blast\s*day\s*to\s*pay\b", r"\bseats\s*filling\s*fast\b", r"\blimited\s*offer\b"],
            "name": "Artificial Scarcity Pressure",
            "description": "Uses artificial scarcity language to pressure candidates into making emotionally driven, rash decisions.",
            "score": -10,
            "severity": "low",
            "explanation": "Artificial seats-filling limits are used to discourage candidates from checking organization details."
        }
    ],
    "contact_anomalies": [
        {
            "id": "free_email_body",
            "keywords": [
                r"\b[a-zA-Z0-9._%+-]+@gmail\.com\b",
                r"\b[a-zA-Z0-9._%+-]+@yahoo\.com\b",
                r"\b[a-zA-Z0-9._%+-]+@outlook\.com\b",
                r"\b[a-zA-Z0-9._%+-]+@hotmail\.com\b"
            ],
            "name": "Public Domain Recruiter Email",
            "description": "Mentions contact details routing to free, public email addresses instead of official company email domains.",
            "score": -15,
            "severity": "medium",
            "explanation": "Professional corporate recruiters always contact candidates from corporate domain-authenticated mail servers."
        },
        {
            "id": "whatsapp_only",
            "keywords": [
                r"\bwhatsapp\s*(?:only|group|chat|link|number|us\s*at)\b",
                r'wa\.me\/',
                r'chat\.whatsapp\.com\/'
            ],
            "name": "WhatsApp-Only Recruiter Contact",
            "description": "Recruiter directs candidates to communicate exclusively via personal WhatsApp chats or links, avoiding professional channels.",
            "score": -10,
            "severity": "low",
            "explanation": "Corporate recruitments utilize corporate emails or dedicated HR portals; personal chat rooms lack audit controls."
        }
    ]
}

class ScamRuleEngine:
    @staticmethod
    def analyze_text(text: str) -> Tuple[List[Dict], List[Dict], int]:
        """
        Scans a job description or email text for exact match rules.
        Each match registers independently.
        Returns:
            evidence: List of dictionaries matching the V2 extended Evidence schema
            red_flags: List of matching red flags {title, description, severity}
            total_deductions: Sum of points to deduct (represented as positive value for scorer input)
        """
        if not text:
            return [], [], 0

        evidence_list = []
        red_flags_list = []
        total_deductions = 0
        matched_rule_ids = set()

        # Iterate over rule sets
        for category, rules in RULES.items():
            for rule in rules:
                rule_id = rule["id"]
                if rule_id in matched_rule_ids:
                    continue

                # Compile and check all keywords/regexes for this rule, capturing the matched substring
                is_matched = False
                matched_substring = ""
                for pattern in rule["keywords"]:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        is_matched = True
                        matched_substring = match.group(0)
                        break

                if is_matched:
                    matched_rule_ids.add(rule_id)
                    score_deduction = abs(rule["score"])
                    total_deductions += score_deduction

                    # V2 Extended Evidence Dict
                    evidence_list.append({
                        "category": category,
                        "factor_name": rule["name"],  # Backwards compatibility
                        "points_deducted": score_deduction,  # Backwards compatibility
                        "severity": rule["severity"],
                        # V2 fields
                        "id": rule_id,
                        "title": rule["name"],
                        "score": rule["score"],  # Signed integer (-25)
                        "matched_text": matched_substring,
                        "explanation": rule["explanation"]
                    })

                    # Append to red flags list
                    red_flags_list.append({
                        "title": rule["name"],
                        "description": rule["description"],
                        "severity": rule["severity"]
                    })

        return evidence_list, red_flags_list, total_deductions
