import re
from typing import Dict, Any, Tuple, Optional

class ExtractionValidator:
    """
    Validation layer for extracted entities. Validates formats,
    detects unrealistic/generic/placeholder values, normalizes formats,
    and adjusts extraction confidence before scoring.
    """

    @classmethod
    def validate_company_name(cls, val: str) -> Tuple[bool, int, str]:
        if not val or val.strip().lower() in ["unknown", "not found", "none", "company", "employer"]:
            return False, 0, "Unknown"
        
        # Must not contain hiring keywords as company name
        bad_keywords = ["hiring", "opportunity", "job opening", "vacancy", "careers", "apply now"]
        val_lower = val.lower()
        if any(kw in val_lower for kw in bad_keywords):
            return False, 0, "Unknown"
        
        return True, 100, val.strip()

    @classmethod
    def validate_job_title(cls, val: str) -> Tuple[bool, int, str]:
        if not val or val.strip().lower() in ["unknown", "not found", "none"]:
            return False, 0, "Unknown"
            
        # Real designation check
        val_lower = val.lower()
        if len(val) > 80:
            return False, 10, "Unknown"
            
        bad_phrases = ["we need", "apply now", "click here", "looking for", "join our team"]
        if any(ph in val_lower for ph in bad_phrases):
            return False, 10, "Unknown"
            
        return True, 100, val.strip()

    @classmethod
    def validate_salary(cls, val: str) -> Tuple[bool, int, str, Dict[str, Any]]:
        meta = {"is_range": False, "period": "yearly", "min": None, "max": None}
        if not val or val.strip().lower() in ["unknown", "not found", "none", "not disclosed", "not specified"]:
            return False, 0, "Unknown", meta

        val_clean = val.strip()
        val_lower = val_clean.lower()
        
        if any(x in val_lower for x in ["pm", "p.m.", "month", "monthly"]):
            meta["period"] = "monthly"
        elif any(x in val_lower for x in ["hr", "hour", "hourly"]):
            meta["period"] = "hourly"
        else:
            meta["period"] = "yearly"

        # Find numbers
        numbers = re.findall(r'\b\d+(?:,\d+)*\b', val_clean)
        parsed_nums = []
        for num in numbers:
            try:
                parsed_nums.append(float(num.replace(',', '')))
            except ValueError:
                pass

        if parsed_nums:
            if len(parsed_nums) >= 2:
                meta["is_range"] = True
                meta["min"] = min(parsed_nums)
                meta["max"] = max(parsed_nums)
            else:
                meta["min"] = parsed_nums[0]
                meta["max"] = parsed_nums[0]

            # Unrealistic values checks
            min_val = meta["min"]
            max_val = meta["max"]
            is_unrealistic = False

            if meta["period"] == "yearly":
                if min_val < 500 or max_val > 2000000:
                    is_unrealistic = True
            elif meta["period"] == "monthly":
                if min_val < 50 or max_val > 150000:
                    is_unrealistic = True
            elif meta["period"] == "hourly":
                if min_val < 2 or max_val > 2000:
                    is_unrealistic = True

            if is_unrealistic:
                return False, 20, val_clean, meta

        return True, 100, val_clean, meta

    @classmethod
    def validate_location(cls, val: str) -> Tuple[bool, int, str]:
        if not val or val.strip().lower() in ["unknown", "not found", "none"]:
            return False, 0, "Unknown"

        val_clean = val.strip()
        return True, 100, val_clean

    @classmethod
    def validate_employment_type(cls, val: str) -> Tuple[bool, int, str]:
        if not val or val.strip().lower() in ["unknown", "not found", "none"]:
            return False, 0, "Unknown"

        val_lower = val.strip().lower()
        if "full" in val_lower:
            return True, 100, "Full Time"
        elif "part" in val_lower:
            return True, 100, "Part Time"
        elif "intern" in val_lower:
            return True, 100, "Internship"
        elif "contract" in val_lower:
            return True, 100, "Contract"
        elif "free" in val_lower or "self" in val_lower:
            return True, 100, "Freelance"
            
        return True, 80, val.strip()

    @classmethod
    def validate_email(cls, val: str) -> Tuple[bool, int, str, Dict[str, Any]]:
        meta = {"is_free": False}
        if not val or val.strip().lower() in ["unknown", "not found", "none"]:
            return False, 0, "Unknown", meta

        val_clean = val.strip()
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_regex.match(val_clean):
            return False, 0, "Unknown", meta

        domain = val_clean.split('@')[-1].lower()
        free_domains = {
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", 
            "aol.com", "protonmail.com", "zoho.com", "icloud.com", "yandex.com"
        }
        if domain in free_domains:
            meta["is_free"] = True
            
        return True, 100, val_clean, meta

    @classmethod
    def validate_website(cls, val: str) -> Tuple[bool, int, str]:
        if not val or val.strip().lower() in ["unknown", "not found", "none"]:
            return False, 0, "Unknown"

        val_clean = val.strip().rstrip('.,;!?-/\\')
        if not re.match(r'^https?://', val_clean, re.IGNORECASE):
            val_clean = "https://" + val_clean

        domain_match = re.search(r'https?://([^/:\s]+)', val_clean, re.IGNORECASE)
        if not domain_match:
            return False, 0, "Unknown"
            
        domain = domain_match.group(1)
        if '.' not in domain or domain.endswith('.') or domain.startswith('.') or "localhost" in domain:
            return False, 0, "Unknown"

        return True, 100, val_clean

    @classmethod
    def validate_all(cls, structured_evidence: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        validated = {}
        for field, detail in structured_evidence.items():
            val = detail.get("value", "Unknown")
            status = detail.get("extraction_status", "not_found")
            source = detail.get("source", "None")
            conf = detail.get("confidence", 0)

            if status == "not_found" or val == "Unknown":
                validated[field] = detail
                continue

            is_valid = True
            adj_conf = conf
            cleaned_val = val
            meta = {}

            if field == "Company Name":
                is_valid, adj_conf, cleaned_val = cls.validate_company_name(val)
            elif field == "Job Title":
                is_valid, adj_conf, cleaned_val = cls.validate_job_title(val)
            elif field == "Salary":
                is_valid, adj_conf, cleaned_val, meta = cls.validate_salary(val)
            elif field == "Location":
                is_valid, adj_conf, cleaned_val = cls.validate_location(val)
            elif field == "Employment Type":
                is_valid, adj_conf, cleaned_val = cls.validate_employment_type(val)
            elif field == "Recruiter Email":
                is_valid, adj_conf, cleaned_val, meta = cls.validate_email(val)
            elif field == "Company Website":
                is_valid, adj_conf, cleaned_val = cls.validate_website(val)

            if not is_valid:
                validated[field] = {
                    "value": "Unknown",
                    "source": source,
                    "extraction_status": "not_found",
                    "confidence": adj_conf
                }
            else:
                validated[field] = {
                    "value": cleaned_val,
                    "source": source,
                    "extraction_status": "extracted",
                    "confidence": min(conf, adj_conf)
                }
                if meta:
                    validated[field]["metadata"] = meta

        for k, v in structured_evidence.items():
            if k not in validated:
                validated[k] = v

        return validated
