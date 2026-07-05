# Design Document: RecruitSafe Platform

## DOCUMENT PRIORITY

**Hierarchy of Truth:**

1. **requirements.md** (Highest Priority - Single Source of Truth)
2. **RecruitSafe Project Overview.pdf** (Secondary Reference)
3. **Locked UI Images** (Visual Styling and Layout Only)

**Conflict Resolution:**
- If any conflict exists between documents, `requirements.md` ALWAYS overrides the PDF
- The UI images override ONLY visual styling, layout, spacing, typography, colors, and hierarchy
- The UI images do NOT add or remove functional requirements
- Never invent requirements that are not explicitly stated in requirements.md
- If uncertain about ANY requirement: STOP and ask for clarification

**Critical Rules:**

1. **No Scope Creep**: Do NOT add features, pages, APIs, database tables, or any functionality that is not explicitly described in requirements.md unless explicitly approved

2. **No Silent Assumptions**: If confidence about a requirement interpretation is less than 95%:
   - STOP immediately
   - Explain the ambiguity clearly
   - Wait for explicit approval
   - Do NOT guess or make assumptions

3. **UI Fidelity**: The provided UI images are the visual source of truth
   - Maintain spacing, typography, colors, hierarchy, and interaction patterns as closely as practical
   - If implementation constraints require visual deviations, ask for approval first
   - Responsive design must preserve the design intent across screen sizes

4. **Repository Hygiene**:
   - Maintain clean Git history with meaningful commit messages
   - Do NOT leave commented-out code or unused files
   - Remove dead code before considering a module complete
   - No TODO placeholders in production code

## Overview

### System Purpose

RecruitSafe is an AI-powered web application designed to protect job seekers from fraudulent job postings and recruitment scams. The platform provides comprehensive analysis of job opportunities through multiple input modalities (text, PDF, image, email, URL) and delivers detailed risk assessments backed by rule-based detection, AI reasoning, and multi-factor scoring.

### Design Philosophy

The system follows a modular, pipeline-based architecture where:
- Each input type is normalized into a common text representation
- Multiple independent analysis modules process the text in parallel
- Results are aggregated into a comprehensive risk assessment
- All analysis is preserved for historical reference and improvement

The frontend is designed as a responsive, user-friendly web application that masks the complexity of backend processing while providing transparency into analysis reasoning.

### Key Design Principles

1. **Security First**: JWT authentication, bcrypt password hashing, input validation, rate limiting, and HTTPS support
2. **Modularity**: Independent analysis modules (OCR, Website Intelligence, Email Analysis, Rule-Based Detection, AI Analysis) can be enhanced or replaced without affecting others
3. **Transparency**: Users see detailed evidence for risk scores, not just a final number
4. **Reliability**: Graceful degradation when external services fail (Gemini API, website lookups)
5. **Performance**: Asynchronous processing, efficient MongoDB queries, temporary file cleanup
6. **User Experience**: Smooth animations, responsive design, real-time feedback

### Technology Stack Justification

**Frontend: React + Tailwind CSS + Framer Motion**
- React: Component-based architecture enables reusability (input forms, report cards, history tables)
- Tailwind CSS: Utility-first approach accelerates UI development and ensures consistency
- Framer Motion: Provides smooth, professional animations without heavy dependencies
- Axios: Simplifies HTTP requests with interceptors for JWT token management

**Backend: FastAPI + Python**
- FastAPI: High-performance async framework with automatic OpenAPI documentation
- Python: Rich ecosystem for ML/AI (Gemini SDK), OCR (Tesseract), and data processing
- Pydantic: Built-in request/response validation with clear error messages
- JWT + bcrypt: Industry-standard authentication and password security

**Database: PostgreSQL**
- CRITICAL: Ignore all MongoDB references in other documents - PostgreSQL is the ONLY database
- Relational structure with proper foreign keys ensures data integrity
- JSONB fields for variable analysis data (evidence lists, metadata)
- Strong ACID compliance for user data and analysis results
- Mature ecosystem with excellent Python support (psycopg2, SQLAlchemy)
- Easy migration management with Alembic

**AI: Gemini API**
- **Primary AI Provider**: Gemini API for all AI analysis features
- **Architecture Requirement**: The AI layer MUST be abstracted so another provider can be substituted later without changing business logic
- Do NOT implement alternative providers unless explicitly requested
- Multi-modal capabilities support future vision analysis features
- Strong reasoning for explaining risk factors in natural language
- Generous token limits for processing long job descriptions
- Cost-effective compared to alternatives

**OCR: Tesseract (Local)**
- Open-source, no API costs or external dependencies
- Sufficient accuracy for job posting text extraction
- Runs locally, ensuring data privacy
- Well-established Python integration

## Architecture

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WebUI[React Web Application]
    end
    
    subgraph "API Gateway Layer"
        FastAPI[FastAPI Server]
        Auth[Auth Middleware]
        RateLimit[Rate Limiter]
    end
    
    subgraph "Service Layer"
        AuthService[Authentication Service]
        DocProcessor[Document Processor]
        OCREngine[OCR Engine - Tesseract]
        WebIntel[Website Intelligence]
        EmailAnalyzer[Email Analyzer]
        ScamDetector[Rule-Based Scam Detector]
        AIAnalyzer[AI Analyzer - Gemini]
        RiskScorer[Risk Scoring Engine]
        ReportGen[PDF Report Generator]
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL Database)]
        FileStorage[Temporary File Storage]
    end
    
    subgraph "External Services"
        GeminiAPI[Gemini API]
        DNS[DNS/Domain Lookup]
    end
    
    WebUI -->|HTTPS/JWT| FastAPI
    FastAPI --> Auth
    Auth --> RateLimit
    RateLimit --> AuthService
    RateLimit --> DocProcessor
    
    DocProcessor --> OCREngine
    DocProcessor --> WebIntel
    DocProcessor --> EmailAnalyzer
    DocProcessor --> ScamDetector
    
    ScamDetector --> AIAnalyzer
    AIAnalyzer --> RiskScorer
    RiskScorer --> ReportGen
    
    AuthService --> PostgreSQL
    ReportGen --> PostgreSQL
    DocProcessor --> FileStorage
    OCREngine --> FileStorage
    
    AIAnalyzer --> GeminiAPI
    WebIntel --> DNS
    EmailAnalyzer --> DNS
    
    style WebUI fill:#e1f5ff
    style FastAPI fill:#ffe1e1
    style PostgreSQL fill:#e1ffe1
    style GeminiAPI fill:#fff5e1
```

### Analysis Pipeline Architecture

```mermaid
graph LR
    Input[User Input] --> Validator[Input Validator]
    Validator --> Router{Input Type?}
    
    Router -->|Text| TextNorm[Text Normalizer]
    Router -->|PDF| PDFProc[PDF Processor]
    Router -->|Image| ImgProc[Image Processor]
    Router -->|Email| EmailProc[Email Processor]
    Router -->|URL| URLProc[URL Processor]
    
    PDFProc --> OCR[OCR Engine]
    ImgProc --> OCR
    OCR --> TextNorm
    EmailProc --> TextNorm
    URLProc --> Scraper[Web Scraper]
    Scraper --> TextNorm
    
    TextNorm --> Parallel{Parallel Analysis}
    
    Parallel --> Rules[Rule-Based Detection]
    Parallel --> WebCheck[Website Analysis]
    Parallel --> EmailCheck[Email Analysis]
    
    Rules --> Aggregator[Result Aggregator]
    WebCheck --> Aggregator
    EmailCheck --> Aggregator
    
    Aggregator --> AI[AI Analysis - Gemini]
    AI --> Scorer[Risk Scorer]
    Scorer --> PDFGen[PDF Generator]
    PDFGen --> Storage[Store in DB]
    Storage --> Response[Return to User]
    
    style Input fill:#e1f5ff
    style Response fill:#e1ffe1
    style AI fill:#fff5e1
```

## Components and Interfaces

### Frontend Architecture

#### Component Structure

```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.jsx
│   │   ├── RegisterForm.jsx
│   │   ├── ForgotPasswordForm.jsx
│   │   └── ProtectedRoute.jsx
│   ├── dashboard/
│   │   ├── Dashboard.jsx
│   │   ├── StatsCard.jsx
│   │   ├── RiskDistributionChart.jsx
│   │   └── RecentAnalysisList.jsx
│   ├── analysis/
│   │   ├── NewAnalysisForm.jsx
│   │   ├── InputTypeSelector.jsx
│   │   ├── FileUploader.jsx
│   │   ├── AnalysisResult.jsx
│   │   ├── TrustScoreDisplay.jsx
│   │   ├── RedFlagsList.jsx
│   │   ├── EvidenceBreakdown.jsx
│   │   └── RecommendationsList.jsx
│   ├── history/
│   │   ├── AnalysisHistory.jsx
│   │   ├── SearchFilters.jsx
│   │   ├── HistoryTable.jsx
│   │   └── ReportCard.jsx
│   ├── profile/
│   │   ├── ProfileView.jsx
│   │   ├── ProfileEdit.jsx
│   │   └── PasswordChange.jsx
│   ├── notifications/
│   │   ├── NotificationBell.jsx
│   │   └── NotificationList.jsx
│   └── common/
│       ├── Header.jsx
│       ├── Sidebar.jsx
│       ├── LoadingSpinner.jsx
│       ├── ErrorBoundary.jsx
│       └── Toast.jsx
├── services/
│   ├── api.js (Axios configuration + interceptors)
│   ├── authService.js
│   ├── analysisService.js
│   ├── historyService.js
│   └── profileService.js
├── context/
│   ├── AuthContext.jsx
│   └── NotificationContext.jsx
├── hooks/
│   ├── useAuth.js
│   ├── useNotifications.js
│   └── useAnalysis.js
├── utils/
│   ├── validators.js
│   ├── formatters.js
│   └── constants.js
├── pages/
│   ├── LandingPage.jsx
│   ├── LoginPage.jsx
│   ├── RegisterPage.jsx
│   ├── DashboardPage.jsx
│   ├── NewAnalysisPage.jsx
│   ├── AnalysisResultPage.jsx
│   ├── HistoryPage.jsx
│   ├── ProfilePage.jsx
│   └── NotFoundPage.jsx
└── App.jsx
```

#### Key Component Interfaces

**ProtectedRoute Component**
```javascript
interface ProtectedRouteProps {
  component: React.ComponentType;
  requiredAuth: boolean;
}
```

**NewAnalysisForm Component**
```javascript
interface NewAnalysisFormProps {
  onSubmitSuccess: (analysisId: string) => void;
}

interface AnalysisFormState {
  inputType: 'text' | 'pdf' | 'image' | 'email' | 'url';
  content: string;
  file: File | null;
  isSubmitting: boolean;
  uploadProgress: number;
}
```

**AnalysisResult Component**
```javascript
interface AnalysisResultProps {
  analysisId: string;
  data: AnalysisReport;
}

