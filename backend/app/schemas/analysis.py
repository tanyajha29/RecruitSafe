from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

class RedFlag(BaseModel):
    title: str
    description: str
    severity: str  # "high", "medium", "low"

class Evidence(BaseModel):
    category: str  # "financial_fraud", "identity_theft", etc.
    factor_name: Optional[str] = None
    description: str
    points_deducted: Optional[int] = None
    severity: str
    # Version 2.0 Extended Fields
    id: Optional[str] = None
    title: Optional[str] = None
    score: Optional[int] = None
    matched_text: Optional[str] = None
    explanation: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def populate_legacy_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            if "factor_name" not in data and "title" in data:
                data["factor_name"] = data["title"]
            if "title" not in data and "factor_name" in data:
                data["title"] = data["factor_name"]
            if "points_deducted" not in data and "score" in data:
                data["points_deducted"] = abs(data["score"]) if data["score"] is not None else 0
            if "score" not in data and "points_deducted" in data:
                data["score"] = -abs(data["points_deducted"]) if data["points_deducted"] is not None else 0
        return data

class WebsiteData(BaseModel):
    url: str
    domain_age_days: Optional[int] = None
    has_valid_ssl: bool
    has_redirects: bool
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
    is_disposable: bool
    is_free_email: bool
    urgency_detected: bool
    payment_request_detected: bool
    credential_request_detected: bool

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
    
    ai_summary: Optional[str] = None
    red_flags: List[RedFlag] = Field(default_factory=list)
    risk_explanation: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    website_data: Optional[WebsiteData] = None
    email_data: Optional[EmailData] = None
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
