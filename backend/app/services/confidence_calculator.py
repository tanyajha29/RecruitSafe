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
        Evaluates the input quality score (0-100) based on text structure and completeness.
        Returns the score and a list of missing fields.
        """
        missing = []
        score = 0
        
        if not text:
            return 0, ["Company Name", "Job Title", "Responsibilities", "Requirements", "Salary Details", "Benefits", "Hiring Process", "Contact Details", "Website"]

        words = text.split()

        # 1. Company Name
        company_keywords = r'\b(?:company|employer|firm|agency|corporation|organization|inc|ltd|pvt|private)\b'
        if re.search(company_keywords, text, re.IGNORECASE):
            score += 10
        else:
            missing.append("Company Name")

        # 2. Job Title
        role_keywords = r'\b(?:role|position|developer|assistant|manager|associate|designer|engineer|executive|intern|fresher|helper|clerk|fitter|writer|internship)\b'
        if re.search(role_keywords, text, re.IGNORECASE):
            score += 10
        else:
            missing.append("Job Title")

        # 3. Responsibilities
        resp_keywords = r'\b(?:responsibilities|duties|role\s+and\s+responsibilities|what\s+you\s+will\s+do|key\s+tasks|tasks|undertake)\b'
        if re.search(resp_keywords, text, re.IGNORECASE):
            score += 15
        else:
            missing.append("Responsibilities")

        # 4. Requirements
        req_keywords = r'\b(?:requirements|qualifications|skills|what\s+you\s+need|experience|skills\s+required|must\s+have|pre-requisites)\b'
        if re.search(req_keywords, text, re.IGNORECASE):
            score += 15
        else:
            missing.append("Requirements")

        # 5. Salary Details
        salary_keywords = r'\b(?:salary|stipend|package|lpa|lakh|pm|p\.m\.|pay|earn|compensation|remuneration|wage)\b'
        if re.search(salary_keywords, text, re.IGNORECASE):
            score += 10
        else:
            missing.append("Salary Details")

        # 6. Benefits
        benefits_keywords = r'\b(?:benefits|perks|insurance|equity|pto|health\s+insurance|medical|bonus|wfh|remote\s+work)\b'
        if re.search(benefits_keywords, text, re.IGNORECASE):
            score += 10
        else:
            missing.append("Benefits")

        # 7. Hiring Process
        process_keywords = r'\b(?:interview|selection|hiring\s+process|round|screening|assessment|test|callback|onboarding)\b'
        if re.search(process_keywords, text, re.IGNORECASE):
            score += 10
        else:
            missing.append("Hiring Process")

        # 8. Contact Details
        email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        phone_pattern = r'\b(?:\+?\d{1,3}[- ]?)?\d{10}\b'
        has_contact = has_email or bool(re.search(email_pattern, text)) or bool(re.search(phone_pattern, text))
        if has_contact:
            score += 5
        else:
            missing.append("Contact Details")

        # 9. Website
        if has_url or bool(re.search(r'https?://[^\s/$.?#].[^\s]*', text)):
            score += 5
        else:
            missing.append("Website Link")

        # 10. Formatting (headings/paragraphs)
        has_headings = bool(re.search(r'(?:[A-Z][A-Za-z\s]{3,15}:|\n[A-Z\s]{4,12}\n)', text))
        if has_headings:
            score += 5
        else:
            missing.append("Section Headings / Structure")

        # 11. Length (words > 100)
        if len(words) > 100:
            score += 5
        else:
            missing.append("Sufficient Word Count (>100 words)")

        # 12. Professional Structure (bullet points, clear lists)
        has_bullets = bool(re.search(r'(?:•|\*|-|\d\.)\s', text))
        if has_bullets:
            score += 5
        else:
            missing.append("List / Bullet Formatting")

        return max(0, min(100, score)), missing

    @classmethod
    def detect_missing_information(cls, text: str, has_email: bool, has_url: bool) -> List[str]:
        """
        Legacy wrapper returning missing details list for backwards compatibility.
        """
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
        agreement_score: int
    ) -> int:
        """
        Calculates a confidence score between 0 and 100.
        Measures certainty/completeness, NOT risk.
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
        if has_website:
            is_reachable = not website_data.get("whois", {}).get("whois_failed", True) or website_data.get("ssl", {}).get("has_valid_ssl", False)
            if is_reachable:
                confidence += 10

        # 3. Company identified +10
        company_keywords = r'\b(?:company|employer|firm|agency|corporation|organization|inc|ltd|pvt|private)\b'
        has_company_name = bool(re.search(company_keywords, text, re.IGNORECASE))
        has_corp_email = email_data and not email_data.get("is_free_email", True)
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

        # 6. Professional formatting +5
        has_bullets = bool(re.search(r'(?:•|\*|-|\d\.)\s', text))
        has_headings = bool(re.search(r'(?:[A-Z][A-Za-z\s]{3,15}:|\n[A-Z\s]{4,12}\n)', text))
        if has_bullets or has_headings:
            confidence += 5

        # 7. AI and Rule Agreement +10
        if agreement_score >= 80:
            confidence += 10

        # 8. Website unavailable -10
        if has_website and not is_reachable:
            confidence -= 10

        # 9. Very short input -20
        if word_count < 30:
            confidence -= 20

        # 10. OCR failure -15
        if ocr_performed:
            non_alphanumeric = len(re.sub(r'[a-zA-Z0-9\s.,!?@:;/-]', '', text))
            garbage_ratio = non_alphanumeric / len(text) if len(text) > 0 else 0.0
            if garbage_ratio > 0.15:
                confidence -= 15

        return max(0, min(100, confidence))