interface AnalysisReport {
  id: string;
  trustScore: number;
  scamProbability: number;
  riskCategory: 'Safe' | 'Needs Verification' | 'Suspicious' | 'High Risk';
  aiSummary: string;
  redFlags: RedFlag[];
  riskExplanation: string;
  recommendations: string[];
  evidenceBreakdown: Evidence[];
  createdAt: string;
  pdfUrl: string;
}
```

#### State Management Strategy

- **Authentication State**: React Context (AuthContext) for user info and token
- **Notifications**: React Context (NotificationContext) for global notifications
- **Form State**: Local component state with React hooks
- **Server State**: React Query for caching and refetching (optional optimization)
- **No Redux**: Application complexity doesn't warrant Redux overhead

#### Routing Structure

```javascript
/                           → LandingPage (public)
/login                      → LoginPage (public)
/register                   → RegisterPage (public)
/forgot-password            → ForgotPasswordPage (public)
/dashboard                  → DashboardPage (protected)
/analysis/new               → NewAnalysisPage (protected)
/analysis/:id               → AnalysisResultPage (protected)
/history                    → HistoryPage (protected)
/profile                    → ProfilePage (protected)
/notifications              → NotificationsPage (protected)
```

### Backend Architecture

#### Module Structure

```
backend/
├── app/
│   ├── main.py (FastAPI app initialization)
│   ├── config.py (Environment variables)
│   ├── database.py (PostgreSQL connection via SQLAlchemy)
│   ├── middleware/
│   │   ├── auth.py (JWT validation)
│   │   └── rate_limit.py (Rate limiting)
│   ├── models/
│   │   ├── user.py (SQLAlchemy User model)
│   │   ├── analysis.py (SQLAlchemy Analysis model)
│   │   ├── notification.py (SQLAlchemy Notification model)
│   │   └── password_reset.py (SQLAlchemy PasswordResetToken model)
│   ├── schemas/
│   │   ├── user.py (Pydantic User schemas for API)
│   │   ├── analysis.py (Pydantic Analysis schemas for API)
│   │   └── notification.py (Pydantic Notification schemas for API)
│   ├── routers/
│   │   ├── auth.py (Login, register, password reset)
│   │   ├── analysis.py (Submit, retrieve, delete analysis)
│   │   ├── history.py (List, search, filter)
│   │   ├── profile.py (Get, update profile)
│   │   └── notifications.py (Get, mark read)
│   ├── services/
│   │   ├── auth_service.py (JWT, bcrypt, password reset)
│   │   ├── document_processor.py (File validation, routing)
│   │   ├── ocr_engine.py (Tesseract integration)
│   │   ├── text_preprocessor.py (Normalization, cleaning)
│   │   ├── website_intelligence.py (Domain analysis, SSL)
│   │   ├── email_analyzer.py (Email validation, pattern detection)
│   │   ├── scam_detector.py (Rule-based detection)
│   │   ├── ai_analyzer.py (Gemini API integration - ABSTRACTED)
│   │   ├── risk_scorer.py (Score calculation, categorization)
│   │   └── report_generator.py (PDF generation)
│   ├── utils/
│   │   ├── validators.py (Input validation)
│   │   ├── sanitizers.py (XSS prevention)
│   │   ├── file_manager.py (Temp file cleanup)
│   │   └── logger.py (Logging configuration)
│   └── alembic/
│       ├── versions/ (Database migrations)
│       └── env.py (Alembic configuration)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── uploads/ (temporary storage)
└── requirements.txt
```

#### Core Service Interfaces

**DocumentProcessor Service**
```python
class DocumentProcessor:
    def process_text(self, text: str) -> ProcessedDocument
    def process_pdf(self, file_path: str) -> ProcessedDocument
    def process_image(self, file_path: str) -> ProcessedDocument
    def process_email(self, email_content: str) -> ProcessedDocument
    def process_url(self, url: str) -> ProcessedDocument
    def validate_file(self, file: UploadFile) -> ValidationResult
```

**OCREngine Service**
```python
class OCREngine:
    def extract_from_image(self, image_path: str) -> str
    def extract_from_pdf(self, pdf_path: str) -> str
    def preprocess_image(self, image_path: str) -> str
```

**ScamDetector Service**
```python
class ScamDetector:
    def detect_financial_fraud(self, text: str) -> List[DetectedPattern]
    def detect_identity_theft(self, text: str) -> List[DetectedPattern]
    def detect_unrealistic_salary(self, text: str) -> List[DetectedPattern]
    def detect_urgency_tactics(self, text: str) -> List[DetectedPattern]
    def verify_company_info(self, text: str) -> List[DetectedPattern]
    def analyze(self, text: str) -> DetectionResults
```

**AIAnalyzer Service**
```python
class AIAnalyzer:
    def generate_summary(self, text: str) -> str
    def identify_red_flags(self, text: str, detection_results: DetectionResults) -> List[RedFlag]
    def explain_risk(self, text: str, trust_score: int, evidence: List[Evidence]) -> str
    def generate_recommendations(self, risk_category: str, evidence: List[Evidence]) -> List[str]
```

**RiskScorer Service**
```python
class RiskScorer:
    def calculate_trust_score(self, evidence: List[Evidence]) -> int
    def calculate_scam_probability(self, trust_score: int) -> float
    def categorize_risk(self, trust_score: int) -> str
    def build_evidence_breakdown(self, detection_results: DetectionResults, 
                                  website_results: WebsiteResults, 
                                  email_results: EmailResults) -> List[Evidence]
```

## Data Models

### PostgreSQL Tables

#### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

#### Analyses Table

```sql
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    input_type VARCHAR(20) NOT NULL, -- 'text', 'pdf', 'image', 'email', 'url'
    original_content TEXT, -- First 1000 chars or URL
    processed_text TEXT, -- Full normalized text
    
    -- Analysis Results
    trust_score INTEGER NOT NULL CHECK (trust_score >= 0 AND trust_score <= 100),
    scam_probability DECIMAL(5,2) NOT NULL CHECK (scam_probability >= 0 AND scam_probability <= 100),
    risk_category VARCHAR(50) NOT NULL, -- 'Safe', 'Needs Verification', 'Suspicious', 'High Risk'
    
    -- AI Generated Content
    ai_summary TEXT,
    red_flags JSONB, -- Array of {title, description, severity}
    risk_explanation TEXT,
    recommendations JSONB, -- Array of strings
    
    -- Evidence Breakdown
    evidence JSONB, -- Array of {category, factor_name, description, points_deducted, severity}
    
    -- Website Analysis (if applicable)
    website_data JSONB, -- {url, domain_age_days, has_valid_ssl, has_redirects, page_title, meta_description}
    
    -- Email Analysis (if applicable)
    email_data JSONB, -- {sender_email, domain, is_disposable, is_free_email, urgency_detected, payment_request_detected, credential_request_detected}
    
    -- PDF Report
    pdf_file_path VARCHAR(500),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms INTEGER,
    gemini_api_called BOOLEAN DEFAULT FALSE,
    ocr_performed BOOLEAN DEFAULT FALSE
);

-- Indexes
CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_analyses_created_at ON analyses(created_at DESC);
CREATE INDEX idx_analyses_user_risk ON analyses(user_id, risk_category);
CREATE INDEX idx_analyses_user_created ON analyses(user_id, created_at DESC);
```

#### Notifications Table

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'analysis_started', 'analysis_complete', 'upload_error', 'pdf_ready'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    analysis_id UUID REFERENCES analyses(id) ON DELETE SET NULL, -- Optional reference
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_user_created ON notifications(user_id, created_at DESC);
```

#### Password Reset Tokens Table

```sql
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    used BOOLEAN DEFAULT FALSE
);

-- Indexes
CREATE UNIQUE INDEX idx_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_reset_tokens_expires_at ON password_reset_tokens(expires_at);
```

### SQLAlchemy Models

```python
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, DECIMAL, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    input_type = Column(String(20), nullable=False)
    original_content = Column(Text)
    processed_text = Column(Text)
    
    trust_score = Column(Integer, nullable=False)
    scam_probability = Column(DECIMAL(5, 2), nullable=False)
    risk_category = Column(String(50), nullable=False)
    
    ai_summary = Column(Text)
    red_flags = Column(JSONB)
    risk_explanation = Column(Text)
    recommendations = Column(JSONB)
    evidence = Column(JSONB)
    website_data = Column(JSONB)
    email_data = Column(JSONB)
    
    pdf_file_path = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    processing_time_ms = Column(Integer)
    gemini_api_called = Column(Boolean, default=False)
    ocr_performed = Column(Boolean, default=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('trust_score >= 0 AND trust_score <= 100', name='check_trust_score_range'),
        CheckConstraint('scam_probability >= 0 AND scam_probability <= 100', name='check_scam_probability_range'),
    )
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    notifications = relationship("Notification", back_populates="analysis")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="SET NULL"))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    analysis = relationship("Analysis", back_populates="notifications")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    used = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")
```

### Pydantic Models

#### Request Models

```python
# Auth Requests
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

# Analysis Requests
class TextAnalysisRequest(BaseModel):
    text: str = Field(max_length=50000)

class EmailAnalysisRequest(BaseModel):
    email_content: str = Field(max_length=50000)

class URLAnalysisRequest(BaseModel):
    url: HttpUrl

# File uploads handled via FastAPI UploadFile

# Profile Requests
class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
```

#### Response Models

```python
class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: datetime
    last_login: Optional[datetime]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class RedFlag(BaseModel):
    title: str
    description: str
    severity: str

class Evidence(BaseModel):
    category: str
    factor_name: str
    description: str
    points_deducted: int
    severity: str

class WebsiteData(BaseModel):
    url: str
    domain_age_days: Optional[int]
    has_valid_ssl: bool
    has_redirects: bool
    page_title: Optional[str]
    meta_description: Optional[str]

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
    trust_score: int
    scam_probability: float
    risk_category: str
    ai_summary: str
    red_flags: List[RedFlag]
    risk_explanation: str
    recommendations: List[str]
    evidence: List[Evidence]
    website_data: Optional[WebsiteData]
    email_data: Optional[EmailData]
    pdf_url: str
    created_at: datetime
    processing_time_ms: int

class AnalysisSummary(BaseModel):
    id: str
    input_type: str
    preview_text: str
    trust_score: int
    risk_category: str
    created_at: datetime

class HistoryResponse(BaseModel):
    total: int
    page: int
    per_page: int
    analyses: List[AnalysisSummary]

class DashboardStats(BaseModel):
    total_analyses: int
    safe_count: int
    suspicious_count: int
    high_risk_count: int
    needs_verification_count: int
    recent_analyses: List[AnalysisSummary]
    risk_distribution: Dict[str, float]

class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    analysis_id: Optional[str]
    is_read: bool
    created_at: datetime
```


