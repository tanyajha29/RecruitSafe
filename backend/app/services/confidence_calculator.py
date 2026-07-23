import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("recruitsafe")

class ConfidenceCalculator:
    """
    Computes a 0-100 Confidence Score based on positive data resolution
    signals and negative data constraint factors.
    Also calculates the Input Quality Score and tracks missing fields.
    """

    @classmethod
    def calculate_input_quality(cls, text: str, has_email: bool, has_url: bool) -> Tuple[int, List[str]]:
        """
        Evaluates the input quality score (0-100) based on weighted information completeness.
        Returns:
            score: 0-100 quality score
            missing: List of missing fields
        """
        missing = []
        score = 0
        
        if not text:
            return 0, [
                "Company Name", "Job Title", "Salary Details", "Location", 
                "Responsibilities", "Requirements", "Benefits", "Hiring Process", 
                "Contact Details", "Website URL", "Company Description"
            ]

        # 1. Company Name (10 pts)
        company_keywords = r'\b(?:company|employer|firm|agency|corporation|organization|inc|ltd|pvt|private)\b'
        if re.search(company_keywords, text, re.IGNORECASE):
            score += 10
        else:
            missing.append("Company Name")

        # 2. Job Title / Role (10 pts)
        role_keywords = r'\b(?:role|position|developer|assistant|manager|associate|designer|engineer|executive|intern|fresher|helper|clerk|fitter|writer|internship)\b'
        if re.search(role_keywords, text, re.IGNORECASE):
            score += 10
        else:
            missing.append("Job Title")

        # 3. Salary Details (10 pts)
        salary_keywords = r'\b(?:salary|stipend|package|lpa|lakh|pm|p\.m\.|pay|earn|compensation|remuneration|wage)\b'
        if re.search(salary_keywords, text, re.IGNORECASE):
            score += 10
        else:
            missing.append("Salary Details")

        # 4. Location (5 pts)
        location_keywords = r'\b(?:location|city|address|remote|hybrid|wfh|office|workplace|state|country|delhi|mumbai|bangalore|pune|hyderabad|noida|gurgaon)\b'
        if re.search(location_keywords, text, re.IGNORECASE):
            score += 5
        else:
            missing.append("Location")

        # 5. Responsibilities (15 pts)
        resp_keywords = r'\b(?:responsibilities|duties|role\s+and\s+responsibilities|what\s+you\s+will\s+do|key\s+tasks|tasks|undertake)\b'
        if re.search(resp_keywords, text, re.IGNORECASE):
            score += 15
        else:
            missing.append("Responsibilities")

        # 6. Requirements (15 pts)
        req_keywords = r'\b(?:requirements|qualifications|skills|what\s+you\s+need|experience|skills\s+required|must\s+have|pre-requisites)\b'
        if re.search(req_keywords, text, re.IGNORECASE):
            score += 15
        else:
            missing.append("Requirements")

        # 7. Benefits (10 pts)
        benefits_keywords = r'\b(?:benefits|perks|insurance|equity|pto|health\s+insurance|medical|bonus|wfh|remote\s+work)\b'
        if re.search(benefits_keywords, text, re.IGNORECASE):
            score += 10
        else:
            missing.append("Benefits")

        # 8. Hiring Process (15 pts)
        process_keywords = r'\b(?:interview|selection|hiring\s+process|round|screening|assessment|test|callback|onboarding)\b'
        if re.search(process_keywords, text, re.IGNORECASE):
            score += 15
        else:
            missing.append("Hiring Process")

        # 9. Contact Details (5 pts)
        email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        phone_pattern = r'\b(?:\+?\d{1,3}[- ]?)?\d{10}\b'
        has_contact = has_email or bool(re.search(email_pattern, text)) or bool(re.search(phone_pattern, text))
        if has_contact:
            score += 5
        else:
            missing.append("Contact Details")

        # 10. Website URL (5 pts)
        if has_url or bool(re.search(r'https?://[^\s/$.?#].[^\s]*', text)):
            score += 5
        else:
            missing.append("Website URL")

        # 11. Company Description (10 pts)
        desc_keywords = r'\b(?:about\s+us|who\s+we\s+are|our\s+vision|our\s+mission|established\s+in|founded\s+in|leading\s+provider|we\s+are\s+a|is\s+a\s+leading|leading\s+\w+\s+firm)\b'
        if re.search(desc_keywords, text, re.IGNORECASE):
            score += 10
        else:
            missing.append("Company Description")

        return max(0, min(100, score)), missing

    @classmethod
    def detect_missing_information(cls, text: str, has_email: bool, has_url: bool) -> List[str]:
        _, missing = cls.calculate_input_quality(text, has_email, has_url)
        return missing

    @classmethod
    def calculate_confidence(
        cls, 
        text: str, 
        email_data: Optional[Dict], 
        website_data: Optional[Dict], 
        ocr_performed: bool, 
        missing_info: List[str],
        agreement_score: Optional[int] = None
    ) -> int:
        """
        Calculates a confidence score between 0 and 100.
        Measures certainty/completeness, NOT risk.
        Unknown/Not Supplied details decrease confidence, not trust.
        """
        if not text:
            return 0

        # Start with a base confidence score of 50
        confidence = 50
        words = text.split()
        word_count = len(words)

        # 1. Detailed input +10
        if word_count > 150:
            confidence += 10

        # 2. Website reachable +10
        has_website = website_data is not None
        is_reachable = False
        whois_info = website_data.get("whois", {}) if has_website else {}
        ssl_info = website_data.get("ssl", {}) if has_website else {}
        dns_info = website_data.get("dns", {}) if has_website else {}
        
        if has_website:
            is_reachable = dns_info.get("resolves", False) or not whois_info.get("whois_failed", True)
            if is_reachable:
                confidence += 10

        # 3. Company identified +10
        company_keywords = r'\b(?:company|employer|firm|agency|corporation|organization|inc|ltd|pvt|private)\b'
        has_company_name = bool(re.search(company_keywords, text, re.IGNORECASE))
        has_corp_email = email_data and not email_data.get("is_free_email", True) and not email_data.get("is_disposable", True)
        if has_company_name or has_corp_email:
            confidence += 10

        # 4. Salary extracted +5
        salary_keywords = r'\b(?:salary|stipend|package|lpa|lakh|pm|p\.m\.|pay|earn|compensation)\b'
        if re.search(salary_keywords, text, re.IGNORECASE):
            confidence += 5

        # 5. Hiring process detected +5
        process_keywords = r'\b(?:interview|selection|hiring\s+process|round|screening|assessment)\b'
        if re.search(process_keywords, text, re.IGNORECASE):
            confidence += 5

        # 6. Formatting features +5
        has_bullets = bool(re.search(r'(?:•|\*|-|\d\.)\s', text))
        has_headings = bool(re.search(r'(?:[A-Z][A-Za-z\s]{3,15}:|\n[A-Z\s]{4,12}\n)', text))
        if has_bullets or has_headings:
            confidence += 5

        # 7. AI and Rule Agreement (Removed to make scores completely independent)
        pass

        # 8. Gaps & Unknown details decrease confidence, NOT trust
        if not has_website:
            confidence -= 10
        else:
            # WHOIS not found/failed
            if whois_info.get("whois_failed", True):
                confidence -= 15
            # SSL missing/invalid
            if not ssl_info.get("has_valid_ssl", False):
                confidence -= 10

        has_email = email_data and email_data.get("sender_email") != ""
        if not has_email:
            confidence -= 10
        else:
            if email_data.get("is_disposable") or not email_data.get("domain_exists"):
                confidence -= 20
            elif email_data.get("is_free_email"):
                confidence -= 15

        # 9. Very short input -20
        if word_count < 30:
            confidence -= 20

        # 10. OCR garbage -15
        if ocr_performed:
            non_alphanumeric = len(re.sub(r'[a-zA-Z0-9\s.,!?@:;/-]', '', text))
            garbage_ratio = non_alphanumeric / len(text) if len(text) > 0 else 0.0
            if garbage_ratio > 0.15:
                confidence -= 15

        return max(0, min(100, confidence))
