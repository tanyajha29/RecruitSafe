import json
from typing import List, Dict, Any

class PromptBuilder:
    """
    Houses standardized templates for RecruitSafe scam detection and summary generation.
    Decoupled from LLM client providers.
    """

    @staticmethod
    def build_summary_prompt(text: str) -> str:
        """
        Creates a prompt asking the model to summarize the job listing.
        """
        return (
            "Summarize the following job offer description in a concise paragraph of 2 to 3 sentences. "
            "Be objective and direct:\n\n"
            f"{text}"
        )

    @staticmethod
    def build_analysis_prompt(text: str, evidence: List[Dict[str, Any]]) -> str:
        """
        Creates a structured analysis prompt listing the raw text and matched rules.
        """
        return f"""
You are the AI Reasoning Engine of the RecruitSafe job scam detection system.
Analyze the following job details and technical evidence.

Job Text:
---
{text}
---

Technical Evidence gathered:
{json.dumps(evidence, indent=2)}

Based on this, perform semantic reasoning and output your findings in a strict JSON format with the following keys. Do NOT omit any keys:
- "ai_summary": A 2-3 sentence overview of what the job is.
- "red_flags": A list of dicts, each with keys "title" (short name of flag), "description" (detailed explanation), and "severity" ("high", "medium", "low"). Extract these flags from both the job text semantic details and the technical evidence.
- "risk_explanation": A cohesive paragraph explaining why this job is safe or risky based on the score and evidence.
- "recommendations": A list of 3-5 actionable safety recommendations for the job seeker.

- "payment_requests": Semantic classification of payment requests. Must be one of: "None", "Low", "Medium", "High".
- "identity_requests": Semantic classification of identity requests. Must be one of: "None", "Low", "Medium", "High".
- "urgency": Semantic classification of urgency pressure. Must be one of: "None", "Low", "Medium", "High".
- "professionalism": Semantic classification of job professionalism. Must be one of: "Poor", "Average", "Good", "Excellent".
- "company_legitimacy": Semantic classification of company legitimacy. Must be one of: "Unknown", "Suspicious", "Likely Legit", "Verified".
- "hiring_process": Semantic classification of hiring workflow. Must be one of: "Suspicious", "Unstructured", "Normal", "Rigorous".
- "communication_style": Semantic classification of communication style. Must be one of: "Informal", "Aggressive", "Professional".
- "overall_risk": Semantic overall risk verdict. Must be one of: "Safe", "Needs Verification", "Suspicious", "High Risk".

Return ONLY the raw JSON string. Do not wrap the JSON in markdown code blocks like ```json ... ```. Do not add any text before or after the JSON.
"""