### API Design

#### Authentication Endpoints

**POST /api/auth/register**
- Request: `RegisterRequest`
- Response: `TokenResponse`
- Status Codes: 201 Created, 400 Bad Request (email exists), 422 Validation Error

**POST /api/auth/login**
- Request: `LoginRequest`
- Response: `TokenResponse`
- Status Codes: 200 OK, 401 Unauthorized

**POST /api/auth/password-reset**
- Request: `PasswordResetRequest`
- Response: `{"message": "Reset email sent"}`
- Status Codes: 200 OK, 404 Not Found

**POST /api/auth/password-reset/confirm**
- Request: `PasswordResetConfirm`
- Response: `{"message": "Password updated"}`
- Status Codes: 200 OK, 400 Bad Request (invalid/expired token)

**POST /api/auth/logout**
- Headers: `Authorization: Bearer <token>`
- Response: `{"message": "Logged out"}`
- Status Codes: 200 OK

#### Profile Endpoints

**GET /api/profile**
- Headers: `Authorization: Bearer <token>`
- Response: `UserResponse`
- Status Codes: 200 OK, 401 Unauthorized

**PUT /api/profile**
- Headers: `Authorization: Bearer <token>`
- Request: `ProfileUpdateRequest`
- Response: `UserResponse`
- Status Codes: 200 OK, 400 Bad Request, 401 Unauthorized

**POST /api/profile/change-password**
- Headers: `Authorization: Bearer <token>`
- Request: `PasswordChangeRequest`
- Response: `{"message": "Password changed"}`
- Status Codes: 200 OK, 400 Bad Request, 401 Unauthorized

#### Analysis Endpoints

**POST /api/analysis/text**
- Headers: `Authorization: Bearer <token>`
- Request: `TextAnalysisRequest`
- Response: `AnalysisResponse`
- Status Codes: 201 Created, 400 Bad Request, 401 Unauthorized, 429 Too Many Requests

**POST /api/analysis/email**
- Headers: `Authorization: Bearer <token>`
- Request: `EmailAnalysisRequest`
- Response: `AnalysisResponse`
- Status Codes: 201 Created, 400 Bad Request, 401 Unauthorized, 429 Too Many Requests

**POST /api/analysis/url**
- Headers: `Authorization: Bearer <token>`
- Request: `URLAnalysisRequest`
- Response: `AnalysisResponse`
- Status Codes: 201 Created, 400 Bad Request, 401 Unauthorized, 429 Too Many Requests

**POST /api/analysis/file**
- Headers: `Authorization: Bearer <token>`, `Content-Type: multipart/form-data`
- Form Data: `file: File`, `type: 'pdf' | 'image'`
- Response: `AnalysisResponse`
- Status Codes: 201 Created, 400 Bad Request (invalid file), 413 Payload Too Large, 429 Too Many Requests

**GET /api/analysis/{analysis_id}**
- Headers: `Authorization: Bearer <token>`
- Response: `AnalysisResponse`
- Status Codes: 200 OK, 404 Not Found, 401 Unauthorized, 403 Forbidden

**DELETE /api/analysis/{analysis_id}**
- Headers: `Authorization: Bearer <token>`
- Response: `{"message": "Analysis deleted"}`
- Status Codes: 200 OK, 404 Not Found, 401 Unauthorized, 403 Forbidden

**GET /api/analysis/{analysis_id}/pdf**
- Headers: `Authorization: Bearer <token>`
- Response: Binary PDF file
- Status Codes: 200 OK, 404 Not Found, 401 Unauthorized, 403 Forbidden

#### History Endpoints

**GET /api/history**
- Headers: `Authorization: Bearer <token>`
- Query Params: `page: int = 1`, `per_page: int = 20`, `risk_category: str = None`, `search: str = None`, `start_date: date = None`, `end_date: date = None`
- Response: `HistoryResponse`
- Status Codes: 200 OK, 401 Unauthorized

#### Dashboard Endpoints

**GET /api/dashboard**
- Headers: `Authorization: Bearer <token>`
- Response: `DashboardStats`
- Status Codes: 200 OK, 401 Unauthorized

#### Notification Endpoints

**GET /api/notifications**
- Headers: `Authorization: Bearer <token>`
- Query Params: `unread_only: bool = False`
- Response: `List[NotificationResponse]`
- Status Codes: 200 OK, 401 Unauthorized

**PUT /api/notifications/{notification_id}/read**
- Headers: `Authorization: Bearer <token>`
- Response: `{"message": "Marked as read"}`
- Status Codes: 200 OK, 404 Not Found, 401 Unauthorized

**PUT /api/notifications/read-all**
- Headers: `Authorization: Bearer <token>`
- Response: `{"message": "All notifications marked as read"}`
- Status Codes: 200 OK, 401 Unauthorized

### Integration Design

#### Gemini API Integration

**Configuration**
```python
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"  # Fast, cost-effective
GEMINI_TIMEOUT = 30  # seconds
GEMINI_MAX_RETRIES = 2
```

**Integration Points**

1. **Job Summarization**
   - Prompt: "Summarize this job posting in 200 words or less. Include job title, company, location, and key responsibilities: {text}"
   - Fallback: Extract first 200 words if API fails

2. **Red Flag Identification**
   - Prompt: "Identify specific red flags in this job posting. The rule-based system detected: {detection_summary}. Provide 3-5 specific concerning phrases or patterns with explanations: {text}"
   - Fallback: Use rule-based detections only

3. **Risk Explanation**
   - Prompt: "Explain why this job posting received a trust score of {score}/100 and is categorized as {category}. Reference these detected issues: {evidence}. Write 2-3 paragraphs in clear language: {text}"
   - Fallback: Template-based explanation

4. **Safety Recommendations**
   - Prompt: "Generate 3-5 specific, actionable safety recommendations for someone considering this job posting. Risk level: {category}. Detected issues: {evidence_summary}"
   - Fallback: Template-based recommendations by risk category

**Error Handling**
- API quota exceeded: Log warning, use fallback responses, notify admin
- Timeout: Retry once, then use fallback
- Invalid response: Log error, use fallback
- All Gemini failures are graceful - analysis completes without AI insights

#### Tesseract OCR Integration

**Installation Requirements**
```bash
# System dependency
apt-get install tesseract-ocr
apt-get install libtesseract-dev

# Python wrapper
pip install pytesseract
pip install pdf2image
pip install Pillow
```

**Configuration**
```python
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")
TESSERACT_LANG = "eng"
TESSERACT_CONFIG = "--psm 6"  # Assume uniform text block
```

**Image Processing Pipeline**
1. Validate file type (PNG, JPG, JPEG)
2. Validate file size (< 10MB)
3. Save to temporary storage
4. Preprocess: Convert to grayscale, increase contrast if needed
5. Run Tesseract OCR
6. Clean extracted text (remove artifacts, normalize whitespace)
7. Delete temporary file
8. Return normalized text

**PDF Processing Pipeline**
1. Validate file type (PDF)
2. Validate file size (< 20MB)
3. Save to temporary storage
4. Convert PDF pages to images using pdf2image
5. Run OCR on each page
6. Concatenate text from all pages
7. Clean and normalize text
8. Delete temporary files
9. Return normalized text

**Error Handling**
- OCR extraction failure: Return error to user, suggest re-upload with better image quality
- Unreadable image: Return error indicating no text detected
- File corruption: Return error indicating invalid file

#### Website Intelligence Integration

**Domain Lookup Services**
```python
import whois
import ssl
import socket
from urllib.parse import urlparse
```

**Analysis Pipeline**
1. Parse and validate URL
2. Extract domain name
3. Check domain age via WHOIS lookup (timeout: 10s)
4. Verify SSL certificate (timeout: 5s)
5. Check for suspicious redirects (max 3 redirects, timeout: 10s)
6. Extract page metadata (title, description) via HTTP GET (timeout: 10s)
7. Aggregate results
8. Flag suspicious indicators

**Risk Factors**
- Domain < 6 months old: -15 points
- No valid SSL: -20 points
- Suspicious redirects: -15 points
- WHOIS privacy enabled: -5 points
- Domain lookup failure: -10 points

**Error Handling**
- All lookups have timeouts
- Failures are logged but don't block analysis
- Missing data is marked as "unavailable" rather than failing

#### Email Analysis Integration

**Email Parsing**
```python
import email
from email.parser import Parser
import dns.resolver
```

**Analysis Pipeline**
1. Parse email headers and body
2. Extract sender email address
3. Validate email format
4. Extract domain from email
5. Check if domain is disposable (maintain blocklist)
6. Check if domain is free email service (Gmail, Yahoo, etc.)
7. Verify domain has MX records (DNS lookup, timeout: 5s)
8. Scan content for urgency keywords
9. Scan content for payment requests
10. Scan content for credential requests
11. Aggregate results

**Risk Factors**
- Disposable email domain: -25 points
- Free email for corporate recruitment: -15 points
- No MX records: -20 points
- Urgency keywords detected: -10 points
- Payment request: -30 points
- Credential request: -30 points

**Keyword Lists**
```python
URGENCY_KEYWORDS = [
    "urgent", "immediate", "act now", "limited time", 
    "expires soon", "hurry", "don't miss", "last chance"
]

PAYMENT_KEYWORDS = [
    "registration fee", "training fee", "equipment purchase",
    "advance payment", "processing fee", "deposit required",
    "send money", "wire transfer", "gift card"
]

CREDENTIAL_KEYWORDS = [
    "ssn", "social security", "bank account", "routing number",
    "credit card", "cvv", "driver's license", "passport number"
]
```

### Security Architecture

#### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant AuthService
    participant Database
    
    User->>Frontend: Enter credentials
    Frontend->>API: POST /api/auth/login
    API->>AuthService: Validate credentials
    AuthService->>Database: Fetch user by email
    Database-->>AuthService: User data
    AuthService->>AuthService: Compare bcrypt hashes
    AuthService->>AuthService: Generate JWT token
    AuthService-->>API: Token + User data
    API-->>Frontend: TokenResponse
    Frontend->>Frontend: Store token in memory
    Frontend-->>User: Redirect to dashboard
    
    User->>Frontend: Access protected route
    Frontend->>API: GET /api/dashboard<br/>Authorization: Bearer <token>
    API->>AuthService: Validate JWT
    AuthService->>AuthService: Verify signature & expiry
    AuthService-->>API: User ID from token
    API->>Database: Fetch dashboard data
    Database-->>API: Dashboard data
    API-->>Frontend: DashboardStats
    Frontend-->>User: Display dashboard
```

#### JWT Token Structure

**Payload**
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "exp": 1735689600,
  "iat": 1735603200
}
```

**Configuration**
```python
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Must be strong random string
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
```

**Token Storage**
- Frontend: In-memory only (React state/context)
- Not in localStorage (XSS risk)
- Secure, HttpOnly cookies as alternative for enhanced security

