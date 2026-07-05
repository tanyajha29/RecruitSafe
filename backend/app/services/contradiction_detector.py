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
                    "title": "Domain Typosquatting Contradiction",
                    "category": "contradictions",
                    "severity": "high",
                    "score": -20,
                    "description": f"Recruiter is contacting from an unofficial lookalike domain ({email_data.get('domain')}) that matches typosquatting patterns for the target company. Fraudulent actors register lookalikes to spoof official HR departments.",
                    "matched_text": email_data.get('domain'),
                    "explanation": "The recruiter's email domain has a Levenshtein distance <= 3 or contains the company name with an unofficial suffix, indicating spoofing."
                })

        # 2. Official claims vs Website signals (New Domain or Missing SSL)
        # Search for official/established corporate claims
        is_official_claim = bool(re.search(
            r'\b(?:official\s+partner|government\s+approved|iso\s+certified|fortune\s+500|established\s+multinational|mnc|verified\s+employer)\b', 
            text, re.IGNORECASE
        ))
        
        if is_official_claim and website_data:
            whois = website_data.get("whois")
            ssl = website_data.get("ssl")

            # Check if domain is extremely young (< 90 days)
            if whois and whois.get("domain_age_days") is not None and whois.get("domain_age_days") < 90:
                msg = f"Established company claims made, but the domain age is only {whois.get('domain_age_days')} days."
                contradictions.append(msg)
                evidence.append({
                    "id": "claim_vs_domain_age_contradiction",
                    "title": "Corporate Age Mismatch",
                    "category": "contradictions",
                    "severity": "high",
                    "score": -15,
                    "description": "The posting claims to represent an established corporate entity, but the website domain was registered very recently. Reputable organizations use mature domains.",
                    "matched_text": f"Established claims vs WHOIS age {whois.get('domain_age_days')} days",
                    "explanation": "Established corporate entities do not host registration portals on newly registered domains (<90 days)."
                })

            # Check if SSL HTTPS is missing
            if ssl and not ssl.get("has_valid_ssl"):
                msg = "Official corporate claims made, but the website lacks active SSL/HTTPS encryption."
                contradictions.append(msg)
                evidence.append({
                    "id": "claim_vs_ssl_contradiction",
                    "title": "Security Protocol Contradiction",
                    "category": "contradictions",
                    "severity": "medium",
                    "score": -15,
                    "description": "The description claims high corporate credentials, but the domain lacks a valid SSL certificate. Official corporate portals always enforce secure HTTPS connections.",
                    "matched_text": "Official claims vs HTTP connection",
                    "explanation": "Established corporate recruitment portals do not transmit credentials over unencrypted (HTTP) channels."
                })

        return {
            "contradictions": contradictions,
            "evidence": evidence
        }
