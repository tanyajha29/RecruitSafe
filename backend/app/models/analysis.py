from datetime import datetime
from typing import Optional, List, Dict
from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, ASCENDING, DESCENDING

class Analysis(Document):
    user_id: PydanticObjectId
    input_type: str  # "text", "pdf", "image", "email", "url"
    original_content: Optional[str] = None  # Preview text or URL
    processed_text: Optional[str] = None   # Full text after OCR/extraction
    status: str = "processing"              # "processing", "completed", "failed"
    error_message: Optional[str] = None

    # Risk Metrics
    trust_score: Optional[int] = None       # 0 - 100
    scam_probability: Optional[float] = None # 0 - 100%
    risk_category: Optional[str] = None     # "Safe", "Needs Verification", "Suspicious", "High Risk"
    
    # Version 2.0 Extended Metrics
    confidence_score: Optional[int] = None   # 0 - 100
    agreement_score: Optional[int] = None    # 0 - 100
    contradictions: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    positive_findings: List[Dict] = Field(default_factory=list)

    # Version 2.1 Upgraded Metrics
    input_quality_score: Optional[int] = None
    verification_status: Optional[Dict[str, str]] = None
    agreement_explanation: Optional[str] = None
    decision_trace: List[str] = Field(default_factory=list)

    # AI Content
    ai_summary: Optional[str] = None
    red_flags: List[Dict[str, str]] = Field(default_factory=list)  # {title, description, severity}
    risk_explanation: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)

    # Technical Detections & Evidence
    evidence: List[Dict] = Field(default_factory=list)  # {id, rule_id, title, category, severity, score, matched_text, reason, evidence_type, confidence, source}
    website_data: Optional[Dict] = None
    email_data: Optional[Dict] = None
    pdf_file_path: Optional[str] = None

    # Meta
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[int] = None
    gemini_api_called: bool = False
    ocr_performed: bool = False

    class Settings:
        name = "analyses"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("user_id", ASCENDING), ("risk_category", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)])
        ]