#### Rate Limiting Strategy

**Implementation**: Sliding window counter per user/IP

**Limits**
- Authenticated users: 100 requests/hour per user
- Unauthenticated: 20 requests/hour per IP
- File uploads: 10 uploads/hour per user
- Analysis submissions: 20 analyses/hour per user

**Enforcement**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/analysis/text")
@limiter.limit("20/hour")
async def analyze_text(request: Request, ...):
    pass
```

**Response Headers**
```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 15
X-RateLimit-Reset: 1735689600
Retry-After: 3600
```

#### Input Validation and Sanitization

**Validation Layers**
1. **Pydantic Models**: Type validation, length constraints, format validation
2. **Custom Validators**: Business logic validation (e.g., file type verification)
3. **Sanitization**: Remove/escape dangerous content

**Text Input Sanitization**
```python
import bleach

def sanitize_text(text: str) -> str:
    # Remove HTML tags
    clean = bleach.clean(text, tags=[], strip=True)
    # Remove null bytes
    clean = clean.replace('\x00', '')
    # Normalize whitespace
    clean = ' '.join(clean.split())
    return clean
```

**File Validation**
```python
ALLOWED_EXTENSIONS = {
    'pdf': ['application/pdf'],
    'image': ['image/png', 'image/jpeg', 'image/jpg']
}

MAX_FILE_SIZES = {
    'pdf': 20 * 1024 * 1024,  # 20MB
    'image': 10 * 1024 * 1024  # 10MB
}

def validate_file(file: UploadFile, file_type: str) -> None:
    # Check extension
    ext = file.filename.split('.')[-1].lower()
    if file_type == 'pdf' and ext != 'pdf':
        raise ValidationError("Invalid file extension")
    if file_type == 'image' and ext not in ['png', 'jpg', 'jpeg']:
        raise ValidationError("Invalid image extension")
    
    # Check MIME type
    if file.content_type not in ALLOWED_EXTENSIONS[file_type]:
        raise ValidationError("Invalid MIME type")
    
    # Check file size
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZES[file_type]:
        raise ValidationError(f"File too large (max {MAX_FILE_SIZES[file_type]/1024/1024}MB)")
```

#### HTTPS and Security Headers

**Security Headers** (via FastAPI middleware)
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# HTTPS redirect in production
if ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

**CORS Configuration**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],  # Specific origin only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### File Processing Workflow

```mermaid
graph TB
    Upload[File Upload] --> Validate{Validate<br/>Type & Size}
    Validate -->|Invalid| Reject[Return 400 Error]
    Validate -->|Valid| Save[Save to /uploads/<user_id>/<uuid>]
    
    Save --> TypeCheck{File Type?}
    
    TypeCheck -->|PDF| PDFConvert[Convert to Images<br/>pdf2image]
    TypeCheck -->|Image| ImagePrep[Preprocess Image<br/>Grayscale, Contrast]
    
    PDFConvert --> OCR[Tesseract OCR<br/>Extract Text]
    ImagePrep --> OCR
    
    OCR --> Clean[Clean & Normalize Text]
    Clean --> Analysis[Run Analysis Pipeline]
    
    Analysis --> Cleanup{Analysis<br/>Complete?}
    Cleanup -->|Yes| Delete[Delete Temp Files]
    Cleanup -->|Error| DeleteErr[Delete Temp Files<br/>Log Error]
    
    Delete --> Return[Return Results]
    DeleteErr --> ReturnErr[Return Error]
    
    style Upload fill:#e1f5ff
    style Return fill:#e1ffe1
    style Reject fill:#ffe1e1
    style ReturnErr fill:#ffe1e1
```

**Temporary File Management**

**Storage Structure**
```
uploads/
├── <user_id>/
│   ├── <uuid1>.pdf
│   ├── <uuid2>.png
│   └── <uuid3>.jpg
```

**Cleanup Strategy**
1. **Immediate Cleanup**: Delete files after successful OCR extraction
2. **Error Cleanup**: Delete files even if OCR fails
3. **Scheduled Cleanup**: Cron job runs hourly, deletes files older than 1 hour
4. **Startup Cleanup**: Clear all temp files on server restart

```python
import os
import time
from pathlib import Path

UPLOAD_DIR = "uploads"
MAX_FILE_AGE_SECONDS = 3600  # 1 hour

def cleanup_old_files():
    now = time.time()
    for user_dir in Path(UPLOAD_DIR).iterdir():
        if user_dir.is_dir():
            for file_path in user_dir.iterdir():
                if file_path.is_file():
                    age = now - file_path.stat().st_mtime
                    if age > MAX_FILE_AGE_SECONDS:
                        file_path.unlink()
                        logger.info(f"Deleted old temp file: {file_path}")
```

### Analysis Pipeline Workflow

```mermaid
graph TB
    Start[Analysis Request] --> CreateNotif[Create 'Processing' Notification]
    CreateNotif --> Input{Input Type?}
    
    Input -->|Text| DirectText[Use Text Directly]
    Input -->|PDF| PDFFlow[PDF → OCR → Text]
    Input -->|Image| ImgFlow[Image → OCR → Text]
    Input -->|Email| EmailParse[Parse Email Content]
    Input -->|URL| URLFetch[Fetch Web Page → Extract Text]
    
    DirectText --> Preprocess[Text Preprocessing<br/>Clean & Normalize]
    PDFFlow --> Preprocess
    ImgFlow --> Preprocess
    EmailParse --> Preprocess
    URLFetch --> Preprocess
    
    Preprocess --> ParallelStart{Launch Parallel Analysis}
    
    ParallelStart --> Rules[Rule-Based Detection<br/>Financial, Identity, Salary, Urgency, Company Info]
    ParallelStart --> WebAnalysis{URL Provided?}
    ParallelStart --> EmailAnalysis{Email Provided?}
    
    WebAnalysis -->|Yes| WebIntel[Website Intelligence<br/>Domain Age, SSL, Redirects, Metadata]
    WebAnalysis -->|No| WebSkip[Skip Website Analysis]
    
    EmailAnalysis -->|Yes| EmailCheck[Email Analyzer<br/>Domain Verify, Disposable Check, Content Scan]
    EmailAnalysis -->|No| EmailSkip[Skip Email Analysis]
    
    Rules --> Aggregate[Aggregate Results]
    WebIntel --> Aggregate
    WebSkip --> Aggregate
    EmailCheck --> Aggregate
    EmailSkip --> Aggregate
    
    Aggregate --> BuildEvidence[Build Evidence Breakdown<br/>Categorize & Score Factors]
    BuildEvidence --> CalcScore[Calculate Trust Score<br/>Scam Probability, Risk Category]
    
    CalcScore --> AICall{Gemini API<br/>Available?}
    
    AICall -->|Yes| AISummary[AI: Generate Summary]
    AICall -->|No| Fallback1[Use Template Summary]
    
    AISummary --> AIFlags[AI: Identify Red Flags]
    Fallback1 --> AIFlags
    AIFlags --> AIExplain[AI: Risk Explanation]
    AIExplain --> AIRecommend[AI: Safety Recommendations]
    
    AIRecommend --> GenPDF[Generate PDF Report]
    GenPDF --> SaveDB[Save to Database]
    SaveDB --> CompleteNotif[Create 'Complete' Notification]
    CompleteNotif --> ReturnResult[Return Analysis Response]
    
    style Start fill:#e1f5ff
    style ReturnResult fill:#e1ffe1
    style AICall fill:#fff5e1
