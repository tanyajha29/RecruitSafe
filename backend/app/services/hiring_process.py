import re
from typing import Dict, Any, List

class HiringProcessValidator:
    """
    Validates the legitimacy of the described hiring workflow.
    - Rewards structured, multi-phase interview funnels.
    - Deducts points for shortcut pressure tactics (e.g. direct joining, no interviews).
    """

    GOOD_PHASES = {
        "application": [r"\bapply\b", r"\bapplication\b", r"\bsubmit\s*resume\b"],
        "assessment": [r"\btest\b", r"\bassessment\b", r"\btask\b", r"\bcoding\s*round\b", r"\bscreening\b"],
        "interview": [r"\binterview\b", r"\btechnical\s*round\b", r"\bdiscussion\b", r"\bpanel\b"],
        "hr_round": [r"\bhr\s*round\b", r"\bmanagerial\s*round\b", r"\bfinal\s*round\b"],
        "offer_letter": [r"\boffer\s*letter\b", r"\bformal\s*contract\b", r"\bemployment\s*agreement\b"]
    }

    BAD_INDICATORS = {
        "direct_joining": {
            "id": "direct_joining_no_interview",
            "title": "Direct Hiring Without Screening",
            "keywords": [r"\bno\s*interview\b", r"\bwithout\s*interview\b", r"\bdirect\s*joining\b", r"\bspot\s*joining\b", r"\bdirect\s*selection\b", r"\bspot\s*selection\b"],
            "score": -20,
            "severity": "high",
            "description": "The job listing guarantees selection or direct joining without a formal evaluation, screening, or interview process. Legitimate corporate entities evaluate candidates before issuing offers."
        },
        "pay_to_hire": {
            "id": "pay_before_interview",
            "title": "Pay-To-Hire Scheme Detected",
            "keywords": [r"\bselection\s*(?:after|upon)\s*payment\b", r"\bpay\s*(?:deposit|fee)\s*first\b", r"\bdeposit\s*required\s*for\s*joining\b"],
            "score": -25,
            "severity": "high",
            "description": "Candidates are instructed to make payment or pay a security deposit before an interview is scheduled or a contract is generated."
        }
    }

    @classmethod
    def validate_process(cls, text: str) -> Dict[str, Any]:
        """
        Audits the job description text for hiring milestones.
        Returns:
            dict containing:
                evidence: list of negative Evidence dicts
                positive_findings: list of positive findings dicts
                hiring_details: metadata
        """
        evidence = []
        positive_findings = []
        detected_good_phases = []

        if not text:
            return {
                "evidence": [],
                "positive_findings": [],
                "hiring_details": {"phases": [], "bad_triggers": []}
            }

        # 1. Audit positive signals (hiring funnel phases)
        for phase_name, regexes in cls.GOOD_PHASES.items():
            for regex in regexes:
                if re.search(regex, text, re.IGNORECASE):
                    detected_good_phases.append(phase_name)
                    break

        # If 3 or more structured steps are found, reward with a trust bonus
        if len(detected_good_phases) >= 3:
            phase_list_str = ", ".join([p.replace("_", " ").title() for p in detected_good_phases])
            positive_findings.append({
                "id": "structured_hiring_funnel",
                "title": "Structured Professional Hiring Funnel",
                "category": "hiring_process",
                "severity": "low",
                "score": 5,
                "description": f"The job description clearly outlines a structured, multi-phase hiring funnel ({phase_list_str}), which is characteristic of professional corporate recruitments.",
                "matched_text": "Multiple hiring stages referenced",
                "explanation": f"Detected {len(detected_good_phases)} legitimate recruitment phases in the job text."
            })

        # 2. Audit negative signals
        triggered_bad = []
        for key, config in cls.BAD_INDICATORS.items():
            for regex in config["keywords"]:
                match = re.search(regex, text, re.IGNORECASE)
                if match:
                    triggered_bad.append(key)
                    evidence.append({
                        "id": config["id"],
                        "title": config["title"],
                        "category": "unrealistic_offers",
                        "severity": config["severity"],
                        "score": config["score"],
                        "description": config["description"],
                        "matched_text": match.group(0),
                        "explanation": f"Matched suspicious hiring shortcut trigger: '{match.group(0)}'."
                    })
                    break

        return {
            "evidence": evidence,
            "positive_findings": positive_findings,
            "hiring_details": {
                "detected_phases": detected_good_phases,
                "bad_triggers": triggered_bad
            }
        }
