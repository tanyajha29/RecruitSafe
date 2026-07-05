import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("recruitsafe")

class SalaryAnalyzer:
    """
    Analyzes job description texts to identify offered salary ranges
    and evaluates their legitimacy based on experience level and location rules.
    """
    
    # Matches LPA, Lakhs, USD, K, per month, etc.
    SALARY_REGEXES = [
        # Match LPA range, e.g., 5-12 LPA
        r'(?:₹|\$)?\s*([\d,]+(?:\.\d+)?)\s*(?:-|to)\s*([\d,]+(?:\.\d+)?)\s*(?:LPA|L\s*P\s*A|lakhs?\s*p\.a\.|lacs?\s*p\.a\.)',
        # Match single LPA, e.g., 25 LPA, 12 LPA
        r'(?:₹|\$)?\s*([\d,]+(?:\.\d+)?)\s*(?:LPA|L\s*P\s*A|lakhs?\s*p\.a\.|lacs?\s*p\.a\.)\b',
        # Match Lakhs, e.g., ₹5 Lakhs, 8 Lakhs
        r'(?:₹|\$)?\s*([\d,]+(?:\.\d+)?)\s*(?:lakhs?|lacs?|l)\b',
        # Match monthly, e.g., 2,00,000 per month, 15000/month, ₹50,000 pm
        r'(?:₹|\$)?\s*([\d,]+(?:\.\d+)?|\d+(?:\.\d+)?\s*(?:lakh|lac|k|thousand))\s*(?:per\s*month|\/month|\/mo|\/m|pm|p\.m\.)'
    ]

    @staticmethod
    def _clean_numeric(value_str: str) -> float:
        """Helper to parse raw text digits to float."""
        clean = re.sub(r'[^\d.]', '', value_str)
        try:
            return float(clean)
        except ValueError:
            return 0.0

    @classmethod
    def extract_salary(cls, text: str) -> Optional[Dict[str, Any]]:
        """
        Parses offered salary numbers, units, and intervals from the text.
        """
        for regex in cls.SALARY_REGEXES:
            matches = re.findall(regex, text, re.IGNORECASE)
            if matches:
                match = matches[0]
                # If it matches the range regex, we have (min, max)
                if isinstance(match, tuple) and len(match) == 2:
                    min_val = cls._clean_numeric(match[0])
                    max_val = cls._clean_numeric(match[1])
                    return {
                        "type": "range",
                        "min": min_val,
                        "max": max_val,
                        "interval": "annual",
                        "matched_text": f"{match[0]} - {match[1]} LPA"
                    }
                else:
                    # Single value match (monthly or absolute Lakhs)
                    val_str = str(match).lower().strip()
                    val = cls._clean_numeric(val_str)
                    
                    # Convert terms like '2 lakh' to numeric value
                    if "lakh" in val_str or "lac" in val_str:
                        # Extract multiplier
                        multiplier_match = re.search(r'(\d+(?:\.\d+)?)', val_str)
                        multiplier = float(multiplier_match.group(1)) if multiplier_match else 1.0
                        val = multiplier * 100000
                    elif "k" in val_str:
                        multiplier_match = re.search(r'(\d+(?:\.\d+)?)', val_str)
                        multiplier = float(multiplier_match.group(1)) if multiplier_match else 1.0
                        val = multiplier * 1000
                    elif "thousand" in val_str:
                        multiplier_match = re.search(r'(\d+(?:\.\d+)?)', val_str)
                        multiplier = float(multiplier_match.group(1)) if multiplier_match else 1.0
                        val = multiplier * 1000
                        
                    # Check interval
                    if any(term in text.lower() for term in ["per month", "/month", "/mo", "pm", "p.m."]):
                        return {
                            "type": "fixed",
                            "value": val,
                            "interval": "monthly",
                            "matched_text": val_str
                        }
                    else:
                        # Fallback to annual Lakhs
                        return {
                            "type": "fixed",
                            "value": val,
                            "interval": "annual",
                            "matched_text": val_str
                        }
        return None

    @classmethod
    def analyze_salary(cls, text: str) -> Dict[str, Any]:
        """
        Evaluates salary correctness relative to the experience level detected in text.
        Returns:
            dict containing:
                evidence: list of Evidence dicts
                positive_findings: list of positive findings dicts
                salary_details: debug metadata dict
        """
        evidence = []
        positive_findings = []
        
        salary_info = cls.extract_salary(text)
        if not salary_info:
            return {
                "evidence": [],
                "positive_findings": [],
                "salary_details": None
            }

        # Detect experience keywords
        is_fresher = bool(re.search(r'\b(?:fresher|intern|entry\s*level|trainee|junior|graduate)\b', text, re.IGNORECASE))
        is_senior = bool(re.search(r'\b(?:senior|lead|architect|manager|head|experienced)\b', text, re.IGNORECASE))
        
        interval = salary_info["interval"]
        matched_str = salary_info["matched_text"]
        
        if interval == "monthly":
            monthly_val = salary_info["value"]
            annual_val = monthly_val * 12
        else:
            # Annual or Lakhs
            val = salary_info.get("value")
            if val is not None:
                if val < 100:  # e.g., "5 lakhs" where val parses as 5
                    annual_val = val * 100000
                else:
                    annual_val = val
            else:
                # Range
                annual_val = salary_info["max"]
                if annual_val < 100:
                    annual_val = annual_val * 100000
            
            monthly_val = annual_val / 12

        # 1. Unrealistic Fresher/Intern Salary Check
        if is_fresher and (monthly_val >= 150000 or annual_val >= 1800000):
            evidence.append({
                "id": "unrealistic_fresher_salary",
                "title": "Unrealistic Fresher Salary Offer",
                "category": "unrealistic_offers",
                "severity": "high",
                "score": -25,
                "description": f"The job post target entry-level freshers/interns but offers an inflated salary of ₹{monthly_val:,.0f}/month. Legitimate entry positions rarely pay such premiums upfront, indicating a potential recruitment lure.",
                "matched_text": matched_str,
                "explanation": f"Offered salary (₹{monthly_val:,.0f}/month) exceeds the entry-level market ceiling of ₹1.25L/month by more than 20%."
            })
        
        # 2. Senior Realistic Salary Check
        elif is_senior and (1000000 <= annual_val <= 4500000):
            positive_findings.append({
                "id": "realistic_senior_salary",
                "title": "Realistic Professional Compensation",
                "category": "salary_intelligence",
                "severity": "low",
                "score": 5,
                "description": f"The offered compensation ({matched_str}) aligns precisely with market standard benchmarks for senior corporate roles.",
                "matched_text": matched_str,
                "explanation": f"Offered salary equivalent (₹{annual_val/100000:.1f} LPA) falls within standard senior dev bounds (10-45 LPA)."
            })
            
        # 3. Fresher Normal Range Check (Bonus)
        elif is_fresher and (300000 <= annual_val <= 1200000):
            positive_findings.append({
                "id": "realistic_fresher_salary",
                "title": "Realistic Entry-Level Compensation",
                "category": "salary_intelligence",
                "severity": "low",
                "score": 5,
                "description": f"The offered salary of {matched_str} is within reasonable boundaries for a junior or trainee position.",
                "matched_text": matched_str,
                "explanation": f"Offered salary equivalent (₹{annual_val/100000:.1f} LPA) matches normal junior developer bounds (3-12 LPA)."
            })

        return {
            "evidence": evidence,
            "positive_findings": positive_findings,
            "salary_details": {
                "monthly_value": monthly_val,
                "annual_value": annual_val,
                "is_fresher": is_fresher,
                "is_senior": is_senior,
                "matched_text": matched_str
            }
        }