```

**Detailed Pipeline Steps**

1. **Input Reception & Validation** (50-100ms)
   - Validate request schema
   - Check file size/type if applicable
   - Create "processing started" notification
   - Generate unique analysis ID

2. **Text Extraction** (100ms - 5s depending on input)
   - Text: Direct use
   - PDF: OCR extraction (2-5s per page)
   - Image: OCR extraction (1-3s)
   - Email: Parse headers + body (< 100ms)
   - URL: HTTP fetch + HTML parsing (500ms - 2s)

3. **Text Preprocessing** (50-200ms)
   - Remove excessive whitespace
   - Normalize line breaks
   - Remove special characters
   - Preserve structure and punctuation

4. **Parallel Analysis** (1-3s total)
   - **Rule-Based Detection** (500ms - 1s)
     - Financial fraud patterns (regex matching)
     - Identity theft patterns (regex matching)
     - Salary analysis (extraction + validation)
     - Urgency tactics (keyword matching)
     - Company info verification (presence checks)
   
   - **Website Intelligence** (1-3s if URL provided)
     - WHOIS lookup (1-2s)
     - SSL verification (500ms)
     - Redirect check (500ms)
     - Metadata extraction (500ms - 1s)
   
   - **Email Analysis** (1-2s if email provided)
     - Domain extraction (< 10ms)
     - Disposable check (blocklist lookup, < 50ms)
     - Free email check (< 10ms)
     - MX record lookup (500ms - 1s)
     - Content pattern matching (100-200ms)

5. **Risk Scoring** (50-100ms)
   - Aggregate all detected factors
   - Calculate point deductions
   - Compute trust score (baseline 100 - deductions)
   - Calculate scam probability (100 - trust score)
   - Assign risk category based on thresholds

6. **AI Analysis** (2-5s total, or 0s if API fails)
   - Generate summary (500ms - 1s)
   - Identify red flags (500ms - 1s)
   - Generate risk explanation (1-2s)
   - Generate recommendations (500ms - 1s)
   - Fallback to templates if any call fails

7. **PDF Generation** (500ms - 2s)
   - Create PDF with ReportLab
   - Include all analysis sections
   - Save to storage
   - Generate download URL

8. **Database Storage** (100-200ms)
   - Save complete analysis document
   - Update user's analysis count
   - Create "analysis complete" notification

9. **Response** (< 10ms)
   - Return AnalysisResponse to frontend
   - Total pipeline time: **5-20 seconds**


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: JWT Token Structure and Validity

*For any* successful user registration or login, the generated JWT token SHALL contain the user's ID and email in the payload, use HS256 algorithm, and have an expiration timestamp exactly 24 hours from creation time.

**Validates: Requirements 1.6, 2.5**

### Property 2: Password Length Validation

*For any* password string with length less than 8 characters, the registration or password change request SHALL be rejected with a validation error.

**Validates: Requirements 1.4**

### Property 3: Email Format Validation

*For any* string submitted as an email address, the system SHALL accept it only if it matches valid email format (contains @ symbol, valid domain structure), and SHALL reject invalid formats with a validation error.

**Validates: Requirements 1.5**

### Property 4: Password Hashing Irreversibility

*For any* password submitted during registration, the value stored in the database SHALL be a bcrypt hash (starting with "$2b$" or "$2a$") and SHALL NOT equal the plaintext password.

**Validates: Requirements 1.3**

### Property 5: Expired Token Rejection

*For any* JWT token with an expiration timestamp in the past, requests using that token SHALL be rejected with a 401 unauthorized error.

**Validates: Requirements 2.4**

### Property 6: Password Reset Token Generation

*For any* password reset request, the generated reset token SHALL be a cryptographically secure random string, and SHALL have an expiration timestamp exactly 1 hour from creation time.

**Validates: Requirements 3.1**

### Property 7: File Size and Type Validation

*For any* uploaded file:
- IF the file type is PDF and size <= 20MB and MIME type is "application/pdf", THEN it SHALL be accepted
- IF the file type is image and size <= 10MB and MIME type is "image/png", "image/jpeg", or "image/jpg", THEN it SHALL be accepted
- OTHERWISE, it SHALL be rejected with an appropriate error message

**Validates: Requirements 6.1, 6.2, 6.3, 6.6, 6.7**

### Property 8: Text Normalization Preservation

*For any* text input after preprocessing:
- Excessive whitespace (multiple spaces, tabs) SHALL be normalized to single spaces
- Line breaks SHALL be normalized to consistent format (\\n)
- Important punctuation (periods, commas, quotes, question marks, exclamation marks) SHALL be preserved
- The semantic meaning of the text SHALL be preserved

**Validates: Requirements 7.3, 8.1, 8.2, 8.3**

### Property 9: Financial Fraud Pattern Detection

*For any* text containing financial fraud keywords ("registration fee", "training fee", "equipment purchase", "advance payment", "processing fee"), the Scam_Detector SHALL detect and flag at least one financial fraud pattern in the evidence breakdown.

**Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5**

### Property 10: Identity Theft Pattern Detection

*For any* text containing identity theft request patterns ("social security number", "SSN", "bank account", "routing number", "credit card", "driver's license"), the Scam_Detector SHALL detect and flag at least one identity theft pattern in the evidence breakdown.

**Validates: Requirements 13.1, 13.2, 13.3, 13.4**

### Property 11: Salary Extraction and Validation

*For any* text containing salary information in common formats ($X/hour, $X/year, $X annually, $Xk), the Scam_Detector SHALL extract the numerical salary value, and IF the salary exceeds typical market rates by more than 50% for entry-level positions, SHALL flag it as unrealistic salary in the evidence breakdown.

**Validates: Requirements 14.1, 14.2, 14.3, 14.4**

### Property 12: Urgency Tactic Detection

*For any* text containing urgency keywords ("urgent", "immediate", "act now", "limited time", "expires soon", "hurry", "don't miss", "last chance"), the Scam_Detector SHALL detect and flag at least one urgency tactic pattern in the evidence breakdown.

**Validates: Requirements 15.1, 15.2, 15.3, 15.4**

### Property 13: Company Information Verification

*For any* text analyzed, IF company name is missing OR company address/location is missing OR contact information is incomplete, THEN the Scam_Detector SHALL flag the corresponding missing information in the evidence breakdown.

**Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5, 16.6**

### Property 14: Email Fraud Pattern Detection

*For any* email content containing urgency keywords, payment requests ("send money", "wire transfer", "gift card"), or credential requests ("password", "login", "account information"), the Email_Analyzer SHALL detect and flag the corresponding pattern in the evidence breakdown.

**Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5**

### Property 15: Trust Score Bounds

*For any* combination of detected risk factors, the calculated Trust_Score SHALL be in the range [0, 100], never negative and never exceeding 100, regardless of the number or severity of factors.

**Validates: Requirements 21.1, 21.6**

### Property 16: Score Deduction Ranges

*For any* detected risk factor in the evidence breakdown:
- IF severity is "high", THEN points_deducted SHALL be in range [20, 30]
- IF severity is "moderate", THEN points_deducted SHALL be in range [10, 15]
- IF severity is "low", THEN points_deducted SHALL be in range [5, 10]

**Validates: Requirements 21.3, 21.4, 21.5**

### Property 17: Scam Probability Calculation

*For any* Trust_Score value T in range [0, 100], the Scam_Probability SHALL equal exactly (100 - T), expressed as a percentage.

**Validates: Requirements 22.1, 22.2**

### Property 18: Risk Category Assignment

*For any* Trust_Score value T:
- IF T >= 80, THEN Risk_Category SHALL be "Safe"
- IF 60 <= T < 80, THEN Risk_Category SHALL be "Needs Verification"
- IF 40 <= T < 60, THEN Risk_Category SHALL be "Suspicious"
- IF T < 40, THEN Risk_Category SHALL be "High Risk"

**Validates: Requirements 23.1, 23.2, 23.3, 23.4**

### Property 19: Evidence Completeness

*For any* analysis with detected risk factors from the Scam_Detector, Website_Intelligence, or Email_Analyzer, ALL detected factors SHALL appear in the evidence breakdown with category, factor_name, description, points_deducted, and severity fields populated.

**Validates: Requirements 24.1, 24.2, 24.3**

### Property 20: Search Filter Matching

*For any* analysis history search request with filters (risk_category, search_term, date_range):
- IF risk_category filter is applied, THEN all returned analyses SHALL have matching Risk_Category
- IF search_term filter is applied, THEN all returned analyses SHALL contain the search term in preview_text (case-insensitive)
- IF date_range filter is applied, THEN all returned analyses SHALL have created_at within the specified range

**Validates: Requirements 28.1, 28.2, 28.3, 28.4**

### Property 21: Input Sanitization

*For any* text input containing HTML tags (<script>, <iframe>, <object>, <embed>) or SQL injection patterns, the sanitization function SHALL remove or escape these elements, and the resulting text SHALL NOT contain executable HTML or SQL code.

**Validates: Requirements 34.1, 34.2, 34.3, 34.4**

## Error Handling

### Error Response Format

All errors shall follow a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "User-friendly error message",
    "details": {
      "field": "specific_field_if_applicable",
      "reason": "technical reason for logging"
    }
  }
}
```

### Error Categories

**Validation Errors (400 Bad Request)**
- Invalid email format
- Password too short
- File size exceeded
- Unsupported file type
- Invalid URL format
- Text length exceeded

**Authentication Errors (401 Unauthorized)**
- Invalid credentials
- Missing JWT token
- Expired JWT token
- Invalid JWT signature

**Authorization Errors (403 Forbidden)**
- Attempting to access another user's analysis
- Attempting to delete another user's report

**Not Found Errors (404)**
- Analysis not found
- User not found
- PDF report not found

**Rate Limit Errors (429 Too Many Requests)**
- Request quota exceeded
- Includes Retry-After header

**Server Errors (500 Internal Server Error)**
- Database connection failure
- OCR processing failure
- PDF generation failure
- Unexpected exceptions

### Error Handling Strategy

**External API Failures**
- **Gemini API**: Use fallback templates, log warning, continue analysis
- **WHOIS Lookup**: Mark as unavailable, log warning, continue with reduced score
- **DNS Lookup**: Mark as unavailable, log warning, continue with reduced score
- **SSL Verification**: Mark as failed, log warning, continue analysis

**OCR Failures**
- **Tesseract Error**: Return error to user, suggest re-upload with better quality
- **No Text Detected**: Return error indicating empty or unreadable image
- **PDF Conversion Error**: Return error indicating corrupted or invalid PDF

**Database Failures**
- **Connection Lost**: Log error, return 500 with retry suggestion
- **Query Timeout**: Log error, return 500
- **Duplicate Key**: Return 400 with appropriate message

**File Processing Failures**
- **Upload Interrupted**: Clean up temp files, return 500
- **Disk Full**: Clean up temp files, log critical, return 500
- **Virus Detected**: Delete file immediately, return 400

### Logging Strategy

**Log Levels**
- **ERROR**: Critical failures, database errors, external API complete failures
- **WARN**: Degraded functionality, external API timeouts, missing optional data
- **INFO**: Successful operations, user actions, analysis completions
- **DEBUG**: Detailed processing steps, intermediate results (development only)

**Log Content**
```python
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "ERROR",
  "user_id": "507f1f77bcf86cd799439011",
  "analysis_id": "507f1f77bcf86cd799439012",
  "error_code": "OCR_EXTRACTION_FAILED",
  "message": "Tesseract failed to extract text from image",
  "stack_trace": "...",
  "context": {
    "file_type": "image/png",
    "file_size": 2048576
  }
}
```

**Sensitive Data Handling**
- NEVER log passwords or JWT tokens
- NEVER log complete file contents
- Hash user email in logs for privacy
- Truncate long text inputs in logs (max 200 chars)


## Testing Strategy

### Testing Approach

RecruitSafe employs a comprehensive dual testing approach that combines property-based testing for universal correctness guarantees with example-based unit tests for specific scenarios and integration tests for external dependencies.

### Property-Based Testing

**Framework: Hypothesis (Python)**

Property-based testing is used for the core business logic modules where behavior should hold universally across wide input ranges:

**Applicable Modules:**
1. **Authentication Module**: JWT token generation, password validation, email validation
2. **Text Preprocessing Module**: Normalization, cleaning, whitespace handling
3. **Pattern Detection Module**: Financial fraud, identity theft, urgency tactics, salary extraction
4. **Risk Scoring Engine**: Score calculation, deduction ranges, category assignment
5. **Validation Module**: Input sanitization, file validation

**Configuration:**
- Minimum 100 iterations per property test (to account for randomization)
- Each property test references its design document property via comment tag
- Tag format: `# Feature: recruitsafe-platform, Property {number}: {property_text}`

**Example Property Test Structure:**

```python
from hypothesis import given, strategies as st
import pytest

# Feature: recruitsafe-platform, Property 4: Password Hashing Irreversibility
@given(password=st.text(min_size=8, max_size=72))
def test_password_hashing_irreversibility(password):
    """For any password, stored hash should not equal plaintext."""
    hashed = hash_password(password)
    assert hashed != password
    assert hashed.startswith(("$2b$", "$2a$"))  # bcrypt format

# Feature: recruitsafe-platform, Property 15: Trust Score Bounds
@given(evidence=st.lists(st.builds(Evidence)))
def test_trust_score_bounds(evidence):
    """For any evidence combination, trust score should be in [0, 100]."""
    score = calculate_trust_score(evidence)
    assert 0 <= score <= 100

# Feature: recruitsafe-platform, Property 8: Text Normalization Preservation
@given(text=st.text(min_size=1, max_size=1000))
def test_text_normalization_preservation(text):
    """For any text, normalization should preserve punctuation and meaning."""
    normalized = preprocess_text(text)
    # Check punctuation preserved
    for punct in ['.', ',', '?', '!', '"', "'"]:
        if punct in text:
            assert punct in normalized
    # Check excessive whitespace removed
    assert '  ' not in normalized
    assert '\t' not in normalized
```

### Unit Testing

**Framework: pytest (Python) + React Testing Library (Frontend)**

Unit tests focus on:
- Specific scenarios and edge cases
- Error conditions and boundary cases
- Component behavior with concrete examples
- Functions not amenable to property testing

