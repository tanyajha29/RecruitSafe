import re
import logging
from typing import Dict, Any, List, Optional
from app.services.extraction.pipeline import CanonicalExtractionPipeline

logger = logging.getLogger("recruitsafe")

class StructuredExtractor:
    """
    Deterministic regex, label, and section-aware entity extraction pipeline.
    Delegates execution to the modular 3-layer CanonicalExtractionPipeline architecture.
    """

    @classmethod
    def clean_extracted_value(cls, val: str) -> str:
        if not val:
            return ""
        cleaned = val.strip()
        noise_patterns = [
            r'^(?:we\s+are\s+)?looking\s+for\s+(?:a\s+|an\s+|the\s+)?',
            r'^(?:we\s+are\s+)?seeking\s+(?:a\s+|an\s+|the\s+)?',
            r'^(?:we\s+are\s+)?hiring\s+for\s+(?:a\s+|an\s+|the\s+)?',
            r'^(?:we\s+are\s+)?hiring\s+(?:a\s+|an\s+|the\s+)?'
        ]
        for pat in noise_patterns:
            cleaned = re.sub(pat, '', cleaned, flags=re.IGNORECASE).strip()
        cleaned = cleaned.strip('"\' \t\n\r:-')
        
        # Strip trailing dot if not preceded by Ltd, Inc, Corp, Co, Pvt
        if cleaned.endswith('.'):
            abbrs = ["ltd.", "inc.", "corp.", "co.", "pvt."]
            if not any(cleaned.lower().endswith(a) for a in abbrs):
                cleaned = cleaned[:-1].strip()
        return cleaned

    @classmethod
    def parse_sections(cls, text: str) -> Dict[str, str]:
        lines = text.split('\n')
        sections = {}
        current_header = "Intro"
        current_lines = []

        header_pattern = re.compile(
            r'^(?:required\s+skills|skills|technologies|requirements|qualifications|experience|education|degree|benefits|perks|hiring\s+process|interview|selection|about\s+us|responsibilities|duties)\b',
            re.IGNORECASE
        )

        for line in lines:
            cleaned = line.strip()
            if not cleaned:
                continue
            is_header = False
            if len(cleaned) < 50:
                if header_pattern.search(cleaned) or (cleaned.endswith(':') and len(cleaned) < 30):
                    is_header = True
            
            if is_header:
                if current_lines:
                    sections[current_header] = "\n".join(current_lines).strip()
                current_header = cleaned.rstrip(':').strip()
                current_lines = []
            else:
                current_lines.append(line)
        
        if current_lines:
            sections[current_header] = "\n".join(current_lines).strip()
            
        return sections

    @classmethod
    def extract_by_label(cls, text: str, label_keywords: List[str]) -> Optional[str]:
        for keyword in label_keywords:
            inline_pattern = r'(?:^|\n)\s*(?:\*\*)?' + re.escape(keyword) + r'(?:\*\*)?\s*[:-]\s*([^\n]+)'
            match = re.search(inline_pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                val = cls.clean_extracted_value(match.group(1))
                if val.lower() not in ["unspecified company", "recruitment outreach", "not disclosed"]:
                    return val
                
            next_line_pattern = r'(?:^|\n)\s*(?:\*\*)?' + re.escape(keyword) + r'(?:\*\*)?\s*[:-]\s*\n\s*([^\n]+)'
            match = re.search(next_line_pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                val = cls.clean_extracted_value(match.group(1))
                if val.lower() not in ["unspecified company", "recruitment outreach", "not disclosed"]:
                    return val
        return None

    @classmethod
    def extract_all(cls, text: str, original_content: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        raw_text = text or original_content or ""
        return CanonicalExtractionPipeline.run_pipeline(raw_text)
