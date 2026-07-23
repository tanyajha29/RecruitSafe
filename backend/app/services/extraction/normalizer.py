import re
from typing import Dict, Any, Optional
from app.services.extraction.models import CanonicalEntity, StatusEnum

FREE_DOMAINS = {
    "gmail.com", "yahoo.com", "yahoo.co.in", "outlook.com", "hotmail.com", 
    "aol.com", "zoho.com", "mail.com", "yandex.com", "protonmail.com",
    "proton.me", "gmx.com", "icloud.com", "mail.ru", "live.com"
}

DISPOSABLE_DOMAINS = {
    "mailinator.com", "10minutemail.com", "tempmail.com", "guerrillamail.com",
    "sharklasers.com", "dispostable.com", "yopmail.com", "trashmail.com"
}

class Normalizer:
    """
    Layer 2: Normalizer.
    Normalizes extracted entities without altering the raw `value`.
    Populates `normalized_value`, entity-specific `metadata`, and sets status to 'normalized'.
    """

    @classmethod
    def normalize_employment_type(cls, entity: CanonicalEntity) -> CanonicalEntity:
        if entity.value == "Unknown" or not entity.value:
            return entity

        val_lower = str(entity.value).lower()
        norm = "OTHER"
        if "full" in val_lower:
            norm = "FULL_TIME"
        elif "part" in val_lower:
            norm = "PART_TIME"
        elif "intern" in val_lower:
            norm = "INTERNSHIP"
        elif "contract" in val_lower:
            norm = "CONTRACT"
        elif "free" in val_lower or "self" in val_lower:
            norm = "FREELANCE"

        entity.normalized_value = norm
        entity.status = StatusEnum.NORMALIZED.value
        return entity

    @classmethod
    def normalize_location(cls, entity: CanonicalEntity, entities_dict: Dict[str, CanonicalEntity]) -> CanonicalEntity:
        if entity.value == "Unknown" or not entity.value:
            return entity

        val_str = str(entity.value)
        val_lower = val_str.lower()

        work_mode = "ONSITE"
        if "remote" in val_lower:
            work_mode = "REMOTE"
        elif "hybrid" in val_lower:
            work_mode = "HYBRID"

        meta: Dict[str, Any] = {"work_mode": work_mode}

        # Check sub-region e.g., Remote (India)
        country_match = re.search(r'\(([^)]+)\)', val_str)
        if country_match:
            c_val = country_match.group(1).strip()
            meta["country"] = c_val
            if entities_dict.get("country") and entities_dict["country"].value == "Unknown":
                entities_dict["country"].value = c_val
                entities_dict["country"].normalized_value = c_val.upper()
                entities_dict["country"].status = StatusEnum.NORMALIZED.value

        for city_name in ["Mumbai", "Bangalore", "Bengaluru", "Delhi", "New Delhi", "Pune", "Hyderabad", "Chennai", "Kolkata", "San Francisco", "New York", "Seattle", "Austin"]:
            if city_name.lower() in val_lower:
                meta["city"] = city_name
                if entities_dict.get("city") and entities_dict["city"].value == "Unknown":
                    entities_dict["city"].value = city_name
                    entities_dict["city"].normalized_value = city_name.upper()
                    entities_dict["city"].status = StatusEnum.NORMALIZED.value

        entity.normalized_value = work_mode
        entity.metadata.update(meta)
        entity.status = StatusEnum.NORMALIZED.value

        # Populate standalone work_mode entity if empty
        if entities_dict.get("work_mode") and entities_dict["work_mode"].value == "Unknown":
            entities_dict["work_mode"].value = work_mode.title()
            entities_dict["work_mode"].normalized_value = work_mode
            entities_dict["work_mode"].status = StatusEnum.NORMALIZED.value

        return entity

    @classmethod
    def normalize_salary(cls, entity: CanonicalEntity, entities_dict: Dict[str, CanonicalEntity]) -> CanonicalEntity:
        if entity.value == "Unknown" or not entity.value:
            return entity

        val_str = str(entity.value)
        val_lower = val_str.lower()

        # Detect currency
        curr = "USD"
        curr_symbol = "$"
        if "₹" in val_str or "inr" in val_lower or "lakh" in val_lower or "lpa" in val_lower:
            curr = "INR"
            curr_symbol = "₹"
        elif "€" in val_str or "eur" in val_lower:
            curr = "EUR"
            curr_symbol = "€"
        elif "£" in val_str or "gbp" in val_lower:
            curr = "GBP"
            curr_symbol = "£"

        # Detect period
        period = "YEARLY"
        if any(p in val_lower for p in ["pm", "p.m.", "month", "monthly"]):
            period = "MONTHLY"
        elif any(p in val_lower for p in ["hr", "hour", "hourly"]):
            period = "HOURLY"

        # Parse numbers & LPA multiplier
        minimum = None
        maximum = None
        is_range = False

        # Check LPA range regex e.g. 8L-11L or 8LPA or 8 Lakhs
        lpa_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakhs?|lpa|l\b)?\s*(?:-|to|–)\s*(\d+(?:\.\d+)?)\s*(?:lakhs?|lpa|l\b)', val_lower)
        if lpa_match:
            g1 = float(lpa_match.group(1))
            g2 = float(lpa_match.group(2))
            minimum = int(g1 * 100000)
            maximum = int(g2 * 100000)
            is_range = True
        else:
            single_lpa = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakhs?|lpa|l\b)', val_lower)
            if single_lpa:
                g1 = float(single_lpa.group(1))
                minimum = int(g1 * 100000)
                maximum = minimum
                is_range = False
            else:
                nums = re.findall(r'\b\d+(?:,\d+)*\b', val_str)
                parsed = []
                for n in nums:
                    try:
                        parsed.append(int(n.replace(',', '')))
                    except ValueError:
                        pass
                if parsed:
                    if len(parsed) >= 2:
                        minimum = min(parsed)
                        maximum = max(parsed)
                        is_range = True
                    else:
                        minimum = parsed[0]
                        maximum = parsed[0]

        meta = {
            "currency": curr_symbol,
            "normalized_currency": curr,
            "period": period,
            "minimum": minimum,
            "maximum": maximum,
            "is_range": is_range
        }

        entity.metadata.update(meta)
        entity.normalized_value = f"{minimum}-{maximum}" if is_range else str(minimum if minimum else val_str)
        entity.status = StatusEnum.NORMALIZED.value

        # Populate standalone currency & salary_period entities
        if entities_dict.get("currency") and entities_dict["currency"].value == "Unknown":
            entities_dict["currency"].value = curr_symbol
            entities_dict["currency"].normalized_value = curr
            entities_dict["currency"].status = StatusEnum.NORMALIZED.value

        if entities_dict.get("salary_period") and entities_dict["salary_period"].value == "Unknown":
            entities_dict["salary_period"].value = period.title()
            entities_dict["salary_period"].normalized_value = period
            entities_dict["salary_period"].status = StatusEnum.NORMALIZED.value

        return entity

    @classmethod
    def normalize_email(cls, entity: CanonicalEntity) -> CanonicalEntity:
        if entity.value == "Unknown" or not entity.value:
            return entity

        val_str = str(entity.value).strip().lower()
        domain = val_str.split('@')[-1] if '@' in val_str else ""
        is_free = domain in FREE_DOMAINS
        is_disposable = domain in DISPOSABLE_DOMAINS

        entity.normalized_value = val_str
        entity.metadata.update({
            "domain": domain,
            "is_free": is_free,
            "is_disposable": is_disposable,
            "mx_found": False,
            "spf_found": False,
            "dmarc_found": False,
            "dkim_found": False
        })
        entity.status = StatusEnum.NORMALIZED.value
        return entity

    @classmethod
    def normalize_website(cls, entity: CanonicalEntity) -> CanonicalEntity:
        if entity.value == "Unknown" or not entity.value:
            return entity

        val_str = str(entity.value).strip()
        has_https = val_str.lower().startswith("https://")
        domain_match = re.search(r'(?:https?://)?([^/:\s]+)', val_str, re.IGNORECASE)
        domain = domain_match.group(1).lower() if domain_match else ""

        entity.normalized_value = val_str if val_str.startswith("http") else f"https://{val_str}"
        entity.metadata.update({
            "domain": domain,
            "https": has_https,
            "reachable": False,
            "redirects": False,
            "domain_age": None,
            "ssl_valid": False
        })
        entity.status = StatusEnum.NORMALIZED.value
        return entity

    @classmethod
    def normalize_all(cls, entities: Dict[str, CanonicalEntity]) -> Dict[str, CanonicalEntity]:
        for key, entity in entities.items():
            if entity.value == "Unknown" or not entity.value:
                continue

            if key == "employment_type":
                cls.normalize_employment_type(entity)
            elif key == "location":
                cls.normalize_location(entity, entities)
            elif key == "salary":
                cls.normalize_salary(entity, entities)
            elif key == "recruiter_email":
                cls.normalize_email(entity)
            elif key == "website":
                cls.normalize_website(entity)
            else:
                if entity.status == StatusEnum.EXTRACTED.value:
                    entity.normalized_value = entity.value
                    entity.status = StatusEnum.NORMALIZED.value

        return entities