**Backend Unit Tests:**

```python
def test_registration_with_existing_email():
    """Should reject registration when email already exists."""
    # Arrange
    register_user("test@example.com", "password123")
    # Act & Assert
    with pytest.raises(ValidationError, match="email already registered"):
        register_user("test@example.com", "different_password")

def test_login_with_invalid_credentials():
    """Should reject login with wrong password."""
    register_user("test@example.com", "correct_password")
    with pytest.raises(AuthenticationError):
        login("test@example.com", "wrong_password")

def test_empty_evidence_yields_perfect_score():
    """Trust score should be 100 with no evidence."""
    score = calculate_trust_score([])
    assert score == 100

def test_financial_fraud_detection_with_no_keywords():
    """Should return empty list when no fraud keywords present."""
    text = "Software Engineer position at Tech Corp."
    patterns = detect_financial_fraud(text)
    assert len(patterns) == 0
```

**Frontend Unit Tests:**

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import NewAnalysisForm from './NewAnalysisForm';

test('should show error when text exceeds 50000 characters', () => {
  render(<NewAnalysisForm />);
  const textarea = screen.getByRole('textbox');
  const longText = 'a'.repeat(50001);
  
  fireEvent.change(textarea, { target: { value: longText } });
  fireEvent.submit(screen.getByRole('form'));
  
  expect(screen.getByText(/exceeds maximum length/i)).toBeInTheDocument();
});

test('should display trust score with correct color', () => {
  const mockData = { trustScore: 35, riskCategory: 'High Risk' };
  render(<TrustScoreDisplay data={mockData} />);
  
  const scoreElement = screen.getByText('35');
  expect(scoreElement).toHaveClass('text-red-600');
});
```

### Integration Testing

**Framework: pytest + pytest-asyncio + httpx (Backend) + Cypress (Frontend)**

Integration tests verify:
- External service integrations (Gemini API, Tesseract, DNS, WHOIS)
- Database operations
- End-to-end API workflows
- File upload and processing
- Authentication flows

**Backend Integration Tests:**

```python
@pytest.mark.asyncio
async def test_ocr_extraction_from_pdf(test_pdf_file):
    """Should extract text from PDF using Tesseract."""
    text = await extract_text_from_pdf(test_pdf_file)
    assert len(text) > 0
    assert isinstance(text, str)

@pytest.mark.asyncio
async def test_gemini_summarization_with_mock():
    """Should generate summary via Gemini API."""
    mock_gemini.set_response("Software Engineer at Tech Corp...")
    summary = await generate_summary(sample_job_text)
    assert len(summary) <= 200
    assert "Software Engineer" in summary

@pytest.mark.asyncio
async def test_complete_analysis_pipeline(test_client, test_user):
    """Should complete full analysis from input to PDF."""
    # Login
    login_response = await test_client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Submit analysis
    analysis_response = await test_client.post(
        "/api/analysis/text",
        json={"text": sample_scam_job_posting},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert analysis_response.status_code == 201
    data = analysis_response.json()
    
    # Verify analysis results
    assert 0 <= data["trust_score"] <= 100
    assert data["risk_category"] in ["Safe", "Needs Verification", "Suspicious", "High Risk"]
    assert len(data["recommendations"]) >= 3
    
    # Verify PDF exists
    pdf_response = await test_client.get(
        f"/api/analysis/{data['id']}/pdf",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
```

**Frontend Integration Tests (Cypress):**

```javascript
describe('Analysis Submission Flow', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'password123');
  });

  it('should complete analysis and display results', () => {
    cy.visit('/analysis/new');
    
    // Select text input
    cy.get('[data-testid="input-type-text"]').click();
    
    // Paste job description
    cy.get('[data-testid="job-text-input"]').type(scamJobPosting);
    
    // Submit
    cy.get('[data-testid="submit-button"]').click();
    
    // Wait for analysis
    cy.get('[data-testid="loading-spinner"]', { timeout: 20000 }).should('not.exist');
    
    // Verify results displayed
    cy.url().should('include', '/analysis/');
    cy.get('[data-testid="trust-score"]').should('be.visible');
    cy.get('[data-testid="risk-category"]').should('contain', 'High Risk');
    cy.get('[data-testid="red-flags-list"]').children().should('have.length.at.least', 1);
    
    // Verify PDF download
    cy.get('[data-testid="download-pdf-button"]').click();
    cy.readFile('cypress/downloads/report.pdf').should('exist');
  });
});
```

### Test Data Strategy

**Fixtures and Factories:**

```python
@pytest.fixture
def sample_safe_job_posting():
    return """
    Senior Software Engineer at Google
    Location: Mountain View, CA
    Salary: $150,000 - $200,000
    
    We're seeking an experienced software engineer...
    Requirements: 5+ years experience, BS in CS...
    Contact: careers@google.com
    """

@pytest.fixture
def sample_scam_job_posting():
    return """
    URGENT! Work from home opportunity!
    Earn $5000/week with no experience!
    
    Just pay $299 registration fee to get started.
    Send your SSN and bank account for direct deposit.
    
    Act now! Limited spots available!
    Contact: quickcash@freemail.com
    """

@pytest.fixture
def evidence_factory():
    def make_evidence(severity="high", category="financial_fraud", points=25):
        return Evidence(
            category=category,
            factor_name=f"{category}_detected",
            description=f"Detected {category} pattern",
            points_deducted=points,
            severity=severity
        )
    return make_evidence
```

### Test Coverage Goals

**Backend:**
- Line coverage: > 85%
- Branch coverage: > 80%
- Critical paths (auth, analysis pipeline, risk scoring): > 95%

**Frontend:**
- Component coverage: > 80%
- Critical user flows (login, analysis submission, results viewing): > 90%

### Continuous Integration

**GitHub Actions Workflow:**

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Tesseract
        run: sudo apt-get install -y tesseract-ocr
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run property tests
        run: pytest tests/ -m property --hypothesis-profile ci
      - name: Run unit tests
        run: pytest tests/ -m unit --cov=app --cov-report=xml
      - name: Run integration tests
        run: pytest tests/ -m integration
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run unit tests
        run: npm test -- --coverage
      - name: Run Cypress tests
        run: npm run cypress:run
```

### Test Execution Strategy

**Development:**
- Run unit tests on file save (watch mode)
- Run property tests before commit (git hook)
- Run integration tests before push

**CI/CD:**
- Run all tests on pull request
- Run property tests with 100 iterations minimum
- Fail build on coverage drop > 2%

**Property-Based Test Warnings:**
When running property tests that interact with external services or perform expensive operations, warnings should be displayed to manage expectations:
- "Running property tests with 100 iterations. This may take several minutes."
- Tests should use mocks for external services to keep execution time reasonable
- Long-running tests should be marked and run separately in CI

### Test Organization

```
backend/tests/
├── unit/
│   ├── test_auth_service.py
│   ├── test_text_preprocessor.py
│   ├── test_scam_detector.py
│   ├── test_risk_scorer.py
│   └── test_validators.py
├── integration/
│   ├── test_ocr_engine.py
│   ├── test_ai_analyzer.py
│   ├── test_analysis_pipeline.py
│   └── test_api_endpoints.py
├── property/
│   ├── test_jwt_properties.py
│   ├── test_validation_properties.py
│   ├── test_normalization_properties.py
│   ├── test_detection_properties.py
│   └── test_scoring_properties.py
├── fixtures/
│   ├── sample_job_postings.py
│   ├── sample_emails.py
│   └── test_files/
│       ├── sample.pdf
│       └── sample.png
└── conftest.py

frontend/src/__tests__/
├── components/
│   ├── NewAnalysisForm.test.jsx
│   ├── AnalysisResult.test.jsx
│   └── TrustScoreDisplay.test.jsx
├── services/
│   ├── authService.test.js
│   └── analysisService.test.js
├── integration/
│   └── cypress/
│       ├── e2e/
│       │   ├── authentication.cy.js
│       │   ├── analysis_flow.cy.js
│       │   └── history.cy.js
│       └── fixtures/
│           └── sample_job_postings.json
```

## Deployment Considerations

### Environment Variables

**Required Configuration:**

```bash
# Database (PostgreSQL ONLY)
DATABASE_URL=postgresql://user:password@localhost:5432/recruitsafe
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Authentication
JWT_SECRET_KEY=<strong-random-256-bit-key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# External APIs
GEMINI_API_KEY=<gemini-api-key>
GEMINI_MODEL=gemini-1.5-flash

# OCR
TESSERACT_CMD=/usr/bin/tesseract
TESSERACT_LANG=eng

# Email (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<email-address>
SMTP_PASSWORD=<app-password>
SMTP_FROM_EMAIL=noreply@recruitsafe.com

# CORS
FRONTEND_URL=http://localhost:3000

# File Upload
MAX_PDF_SIZE_MB=20
MAX_IMAGE_SIZE_MB=10
UPLOAD_DIR=uploads

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_HOUR=100

# Environment
ENVIRONMENT=production  # or development
LOG_LEVEL=INFO
```

### Infrastructure Requirements

**Backend Server:**
- Python 3.11+
- 2GB RAM minimum (4GB recommended for Tesseract)
- 20GB disk space (for temporary file storage)
- Tesseract OCR system package installed
- Linux/Ubuntu recommended for Tesseract compatibility

**Database:**
- PostgreSQL 13+ (CRITICAL: PostgreSQL is the ONLY database - ignore all MongoDB references)
- Connection pooling configured (20-30 connections)
- Regular backups enabled (daily with 30-day retention)
- Replication for production (primary + read replica)

**Frontend:**
- Node.js 18+ for build
- Static hosting (Vercel, Netlify, S3 + CloudFront)
- HTTPS required

### Performance Considerations

**Expected Load:**
- Concurrent users: 100-1000
- Analyses per hour: 500-5000
- Average analysis time: 5-20 seconds
- Database queries per analysis: 3-5

**Optimization Strategies:**
- PostgreSQL connection pooling (20-30 connections via SQLAlchemy)
- Async processing for analysis pipeline
- Rate limiting to prevent overload
- Temporary file cleanup to prevent disk issues
- CDN for frontend static assets
- Database query optimization with proper indexes
- JSONB indexing for frequently queried fields
- Gemini API request caching for similar queries (optional)

### Monitoring and Alerting

**Metrics to Track:**
- API response times (p50, p95, p99)
- Analysis pipeline success rate
- Gemini API failure rate
- OCR failure rate
- Database query performance
- Disk space usage (temp files)
- Error rates by endpoint

**Alerts:**
- Error rate > 5% for 5 minutes
- Analysis pipeline failure > 20% for 10 minutes
- Gemini API quota approaching limit
- Disk space > 80% full
- Database connection pool exhausted

### Security Hardening

