import re
from typing import Dict, Any, List, Optional

class ConfidenceCalculator:
    """
    Computes a 0-100 Confidence Score based on positive data resolution
    signals and negative data constraint factors.
    Also detects missing information blocks in job posts.
    """

    @classmethod
    def detect_missing_information(cls, text: str, has_email: bool, has_url: bool) -> List[str]:
        """
        Scans text for crucial job listing parameters.
        Returns a list of missing information items.
        """
        missing = []
        if not text:
            return ["Job Description Text", "Company Name", "Job Role / Title", "Salary Details", "Contact Channel"]

        words = text.split()
        
        # 1. Check for extreme short text
        if len(words) < 20:
            missing.append("Sufficient job details (too short)")

        # 2. Check for company name references
        company_keywords = r'\b(?:company|employer|firm|agency|corporation|organization|inc|ltd|pvt|private)\b'
        if not re.search(company_keywords, text, re.IGNORECASE):
            missing.append("Company Name / Corporate Reference")

        # 3. Check for job titles/roles
        role_keywords = r'\b(?:role|position|developer|assistant|manager|associate|designer|engineer|executive|intern|fresher|helper|clerk|fitter|writer|internship)\b'
        if not re.search(role_keywords, text, re.IGNORECASE):
            missing.append("Job Role / Position Title")

        # 4. Check for salary terms
        salary_keywords = r'\b(?:salary|stipend|package|lpa|lakh|pm|p\.m\.|pay|earn|compensation|remuneration)\b'
        if not re.search(salary_keywords, text, re.IGNORECASE):
            missing.append("Salary / Compensation Range")

        # 5. Check for contact channel
        email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        phone_pattern = r'\b(?:\+?\d{1,3}[- ]?)?\d{10}\b'
        has_contact_in_text = bool(re.search(email_pattern, text)) or bool(re.search(phone_pattern, text))
        
        if not (has_email or has_url or has_contact_in_text):
            missing.append("Contact Channel (Email, URL, or Phone)")

        return missing

    @classmethod
    def calculate_confidence(cls, text: str, email_data: Optional[Dict], website_data: Optional[Dict], ocr_performed: bool, missing_info: List[str]) -> int:
        """
        Calculates a confidence score between 0 and 100.
        Uses positive signals to increase and negative signals to decrease confidence.
        """
        if not text:
            return 0

        # Start with a base confidence score
        confidence = 70
        word_count = len(text.split())

        # --- Positive Components (Confirmations) ---
        # Long, detailed descriptions increase confidence
        if word_count > 150:
            confidence += 15
        elif word_count > 80:
            confidence += 5

        # Domain resolution success
        if website_data and website_data.get("whois") and not website_data["whois"].get("whois_failed"):
            confidence += 5
        
        # Valid SSL connection
        if website_data and website_data.get("ssl") and website_data["ssl"].get("has_valid_ssl"):
            confidence += 5

        # Email domain validation
        if email_data and email_data.get("domain_exists"):
            confidence += 5

        # --- Negative Components (Reductions) ---
        # Extremely short descriptions decrease confidence heavily
        if word_count < 30:
            confidence -= 25
        elif word_count < 60:
            confidence -= 10

        # OCR character corruption checks
        if ocr_performed:
            # Check ratio of non-alphanumeric/garbage characters in text
            non_alphanumeric = len(re.sub(r'[a-zA-Z0-9\s.,!?@:;/-]', '', text))
            garbage_ratio = non_alphanumeric / len(text) if len(text) > 0 else 0.0
            if garbage_ratio > 0.15:
                confidence -= 20
                logger.warning(f"High OCR garbage character ratio: {garbage_ratio:.2f}. Reducing confidence.")

        # Website details requested but failed
        if website_data and (website_data.get("whois", {}).get("whois_failed") or not website_data.get("ssl", {}).get("has_valid_ssl")):
            confidence -= 10

        # Email domain DNS check failed (domain doesn't exist)
        if email_data and not email_data.get("domain_exists"):
            confidence -= 15

        # Deduct for each missing layer of crucial information
        confidence -= len(missing_info) * 8

        # Clamp between 0 and 100
        return max(0, min(100, confidence))
