import re
import json
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger("recruitsafe")

class RedFlagItem(BaseModel):
    title: str = Field(..., description="Short name of the flag")
    description: str = Field(..., description="Detailed explanation of the flag")
    severity: str = Field(..., description="Must be one of 'high', 'medium', 'low'")

class StructuredAnalysisOutput(BaseModel):
    ai_summary: str
    red_flags: List[RedFlagItem]
    risk_explanation: str
    recommendations: List[str]
    payment_requests: str
    identity_requests: str
    urgency: str
    professionalism: str
    company_legitimacy: str
    hiring_process: str
    communication_style: str
    overall_risk: str

def parse_and_validate_analysis(response_text: str) -> Dict[str, Any]:
    """
    Cleans markdown formatting, parses JSON, and validates it against Pydantic.
    """
    response_text = response_text.strip()
    if not response_text:
        raise ValueError("Empty response text returned from LLM provider.")

    # Clean markdown code block wrapping
    if response_text.startswith("```"):
        response_text = re.sub(r'^```(?:json)?\n', '', response_text)
        response_text = re.sub(r'\n```$', '', response_text)
        response_text = response_text.strip()

    parsed_json = json.loads(response_text)
    
    # Run Pydantic validation
    validated_model = StructuredAnalysisOutput.model_validate(parsed_json)
    
    # Return as dict
    return validated_model.model_dump()

def generate_local_fallback(text: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Local heuristic-based fallback reasoning in case of API failure or missing keys.
    """
    logger.info("Generating local fallback AI analysis.")
    
    # 1. Generate generic summary
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    job_preview = lines[0] if lines else "employment opportunity"
    summary = f"This check details an analysis for a job listing referring to '{job_preview[:60]}'."
    if len(lines) > 1:
        summary += f" The description contains requirements and details matching {len(lines)} content lines."

    # 2. Map evidence to red flags
    red_flags = []
    for item in evidence:
        red_flags.append({
            "title": item.get("title") or item.get("factor_name") or "Flagged Indicator",
            "description": item.get("description", "A potential security anomaly was detected."),
            "severity": item.get("severity", "medium")
        })

    # 3. Create cohesive explanation
    if not evidence:
        explanation = "No rule-based red flags were matched in the job description or email text. The listing does not contain typical payment requests, identity theft triggers, or high pressure tactics. However, manual diligence is always advised."
    else:
        explanation = f"Our automated scan detected {len(evidence)} red flags in the job offer description. "
        severities = [item["severity"] for item in evidence]
        if "high" in severities:
            explanation += "Crucially, high severity items (such as upfront payment requests or identity document checks) indicate a significant probability of recruitment fraud."
        else:
            explanation += "These indicators (such as public recruiter emails or urgency pressure tactics) suggest the listing warrants additional verification before sharing sensitive details."

    # 4. Generate recommendations
    recommendations = [
        "Do not pay any upfront fees for registration, training materials, or laptops.",
        "Verify the recruiter's identity by searching their profile on LinkedIn or contacting the company's official HR department.",
        "Never share government identifiers (Aadhaar, PAN card, Passport scans) or banking details before a formal, verified contract is signed."
    ]
    if any(item.get("category") == "pressure_tactics" for item in evidence):
        recommendations.append("Do not succumb to short response windows; take time to verify the employer details.")

    # Determine overall risk based on evidence
    has_high = any(item.get("severity") == "high" for item in evidence)
    has_medium = any(item.get("severity") == "medium" for item in evidence)
    overall_risk = "Safe"
    if has_high:
        overall_risk = "High Risk"
    elif has_medium:
        overall_risk = "Suspicious"
    elif evidence:
        overall_risk = "Needs Verification"

    return {
        "ai_summary": summary,
        "red_flags": red_flags,
        "risk_explanation": explanation,
        "recommendations": recommendations,
        "payment_requests": "High" if any("fee" in str(item.get("id")).lower() for item in evidence) else "None",
        "identity_requests": "High" if any("identity" in str(item.get("category")).lower() for item in evidence) else "None",
        "urgency": "High" if any("urgency" in str(item.get("id")).lower() for item in evidence) else "None",
        "professionalism": "Poor" if evidence else "Good",
        "company_legitimacy": "Suspicious" if overall_risk in ["High Risk", "Suspicious"] else "Likely Legit",
        "hiring_process": "Suspicious" if any("interview" in str(item.get("id")).lower() for item in evidence) else "Normal",
        "communication_style": "Informal" if any("whatsapp" in str(item.get("id")).lower() or "free_email" in str(item.get("id")).lower() for item in evidence) else "Professional",
        "overall_risk": overall_risk
    }