**Production Checklist:**
- [ ] HTTPS enabled with valid certificate
- [ ] Strong JWT secret (256-bit random)
- [ ] Rate limiting enabled
- [ ] CORS restricted to frontend domain only
- [ ] Security headers configured
- [ ] PostgreSQL authentication enabled with strong password
- [ ] PostgreSQL network access restricted (firewall rules)
- [ ] Database connections use SSL/TLS
- [ ] Environment variables not in code
- [ ] Secrets rotation policy established
- [ ] Regular dependency updates
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries via SQLAlchemy)
- [ ] File upload virus scanning (optional but recommended)

### Backup and Recovery

**Backup Strategy:**
- PostgreSQL: Daily automated backups via pg_dump, 30-day retention
- Point-in-time recovery (PITR) with WAL archiving
- User data: Encrypted backups stored securely
- Analysis reports: Backed up with database
- Temp files: No backup needed (ephemeral)

**Recovery Procedures:**
- Database restore from backup: < 1 hour RTO
- Application deployment rollback: < 15 minutes
- Disaster recovery plan documented

## Future Enhancements

**Potential Features:**
1. **Multi-language Support**: Expand OCR and analysis to support Spanish, French, etc.
2. **Batch Analysis**: Upload multiple job postings at once
3. **Browser Extension**: Analyze jobs directly from job boards
4. **Company Reputation Database**: Track known scam companies
5. **Social Sharing**: Share analysis results (anonymized)
6. **API Access**: Provide API for third-party integrations
7. **Mobile Apps**: Native iOS and Android applications
8. **Collaborative Features**: Share reports with friends/family
9. **Advanced AI Models**: Fine-tuned models for job scam detection
10. **Real-time Alerts**: Notify users of new scam patterns

**Technical Debt Considerations:**
- Migrate to cloud storage for PDF reports (S3) as scale increases
- Implement caching layer (Redis) for frequently accessed analyses
- Consider microservices architecture if complexity grows
- Implement message queue (RabbitMQ/Celery) for async processing at scale

## Implementation Phases

The implementation MUST follow these phases sequentially. Each phase must be completed, tested, and verified before proceeding to the next phase.

### Phase 1: Project Setup & Infrastructure
**Duration**: 1-2 days

**Deliverables:**
- Project folder structure (frontend + backend)
- Git repository initialized
- Environment configuration (.env.example, .env templates)
- PostgreSQL database setup with Alembic migrations
- FastAPI basic app initialization
- React app with Tailwind CSS and Framer Motion configured
- README.md with setup instructions
- requirements.txt and package.json with all dependencies

**Definition of Done:**
- [ ] Backend starts without errors (`uvicorn app.main:app`)
- [ ] Frontend starts without errors (`npm start`)
- [ ] PostgreSQL connection successful
- [ ] Alembic migrations run successfully
- [ ] No TypeScript/Python errors
- [ ] Environment variables documented
- [ ] Git repository has initial commit

### Phase 2: Authentication Module
**Duration**: 2-3 days

**Deliverables:**
- User registration endpoint with email validation and password hashing (bcrypt)
- Login endpoint with JWT token generation
- Password reset flow (request + confirm endpoints)
- JWT middleware for protected routes
- Frontend: Login, Register, Forgot Password pages
- Auth context and useAuth hook
- Protected route component
- Token storage and automatic refresh

**Definition of Done:**
- [ ] Users can register with email/password
- [ ] Passwords are hashed with bcrypt (verified in database)
- [ ] Users can log in and receive JWT token
- [ ] JWT tokens expire after 24 hours
- [ ] Protected routes redirect to login when unauthenticated
- [ ] Password reset emails are sent (or mocked for dev)
- [ ] No console errors
- [ ] Forms have validation and error messages
- [ ] Loading states implemented
- [ ] Success notifications displayed
- [ ] All endpoints tested (manual or automated)
- [ ] No SQL injection vulnerabilities
- [ ] No hardcoded secrets

### Phase 3: Dashboard & Profile
**Duration**: 2-3 days

**Deliverables:**
- Dashboard backend: stats aggregation endpoint
- Profile backend: get/update profile, change password endpoints
- Frontend: Dashboard page with statistics and visualizations
- Frontend: Profile page with view/edit modes
- StatsCard component
- RiskDistributionChart component (basic chart library)
- RecentAnalysisList component

**Definition of Done:**
- [ ] Dashboard displays user statistics (total analyses, risk distribution)
- [ ] Dashboard shows recent analyses list
- [ ] Profile displays user information
- [ ] Users can update full name and email
- [ ] Users can change password (requires current password)
- [ ] Responsive design matches UI mockups
- [ ] Smooth animations with Framer Motion (subtle, not flashy)
- [ ] Loading states for all data fetching
- [ ] Error handling for failed requests
- [ ] Success notifications for updates
- [ ] No console errors
- [ ] No TypeScript errors

### Phase 4: File Upload & OCR Module
**Duration**: 3-4 days

**Deliverables:**
- File upload validation (size, type, MIME checks)
- Temporary file storage with unique paths per user
- Tesseract OCR integration for images
- PDF to image conversion + OCR for PDFs
- Text preprocessing and normalization service
- File cleanup service (immediate + scheduled)
- Frontend: FileUploader component with drag-and-drop
- Upload progress indicator

**Definition of Done:**
- [ ] PDF files (≤20MB) upload successfully
- [ ] Image files (≤10MB) upload successfully
- [ ] Invalid files rejected with clear error messages
- [ ] OCR extracts text from images
- [ ] OCR extracts text from PDFs (all pages)
- [ ] Extracted text is cleaned and normalized
- [ ] Temporary files are deleted after processing
- [ ] Upload progress shown to user
- [ ] Error handling for OCR failures
- [ ] No disk space leaks
- [ ] File validation prevents malicious uploads
- [ ] No console errors

### Phase 5: Analysis Pipeline - Rule Engine
**Duration**: 3-4 days

**Deliverables:**
- Financial fraud detection service (keyword patterns)
- Identity theft detection service (keyword patterns)
- Salary extraction and validation service
- Urgency tactic detection service
- Company information verification service
- ScamDetector service that coordinates all detections
- Evidence builder service
- Unit tests for each detection module

**Definition of Done:**
- [ ] Financial fraud patterns detected correctly
- [ ] Identity theft patterns detected correctly
- [ ] Unrealistic salaries flagged correctly
- [ ] Urgency tactics detected correctly
- [ ] Missing company info flagged correctly
- [ ] Evidence breakdown includes all detected factors
- [ ] Each factor has category, description, severity, points
- [ ] No false negatives on test cases
- [ ] Property-based tests pass (100+ iterations)
- [ ] Unit tests cover edge cases
- [ ] No Python errors

### Phase 6: Analysis Pipeline - AI & Scoring
**Duration**: 3-4 days

**Deliverables:**
- Gemini API integration service (ABSTRACTED for provider flexibility)
- AI summarization function with fallback
- AI red flag identification with fallback
- AI risk explanation with fallback
- AI recommendations generation with fallback
- Risk scoring engine (trust score calculation)
- Scam probability calculator
- Risk category assignment logic
- Comprehensive error handling for API failures

**Definition of Done:**
- [ ] Gemini API calls succeed with valid API key
- [ ] Summaries generated (≤200 words)
- [ ] Red flags identified (3-5 specific items)
- [ ] Risk explanations are clear and reference evidence
- [ ] Recommendations are actionable (3-5 items)
- [ ] Fallback templates used when API fails
- [ ] Trust score in range [0, 100]
- [ ] Scam probability = 100 - trust score
- [ ] Risk categories assigned correctly (Safe/Needs Verification/Suspicious/High Risk)
- [ ] AI service abstracted (provider can be swapped)
- [ ] API timeout and retry logic implemented
- [ ] All correctness properties validated
- [ ] No crashes on API failures

### Phase 7: Website & Email Intelligence
**Duration**: 2-3 days

**Deliverables:**
- Website intelligence service (WHOIS, SSL, redirects, metadata)
- Email analyzer service (domain validation, pattern detection)
- Disposable email blocklist
- Free email provider list
- DNS MX record verification
- Integration with analysis pipeline

**Definition of Done:**
- [ ] Domain age extracted via WHOIS
- [ ] SSL certificate validation works
- [ ] Suspicious redirects detected
- [ ] Page metadata extracted
- [ ] Email domain validation works
- [ ] Disposable emails flagged
- [ ] Free email services identified
- [ ] Urgency/payment/credential patterns detected in emails
- [ ] All operations have timeouts
- [ ] Failures don't block analysis
- [ ] Missing data marked as "unavailable"
- [ ] Evidence breakdown includes website/email factors

### Phase 8: PDF Report Generation
**Duration**: 2-3 days

**Deliverables:**
- PDF generation service using ReportLab
- Report template with branding
- Report includes: trust score, risk category, summary, red flags, evidence, recommendations
- PDF storage in file system (or S3 if configured)
- PDF download endpoint
- PDF viewer component in frontend

**Definition of Done:**
- [ ] PDFs generated successfully for all analyses
- [ ] PDFs include all analysis sections
- [ ] PDFs are well-formatted and readable
- [ ] PDF download works from frontend
- [ ] PDF file paths stored in database
- [ ] PDF storage cleaned up on analysis deletion
- [ ] Error handling for generation failures
- [ ] No memory leaks

### Phase 9: New Analysis Flow Integration
**Duration**: 3-4 days

**Deliverables:**
- Complete analysis pipeline orchestration
- Analysis endpoints (text, email, URL, file)
- Analysis retrieval and deletion endpoints
- Frontend: New Analysis page with input type selector
- Frontend: Analysis Result page with all sections
- TrustScoreDisplay component
- RedFlagsList component
- EvidenceBreakdown component
- RecommendationsList component
- Notification creation for analysis start/complete

**Definition of Done:**
- [ ] Text analysis works end-to-end
- [ ] Email analysis works end-to-end
- [ ] URL analysis works end-to-end
- [ ] PDF upload analysis works end-to-end
- [ ] Image upload analysis works end-to-end
- [ ] Results page displays all sections correctly
- [ ] Trust score displayed with correct color coding
- [ ] Red flags listed with severity badges
- [ ] Evidence breakdown shown with categories
- [ ] Recommendations displayed clearly
- [ ] PDF download button works
- [ ] Analysis processing time ≤ 20 seconds
- [ ] Error handling for all failure modes
- [ ] Loading states during processing
- [ ] Success notifications
- [ ] Responsive design matches UI mockups
- [ ] Smooth animations (Framer Motion)
- [ ] No console errors
- [ ] No failing API calls

### Phase 10: History & Search
**Duration**: 2-3 days

**Deliverables:**
- History listing endpoint with pagination
- Search and filter implementation (risk category, text search, date range)
- Analysis deletion endpoint
- Frontend: History page with search/filter UI
- HistoryTable component
- SearchFilters component
- ReportCard component
- Delete confirmation modal

