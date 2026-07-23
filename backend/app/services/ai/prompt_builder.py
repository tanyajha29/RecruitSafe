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
- "ai_summary": A professional cybersecurity executive summary of the job listing. The summary MUST be structured to contain: 1. Overall assessment of the posting, 2. Positive findings (e.g., professional layout, clear responsibilities), 3. Negative findings (e.g., payments/red flags if any), 4. Unknown findings (e.g., unverified employer presence), 5. Recommended action, and 6. Confidence explanation. Construct it as a single cohesive paragraph. Crucially, the summary must be evidence-driven: clearly distinguish between verified findings, unknown findings, and confirmed risks. Avoid presenting unverified technical issues (such as WHOIS lookup failures or unresolvable domains) as confirmed facts; explicitly mark them as unknown.
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

    @staticmethod
    def build_fallback_extraction_prompt(text: str, missing_fields: List[str]) -> str:
        fields_str = "\n".join([f'- "{field}"' for field in missing_fields])
        return f"""
You are a precise data extraction agent. Extract the values for the following fields from the given Job Text:
{fields_str}

Rules:
1. Do NOT invent, assume, or infer any information.
2. If the information is not explicitly found in the text, return "Unknown" for that field.
3. Return a clean JSON object with the requested field names as keys. Do not include markdown code blocks.

Job Text:
---
{text}
---
"""
