import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("recruitsafe")

class PsychologicalDetector:
    """
    Detects emotional manipulation and pressure tactics in job descriptions.
    Computes distinct Urgency and Pressure scores (0-100) and returns V2 evidence.
    """

    URGENCY_KEYWORDS = [
        r"\bwithin\s*(?:30\s*minutes|2\s*hours|24\s*hours|48\s*hours)\b",
        r"\bonly\s*today\b",
        r"\boffer\s*expires\s*today\b",
        r"\bapply\s*(?:immediately|today)\b",
        r"\burgent\s*(?:hiring|joining|requirement)\b",
        r"\bseats\s*filling\s*fast\b",
        r"\bhurry\s*up\b",
        r"\bquick\s*action\b",
        r"\blimited\s*(?:seats|spots|time)\b"
    ]

    PRESSURE_KEYWORDS = [
        r"\b100%\s*(?:placement|selection|guaranteed|job)\b",
        r"\bguaranteed\s*(?:job|placement|salary|selection)\b",
        r"\bspot\s*(?:joining|selection)\b",
        r"\bearn\s*(?:money|cash)\s*fast\b",
        r"\bmake\s*money\s*today\b",
        r"\bno\s*(?:interview|skills|experience|qualification)\s*required\b",
        r"\bdirect\s*joining\b",
        r"\bselection\s*assured\b",
        r"\binstant\s*(?:cash|payout)\b"
    ]

    @classmethod
    def analyze_manipulation(cls, text: str) -> Dict[str, Any]:
        """
        Computes Urgency and Pressure scores, returning V2 evidence if thresholds are crossed.
        """
        evidence = []
        
        if not text:
            return {
                "urgency_score": 0,
                "pressure_score": 0,
                "evidence": []
            }

        # Calculate word count for simple density scaling
        word_count = len(text.split()) or 1
        
        # 1. Calculate Urgency matches
        urgency_matches = []
        for pattern in cls.URGENCY_KEYWORDS:
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                urgency_matches.extend(found)
                
        # 2. Calculate Pressure matches
        pressure_matches = []
        for pattern in cls.PRESSURE_KEYWORDS:
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                pressure_matches.extend(found)

        # Scale scores: each unique pattern matched contributes 25 points, capped at 100
        unique_urgency_count = len(set([m.lower() for m in urgency_matches]))
        unique_pressure_count = len(set([m.lower() for m in pressure_matches]))
        
        urgency_score = min(100, unique_urgency_count * 25)
        pressure_score = min(100, unique_pressure_count * 25)

        # 3. Generate Evidence objects if thresholds are exceeded
        if urgency_score >= 50:
            evidence.append({
                "id": "high_urgency_tactics",
                "title": "Artificial Urgency Pressure",
                "category": "pressure_tactics",
                "severity": "medium",
                "score": -8,
                "description": f"The job posting uses high-urgency keywords to create synthetic panic (Urgency Score: {urgency_score}/100), rushing candidates into registering or paying before carrying out proper verification.",
                "matched_text": ", ".join(list(set(urgency_matches))[:3]),
                "explanation": f"Urgency score ({urgency_score}) crossed the medium threshold of 50. Matched urgency triggers: {list(set(urgency_matches))}"
            })

        if pressure_score >= 50:
            evidence.append({
                "id": "guaranteed_placement_tactics",
                "title": "Unrealistic Placement Guarantee",
                "category": "unrealistic_offers",
                "severity": "medium",
                "score": -12,
                "description": f"The job post claims 100% placement or guaranteed hiring without evaluating competence (Pressure Score: {pressure_score}/100). Professional recruitments never guarantee hiring prior to assessments.",
                "matched_text": ", ".join(list(set(pressure_matches))[:3]),
                "explanation": f"Pressure score ({pressure_score}) crossed the medium threshold of 50. Matched placement pressure triggers: {list(set(pressure_matches))}"
            })

        return {
            "urgency_score": urgency_score,
            "pressure_score": pressure_score,
            "evidence": evidence
        }