**Definition of Done:**
- [ ] History page lists all user analyses
- [ ] Pagination works correctly
- [ ] Search by text filters results
- [ ] Filter by risk category works
- [ ] Filter by date range works
- [ ] Users can delete their analyses
- [ ] Delete confirmation prevents accidents
- [ ] Deleted analyses removed from database and file system
- [ ] Empty state shown when no results
- [ ] Loading states implemented
- [ ] Responsive design
- [ ] No console errors

### Phase 11: Notifications System
**Duration**: 2-3 days

**Deliverables:**
- Notification creation service
- Notification listing endpoint
- Mark notification as read endpoint
- Mark all notifications as read endpoint
- Frontend: NotificationBell component with badge
- Frontend: NotificationList component
- Real-time notification updates (polling or WebSocket)

**Definition of Done:**
- [ ] Notifications created on analysis start/complete/error
- [ ] Notification bell shows unread count
- [ ] Clicking bell opens notification list
- [ ] Users can mark individual notifications as read
- [ ] Users can mark all notifications as read
- [ ] Notifications link to relevant analyses
- [ ] Notification list updates without page refresh
- [ ] Responsive design
- [ ] No console errors

### Phase 12: Rate Limiting & Security
**Duration**: 2-3 days

**Deliverables:**
- Rate limiting middleware (per user, per IP)
- Input sanitization for all text inputs
- File upload security checks
- Security headers middleware
- CORS configuration
- SQL injection prevention audit
- XSS prevention audit
- HTTPS redirect in production

**Definition of Done:**
- [ ] Rate limiting enforced (100 req/hr authenticated, 20 req/hr unauthenticated)
- [ ] Rate limit headers included in responses
- [ ] 429 errors returned when limits exceeded
- [ ] All text inputs sanitized (HTML tags removed)
- [ ] File uploads validate MIME types
- [ ] SQL injection not possible (parameterized queries verified)
- [ ] XSS attacks prevented (sanitization verified)
- [ ] Security headers configured (HSTS, CSP, X-Frame-Options, etc.)
- [ ] CORS restricted to frontend domain only
- [ ] HTTPS enforced in production
- [ ] No hardcoded secrets in code

### Phase 13: Testing & Quality Assurance
**Duration**: 3-5 days

**Deliverables:**
- Property-based tests for core business logic (21 properties)
- Unit tests for all services
- Integration tests for API endpoints
- Frontend component tests
- End-to-end tests for critical flows (Cypress)
- Test coverage report
- Bug fixes from testing

**Definition of Done:**
- [ ] All 21 property-based tests pass (100+ iterations each)
- [ ] Unit test coverage ≥ 85%
- [ ] Critical path coverage ≥ 95% (auth, analysis, scoring)
- [ ] All integration tests pass
- [ ] All frontend component tests pass
- [ ] E2E tests pass for: registration, login, analysis submission, results viewing, history
- [ ] No failing tests
- [ ] No known critical bugs
- [ ] Performance acceptable (analysis ≤ 20s, API responses ≤ 2s)

### Phase 14: Documentation & Deployment
**Duration**: 2-3 days

**Deliverables:**
- Comprehensive README.md with setup instructions
- API documentation (FastAPI auto-generated + enhancements)
- Environment variable documentation
- Database migration guide
- Deployment guide (Docker, VPS, cloud platforms)
- User guide (optional)
- License file

**Definition of Done:**
- [ ] README includes: project description, features, tech stack, prerequisites, installation, configuration, running locally, testing, deployment
- [ ] API documentation accessible and accurate
- [ ] All environment variables documented with examples
- [ ] Database setup instructions clear
- [ ] Deployment tested on at least one platform
- [ ] Docker configuration works (optional but recommended)
- [ ] No missing documentation for critical features

## Definition of Done (Per Module)

At the end of EVERY module/phase, verify the following checklist:

### Code Quality
- [ ] **No TypeScript errors** in frontend code
- [ ] **No Python errors** in backend code
- [ ] **No console errors** in browser
- [ ] **No console warnings** (or documented as acceptable)
- [ ] **Linting passes** (ESLint for frontend, flake8/black for backend)
- [ ] **Type hints** present in Python functions
- [ ] **Modular code** with proper separation of concerns
- [ ] **No duplicated logic** (DRY principle)
- [ ] **No commented-out code** (remove dead code)
- [ ] **No TODO/FIXME placeholders** without associated tickets
- [ ] **Meaningful variable and function names**

### Functionality
- [ ] **All features work** as specified in requirements.md
- [ ] **No fake data** unless explicitly approved for development
- [ ] **No placeholder APIs** - all endpoints functional
- [ ] **Error handling** implemented for all failure scenarios
- [ ] **Loading states** shown during async operations
- [ ] **Success notifications** displayed for user actions
- [ ] **Error notifications** displayed for failures
- [ ] **Input validation** on frontend and backend
- [ ] **Edge cases handled** (empty states, zero results, etc.)

### UI/UX
- [ ] **Responsive design** works on mobile, tablet, desktop
- [ ] **UI matches mockups** (spacing, typography, colors, hierarchy)
- [ ] **Smooth animations** using Framer Motion (subtle, professional)
- [ ] **Accessibility** - proper ARIA labels, keyboard navigation
- [ ] **Loading spinners** for async operations
- [ ] **Empty states** designed and implemented
- [ ] **Error messages** are user-friendly and actionable

### Security
- [ ] **Input sanitization** prevents XSS attacks
- [ ] **SQL injection prevented** (parameterized queries)
- [ ] **Authentication required** for protected routes
- [ ] **Authorization enforced** (users can't access others' data)
- [ ] **Passwords hashed** with bcrypt (never stored plaintext)
- [ ] **Secrets in environment variables** (not in code)
- [ ] **HTTPS ready** (security headers configured)
- [ ] **File validation** prevents malicious uploads

### Testing
- [ ] **Unit tests written** for business logic
- [ ] **Integration tests pass** for API endpoints
- [ ] **Property-based tests pass** (where applicable)
- [ ] **Manual testing completed** for UI flows
- [ ] **No known bugs** in the module
- [ ] **Performance acceptable** (no slow queries, no memory leaks)

### Documentation
- [ ] **Code comments** added where necessary (not obvious code)
- [ ] **API endpoints documented** (request/response examples)
- [ ] **README updated** if setup steps changed
- [ ] **Environment variables documented** if new ones added

### Integration
- [ ] **Frontend communicates with backend** successfully
- [ ] **Database queries work** as expected
- [ ] **External APIs integrate** correctly (Gemini, Tesseract)
- [ ] **No broken dependencies** between modules
- [ ] **Build succeeds** without errors or warnings

## Final Completion Checklist

Before declaring the project COMPLETE, verify ALL of the following:

### Requirements Coverage
- [ ] **All 40 requirements implemented** (reference requirements.md)
- [ ] **All 21 correctness properties validated** (property-based tests)
- [ ] **No scope creep** - only specified features implemented
- [ ] **No missing features** from requirements.md

### UI Completeness
- [ ] **UI matches locked design** (spacing, typography, colors, hierarchy)
- [ ] **All pages implemented**: Landing, Login, Register, Forgot Password, Dashboard, New Analysis, Analysis Result, History, Report Viewer, Profile, Settings, Notifications
- [ ] **Responsive design verified** on multiple screen sizes
- [ ] **Animations smooth and professional** (Framer Motion)
- [ ] **No visual regressions** from mockups

### Backend Completeness
- [ ] **All API endpoints functional** and tested
- [ ] **Authentication system complete** (register, login, password reset, JWT)
- [ ] **Analysis pipeline works** end-to-end (all input types)
- [ ] **Rule-based detection accurate** (financial, identity, salary, urgency, company)
- [ ] **AI integration functional** with fallbacks
- [ ] **Risk scoring correct** (trust score, scam probability, categories)
- [ ] **PDF generation works** for all analyses
- [ ] **Notifications system operational**
- [ ] **Rate limiting enforced**

### Database & Migrations
- [ ] **PostgreSQL schema matches design** (4 tables with indexes)
- [ ] **All migrations applied** successfully
- [ ] **Foreign keys and constraints** configured
- [ ] **JSONB fields** used appropriately for variable data
- [ ] **Indexes optimized** for common queries
- [ ] **No MongoDB references** remain in codebase

### Security Audit
- [ ] **JWT authentication secure** (strong secret, proper expiration)
- [ ] **Password hashing with bcrypt** verified
- [ ] **SQL injection prevented** (parameterized queries)
- [ ] **XSS attacks prevented** (input sanitization)
- [ ] **Rate limiting protects** against abuse
- [ ] **File uploads validated** (size, type, MIME)
- [ ] **CORS restricted** to frontend domain
- [ ] **Security headers configured** (HSTS, CSP, X-Frame-Options)
- [ ] **HTTPS ready** (redirect configured for production)
- [ ] **No secrets in code** (all in environment variables)

### Testing Coverage
- [ ] **All 21 property-based tests pass** (100+ iterations)
- [ ] **Unit test coverage ≥ 85%**
- [ ] **Critical path coverage ≥ 95%**
- [ ] **Integration tests pass** for all API endpoints
- [ ] **Frontend component tests pass**
- [ ] **E2E tests pass** for critical user flows
- [ ] **No failing tests** in test suite
- [ ] **Performance benchmarks met** (analysis ≤ 20s)

### Code Quality
- [ ] **No TypeScript errors**
- [ ] **No Python errors**
- [ ] **No console errors or warnings**
- [ ] **Linting passes** (ESLint + flake8/black)
- [ ] **No dead code** (commented-out code removed)
- [ ] **No TODO placeholders** without tickets
- [ ] **Clean Git history** with meaningful commits
- [ ] **No unused files or dependencies**

### Documentation
- [ ] **README complete** with setup instructions
- [ ] **API documentation accessible** (FastAPI auto-docs)
- [ ] **Environment variables documented** with examples
- [ ] **Database migration guide** included
- [ ] **Deployment instructions** provided
- [ ] **Installation tested** on clean environment
- [ ] **License file** present

### Deployment Readiness
- [ ] **Application runs in production mode** without errors
- [ ] **PostgreSQL connection pooling configured**
- [ ] **Environment variables set** for production
- [ ] **Logging configured** appropriately
- [ ] **Error monitoring** ready (Sentry or similar)
- [ ] **Backup strategy documented**
- [ ] **SSL/TLS certificates** configured
- [ ] **Docker configuration works** (if using Docker)
- [ ] **Deployment tested** on target platform

### User Acceptance
- [ ] **All user stories testable** and tested
- [ ] **Critical user flows work**: Registration → Login → Analysis → View Results → View History → Download PDF
- [ ] **Error messages helpful** and user-friendly
- [ ] **Performance acceptable** for end users
- [ ] **Mobile experience smooth** on real devices (not just emulation)

**If ANY item above is incomplete, the project is NOT DONE. Return to the relevant phase and complete it.**

