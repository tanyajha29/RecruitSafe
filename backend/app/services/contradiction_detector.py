import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("recruitsafe")

class ContradictionDetector:
    """
    Detects structural contradictions in recruitment offers by matching
    textual claims against physical server/domain intelligence metrics.
    """

    @classmethod
    def detect_contradictions(cls, text: str, email_data: Optional[Dict[str, Any]], website_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs cross-layer contradiction logic.
        Returns:
        dict containing:
            contradictions: list of string descriptions
            evidence: list of negative Evidence objects
        """
        contradictions = []
        evidence = []

        if not text:
            return {
                "contradictions": [],
                "evidence": []
            }

        # 1. Recruiter Email Domain vs Company Website typosquatting contradiction
        if email_data and email_data.get("typosquatting_check"):
            typo = email_data["typosquatting_check"]
            if typo.get("is_suspicious_typosquatting"):
                reason = typo.get("reason", "Recruiter domain closely resembles official company domain.")
                contradictions.append(reason)
                evidence.append({
                    "id": "email_typosquatting_contradiction",
                    "rule_id": "CON_001",
                    "title": "Domain Typosquatting Contradiction",
                    "category": "contradictions",
                    "severity": "high",
                    "score": -20,
                    "matched_text": email_data.get('domain'),
                    "reason": f"Recruiter is contacting from an unofficial lookalike domain ({email_data.get('domain')}) that matches typosquatting patterns for the target company. Fraudulent actors register lookalikes to spoof official HR departments.",
                    "evidence_type": "negative",
                    "confidence": 15,
                    "source": "Email Analyzer"
                })

        # 2. Famous Corporate Brand vs Free Email Provider Contradiction
        # Check if the text references a major corporate brand, but recruiter email is a free public address
        famous_brands = ["google", "microsoft", "amazon", "apple", "facebook", "netflix", "adobe", "salesforce", "ibm", "tcs", "wipro", "infosys", "cognizant", "accenture", "meta"]
        brand_detected = None
        for brand in famous_brands:
            if re.search(r'\b' + brand + r'\b', text, re.IGNORECASE):
                brand_detected = brand.capitalize()
                break

        if brand_detected and email_data and email_data.get("is_free_email"):
            msg = f"Claims to represent {brand_detected} but recruiter uses a free email address ({email_data.get('sender_email')})."
            contradictions.append(msg)
            evidence.append({
                "id": "brand_vs_free_email_contradiction",
                "rule_id": "CON_002",
                "title": "Corporate Brand Spoofing",
                "category": "contradictions",
                "severity": "high",
                "score": -25,
                "matched_text": f"Brand: {brand_detected} vs Email: {email_data.get('sender_email')}",
                "reason": f"The job posting claims association with {brand_detected}, but the contact email uses a free public provider ({email_data.get('sender_email')}) instead of an official brand domain.",
                "evidence_type": "negative",
                "confidence": 15,
                "source": "Email Analyzer"
            })

        # 3. Famous Corporate Brand vs Chat-Only Recruiting Channels Contradiction
        has_whatsapp = bool(re.search(r'\b(?:whatsapp|wa\.me|chat\s+on\s+whatsapp)\b', text, re.IGNORECASE))
        has_phone = bool(re.search(r'\b(?:\+?\d{1,3}[- ]?)?\d{10}\b', text))
        has_email = email_data and email_data.get("domain") != ""
        has_website = website_data is not None

        if brand_detected and (has_whatsapp or has_phone) and not (has_email or has_website):
            msg = f"Claims to represent {brand_detected} but lists only a telephone/WhatsApp contact channel."
            contradictions.append(msg)
            evidence.append({
                "id": "brand_vs_whatsapp_contradiction",
                "rule_id": "CON_003",
                "title": "Unverified Contact Channel Mismatch",
                "category": "contradictions",
                "severity": "high",
                "score": -20,
                "matched_text": "WhatsApp/Phone contact for corporate brand",
                "reason": f"The job post references {brand_detected} but only provides a direct phone/WhatsApp contact without an official corporate email or web portal.",
                "evidence_type": "negative",
                "confidence": 10,
                "source": "Rule Engine"
            })

        # 4. HTTPS URL vs SSL Verification Failure Contradiction
        if website_data and website_data.get("url", "").startswith("https://") and website_data.get("ssl") and not website_data["ssl"].get("has_valid_ssl"):
            msg = "Website claims HTTPS connection, but SSL verification failed."
            contradictions.append(msg)
            evidence.append({
                "id": "https_vs_ssl_fail_contradiction",
                "rule_id": "CON_004",
                "title": "Broken Secure Protocol (SSL Fail)",
                "category": "contradictions",
                "severity": "medium",
                "score": 0,
                "matched_text": website_data.get("url"),
                "reason": "The URL specifies a secure protocol (HTTPS) but the security certificate handshake failed, indicating a self-signed, expired, or spoofed certificate.",
                "evidence_type": "negative",
                "confidence": 10,
                "source": "Website Analyzer"
            })

        # 5. Established / History Claims vs Domain Age Contradiction
        has_history_claim = bool(re.search(r'\b(?:established\s+in|founded\s+in|celebrating\s+\d+|over\s+\d+\s+years|since\s+\d{4})\b', text, re.IGNORECASE))
        if has_history_claim and website_data and website_data.get("whois"):
            whois = website_data["whois"]
            age = whois.get("domain_age_days")
            if age is not None and age < 60:
                msg = f"Company claims established history, but the website domain age is only {age} days."
                contradictions.append(msg)
                evidence.append({
                    "id": "history_vs_domain_age_contradiction",
                    "rule_id": "CON_005",
                    "title": "Corporate Longevity Mismatch",
                    "category": "contradictions",
                    "severity": "high",
                    "score": -20,
                    "matched_text": f"Longevity claims vs domain registered {age} days ago",
                    "reason": "The text claims a long corporate history or established foundation, but the registration age of the domain is less than 60 days.",
                    "evidence_type": "negative",
                    "confidence": 15,
                    "source": "Website Analyzer"
                })

        # 6. Legacy Official claims vs Website signals (New Domain or Missing SSL)
        is_official_claim = bool(re.search(
            r'\b(?:official\s+partner|government\s+approved|iso\s+certified|fortune\s+500|established\s+multinational|mnc|verified\s+employer)\b', 
            text, re.IGNORECASE
        ))
        
        if is_official_claim and website_data:
            whois = website_data.get("whois")
            ssl = website_data.get("ssl")

            # Check if domain is extremely young (< 90 days) but not already flagged
            if whois and whois.get("domain_age_days") is not None and whois.get("domain_age_days") < 90:
                # Avoid duplicates with history claims
                if not any(item["id"] == "history_vs_domain_age_contradiction" for item in evidence):
                    msg = f"Established company claims made, but the domain age is only {whois.get('domain_age_days')} days."
                    contradictions.append(msg)
                    evidence.append({
                        "id": "claim_vs_domain_age_contradiction",
                        "rule_id": "CON_006",
                        "title": "Corporate Age Mismatch",
                        "category": "contradictions",
                        "severity": "high",
                        "score": -15,
                        "matched_text": f"Established claims vs WHOIS age {whois.get('domain_age_days')} days",
                        "reason": "The posting claims to represent an established corporate entity, but the website domain was registered very recently. Reputable organizations use mature domains.",
                        "evidence_type": "negative",
                        "confidence": 10,
                        "source": "Website Analyzer"
                    })

            # Check if SSL HTTPS is missing (only if website is reachable and not already flagged for https vs ssl)
            is_reachable = whois and not whois.get("whois_failed", True)
            if is_reachable and ssl and not ssl.get("has_valid_ssl"):
                if not any(item["id"] == "https_vs_ssl_fail_contradiction" for item in evidence):
                    msg = "Official corporate claims made, but the website lacks active SSL/HTTPS encryption."
                    contradictions.append(msg)
                    evidence.append({
                        "id": "claim_vs_ssl_contradiction",
                        "rule_id": "CON_007",
                        "title": "Security Protocol Contradiction",
                        "category": "contradictions",
                        "severity": "medium",
                        "score": 0,
                        "matched_text": "Official claims vs HTTP connection",
                        "reason": "The description claims high corporate credentials, but the domain lacks a valid SSL certificate. Official corporate portals always enforce secure HTTPS connections.",
                        "evidence_type": "negative",
                        "confidence": 10,
                        "source": "Website Analyzer"
                    })

        return {
            "contradictions": contradictions,
            "evidence": evidence
        }
