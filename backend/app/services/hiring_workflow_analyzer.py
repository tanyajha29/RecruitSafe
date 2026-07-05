import re
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("recruitsafe")

STAGE_KEYWORDS = {
    "Application": [r"\bapply\b", r"\bapplication\s*form\b", r"\bsubmit\s*application\b", r"\bonline\s*application\b"],
    "Resume Screening": [r"\bresume\b", r"\bcv\b", r"\bscreening\b", r"\bshortlist\b", r"\bevaluate\s*cv\b"],
    "Online Assessment": [r"\btest\b", r"\bexam\b", r"\bassessment\b", r"\bcoding\s*test\b", r"\bonline\s*test\b"],
    "Technical Interview": [r"\btechnical\s*interview\b", r"\btechnical\s*round\b", r"\bcoding\s*interview\b", r"\btechnical\s*discussion\b"],
    "HR Interview": [r"\bhr\s*interview\b", r"\bhr\s*round\b", r"\bhr\s*discussion\b", r"\bhuman\s*resources\s*round\b"],
    "Manager Interview": [r"\bmanager\s*round\b", r"\bmanager\s*interview\b", r"\bmanagerial\s*round\b"],
    "Background Verification": [r"\bbackground\s*(?:check|verification)\b", r"\bdocument\s*verification\b", r"\breference\s*check\b"],
    "Medical": [r"\bmedical\s*(?:test|check|exam)\b", r"\bfitness\s*test\b"],
    "Offer Letter": [r"\boffer\s*letter\b", r"\bofficial\s*offer\b", r"\boffer\s*release\b"],
    "Joining": [r"\bjoining\b", r"\bonboard\b", r"\bonboarding\b", r"\binduction\b"],
    "Training": [r"\btraining\b", r"\bprobation\b", r"\bon-the-job\b"]
}

RISKY_KEYWORDS = {
    "Pay Fee": [r"\bpay\s*(?:fee|deposit|amount)\b", r"\bregistration\s*fee\b", r"\brefundable\s*deposit\b", r"\bprocessing\s*fee\b", r"\btraining\s*fee\b", r"\bpay\s+(?:a\s+)?(?:\w+\s+)?(?:fee|deposit|amount)\b"],
    "Immediate Joining": [r"\bimmediate\s*(?:joining|start)\b", r"\bdirect\s*(?:joining|selection)\b", r"\bjoining\s*tomorrow\b"],
    "Pay Fee Later": [r"\bpay\s*later\b", r"\bdeduct\s*from\s*salary\b", r"\bsalary\s*deduction\b"],
    "No Interview": [r"\bno\s*interview\b", r"\bwithout\s*interview\b", r"\bdirect\s*selection\b"]
}

class HiringWorkflowAnalyzer:
    """
    Modular service to verify logical stages of recruitment workflow.
    Differentiates between structured processes, risky steps, and direct onboarding.
    """

    @classmethod
    def detect_stages(cls, text: str) -> List[Tuple[str, int]]:
        """Scans text for hiring stages and returns matched stage name and its character index."""
        matched = []
        if not text:
            return matched

        for stage, patterns in STAGE_KEYWORDS.items():
            first_idx = -1
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    idx = match.start()
                    if first_idx == -1 or idx < first_idx:
                        first_idx = idx
            if first_idx != -1:
                matched.append((stage, first_idx))

        # Sort stages chronologically by their occurrence in description text
        matched.sort(key=lambda x: x[1])
        return matched

    @classmethod
    def detect_risks(cls, text: str) -> List[Tuple[str, int]]:
        """Scans text for risky workflow signs and returns name and character index."""
        matched = []
        if not text:
            return matched

        for risk, patterns in RISKY_KEYWORDS.items():
            first_idx = -1
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    idx = match.start()
                    if first_idx == -1 or idx < first_idx:
                        first_idx = idx
            if first_idx != -1:
                matched.append((risk, first_idx))

        matched.sort(key=lambda x: x[1])
        return matched

    @classmethod
    def analyze_workflow(cls, text: str) -> Dict[str, Any]:
        """
        Analyzes the hiring timeline sequence structure.
        Returns:
            score: 0-100 workflow score
            type: "Good", "Risky", "Very Risky"
            explanation: detailed analysis text
            diagram: ASCII flowchart string
            missing_stages: expected checklist items absent from posting
        """
        stages = cls.detect_stages(text)
        risks = cls.detect_risks(text)

        stage_names = [s[0] for s in stages]
        risk_names = [r[0] for r in risks]

        # Expected Checklist
        expected = ["Application", "Technical Interview", "HR Interview", "Offer Letter", "Joining"]
        missing = [est for est in expected if est not in stage_names]

        # Flow Diagram Construction
        flow_items = []
        for item in sorted(stages + risks, key=lambda x: x[1]):
            flow_items.append(item[0])

        if not flow_items:
            flow_items = ["No explicit hiring workflow defined"]

        diagram = " → ".join(flow_items)

        # Baseline Scoring
        score = 80
        workflow_type = "Good"
        explanation = ""

        # Adjust score based on structural checks
        if len(stage_names) >= 4:
            score += 15  # Structured pipeline
        elif len(stage_names) == 0:
            score -= 15  # Unstructured/missing pipeline

        # Deduct if expected stages are missing
        if "Technical Interview" in missing or "HR Interview" in missing:
            score -= 10
        if "Offer Letter" in missing:
            score -= 5

        # Evaluate risk combinations
        has_pay_fee = "Pay Fee" in risk_names or "Pay Fee Later" in risk_names
        has_no_interview = "No Interview" in risk_names
        has_immediate = "Immediate Joining" in risk_names

        if has_pay_fee and has_no_interview:
            score = 25
            workflow_type = "Very Risky"
            explanation = "This workflow is highly suspicious: it promises direct job placement with no evaluation rounds, but demands monetary payments."
        elif has_pay_fee:
            score = 45
            workflow_type = "Risky"
            explanation = "Risky workflow detected: candidate is prompted to make upfront payments (for kits, training, or deposit) during the application timeline."
        elif has_no_interview and has_immediate:
            score = 35
            workflow_type = "Very Risky"
            explanation = "High-risk indicator: posting offers direct, immediate joining without any formal competency assessments or interview sessions."
        elif has_no_interview:
            score = 55
            workflow_type = "Risky"
            explanation = "Unusual hiring process: direct selection is promised without typical screening or interview checks."
        else:
            if len(stage_names) >= 3:
                score = max(score, 90)
                explanation = "Legitimate recruitment timeline: utilizes a standard pipeline with evaluation checks and multiple interview stages before contract release."
            else:
                explanation = "Standard sparse hiring process. Minimal details are provided regarding the exact timeline sequences."

        score = max(0, min(100, score))

        return {
            "score": score,
            "type": workflow_type,
            "explanation": explanation,
            "diagram": diagram,
            "missing_stages": missing
        }
