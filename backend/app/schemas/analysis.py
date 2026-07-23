from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

class RedFlag(BaseModel):
    title: str
    description: str
    severity: str  # "high", "medium", "low"

class Evidence(BaseModel):
    id: str
    rule_id: str
    title: str
    category: str
    severity: str  # "high", "medium", "low", "none"
    score: int
    matched_text: Optional[str] = None
    reason: Optional[str] = None
    evidence_type: str  # "positive", "negative", "unknown"
    confidence: int
    source: str  # "Rule Engine", "Website Analyzer", "Email Analyzer", "AI", "OCR", "Company Verification"

    # Legacy fields kept for UI rendering backwards compatibility
    factor_name: Optional[str] = None
    description: Optional[str] = None
    points_deducted: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def populate_legacy_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            # Map rule_id
            if "rule_id" not in data:
                data["rule_id"] = "RULE_GENERIC"
            # Map id
            if "id" not in data:
                data["id"] = "generic_evidence"
            # Map title
            if "title" not in data and "factor_name" in data:
                data["title"] = data["factor_name"]
            if "factor_name" not in data and "title" in data:
                data["factor_name"] = data["title"]
            # Map description
            if "description" not in data and "reason" in data:
                data["description"] = data["reason"]
            if "reason" not in data and "description" in data:
                data["reason"] = data["description"]
            # Map score
            if "score" not in data and "points_deducted" in data:
                data["score"] = -abs(data["points_deducted"]) if data["points_deducted"] is not None else 0
            if "points_deducted" not in data and "score" in data:
                data["points_deducted"] = abs(data["score"]) if data["score"] is not None else 0
            # Map evidence_type
            if "evidence_type" not in data:
                score_val = data.get("score", 0)
                data["evidence_type"] = "positive" if score_val > 0 else ("unknown" if score_val == 0 else "negative")
            # Map confidence
            if "confidence" not in data:
                data["confidence"] = 10
            # Map source
            if "source" not in data:
                data["source"] = "Rule Engine"
        return data

class WebsiteData(BaseModel):
    url: str
    domain_age_days: Optional[int] = None
    has_valid_ssl: Optional[bool] = False
    has_redirects: Optional[bool] = False
    page_title: Optional[str] = None
    meta_description: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def flatten_nested_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            if "whois" in data and isinstance(data["whois"], dict):
                data["domain_age_days"] = data["whois"].get("domain_age_days")
            if "ssl" in data and isinstance(data["ssl"], dict):
                data["has_valid_ssl"] = data["ssl"].get("has_valid_ssl", False)
            if "has_valid_ssl" not in data:
                data["has_valid_ssl"] = False
        return data

class EmailData(BaseModel):
    sender_email: str
    domain: str
    is_disposable: Optional[bool] = False
    is_free_email: Optional[bool] = False
    urgency_detected: Optional[bool] = False
    payment_request_detected: Optional[bool] = False
    credential_request_detected: Optional[bool] = False

class AnalysisResponse(BaseModel):
    id: str
    input_type: str
    status: str
    error_message: Optional[str] = None
    trust_score: Optional[int] = None
    scam_probability: Optional[float] = None
    risk_category: Optional[str] = None
    
    # Version 2.0 metrics
    confidence_score: Optional[int] = None
    agreement_score: Optional[int] = None
    contradictions: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    positive_findings: List[Dict] = Field(default_factory=list)

    # Version 2.1 Upgraded metrics
    input_quality_score: Optional[int] = None
    verification_status: Optional[Dict[str, str]] = None
    agreement_explanation: Optional[str] = None
    decision_trace: List[str] = Field(default_factory=list)

    # Version 2.2 Upgraded metrics
    email_detected: Optional[bool] = None
    email_type: Optional[str] = None
    hiring_workflow: Optional[Dict[str, Any]] = None
    
    ai_summary: Optional[str] = None
    red_flags: List[RedFlag] = Field(default_factory=list)
    risk_explanation: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    website_data: Optional[WebsiteData] = None
    structured_evidence: Optional[Dict[str, Any]] = None
    email_data: Optional[EmailData] = None
    hybrid_verdict: Optional[Dict[str, Any]] = None
    pdf_url: Optional[str] = None
    created_at: datetime
    processing_time_ms: Optional[int] = None

    @field_validator("id", mode="before")
    @classmethod
    def serialize_id(cls, v):
        if v is not None:
            return str(v)
        return v

    class Config:
        from_attributes = True

class AnalysisSummary(BaseModel):
    id: str
    input_type: str
    original_content: Optional[str] = None
    trust_score: Optional[int] = None
    risk_category: Optional[str] = None
    created_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def serialize_id(cls, v):
        if v is not None:
            return str(v)
        return v

    class Config:
        from_attributes = True

class HistoryResponse(BaseModel):
    total: int
    page: int
    per_page: int
    analyses: List[AnalysisSummary]

class DashboardStats(BaseModel):
    total_analyses: int
    safe_count: int
    needs_verification_count: int
    suspicious_count: int
    high_risk_count: int
    recent_analyses: List[AnalysisSummary]
    risk_distribution: Dict[str, float]  # Percentage of each category

class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    analysis_id: Optional[str] = None
    is_read: bool
    created_at: datetime

    @field_validator("id", "analysis_id", mode="before")
    @classmethod
    def serialize_id(cls, v):
        if v is not None:
            return str(v)
        return v

    class Config:
        from_attributes = True
