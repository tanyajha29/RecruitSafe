import time
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_db
from app.utils.logger import setup_logging
from app.routers import auth, profile, analysis, history, notifications, dashboard, report

# Setup application logging
setup_logging(log_level_str=settings.LOG_LEVEL, environment=settings.ENVIRONMENT)
logger = logging.getLogger("recruitsafe")

# Lifespan event handler for FastAPI startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting RecruitSafe FastAPI application...")
    import os
    os.makedirs("uploads", exist_ok=True)
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database on startup: {e}")
    yield
    # Shutdown
    logger.info("Shutting down RecruitSafe FastAPI application...")

# Initialize Limiter for Rate Limiting
limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.RATE_LIMIT_ENABLED,
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS_PER_HOUR}/hour"]
)

app = FastAPI(
    title="RecruitSafe API",
    description="AI-Powered Fake Job and Internship Detection Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Connect slowapi rate limit state & exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS Middleware
# Restricts domain calls only to the verified Frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Security Headers & Request Correlation ID Middleware
@app.middleware("http")
async def process_request_middleware(request: Request, call_next):
    # Set request correlation ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    # Store request id on request state so it is accessible in handlers
    request.state.request_id = request_id
    
    start_time = time.time()
    
    # Execute request
    response: Response = await call_next(request)
    
    # Calculate processing time
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Log structured request details
    logger.info(
        f"{request.method} {request.url.path} finished with status {response.status_code} in {duration_ms}ms",
        extra={
            "request_id": request_id,
            "processing_time_ms": duration_ms
        }
    )
    
    # Add Security Headers
    response.headers["X-Request-ID"] = request_id
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response

# Structured Error Handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Formats standard FastAPI HTTPExceptions into our standardized JSON error structure.
    """
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": {"request_id": request_id}
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Formats Pydantic request body validation errors into our standardized structure.
    """
    request_id = getattr(request.state, "request_id", None)
    # Simplify error details for JSON payload
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        errors.append({
            "field": loc,
            "message": err.get("msg"),
            "type": err.get("type")
        })
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_FAILED",
                "message": "Input validation failed. Please check your inputs.",
                "details": {
                    "request_id": request_id,
                    "validation_errors": errors
                }
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handles uncaught backend exceptions, logging them structured and returning a clean 500 error.
    """
    request_id = getattr(request.state, "request_id", None)
    logger.error(
        f"Unhandled exception encountered: {exc}",
        exc_info=True,
        extra={"request_id": request_id}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred on the server. Please try again later.",
                "details": {"request_id": request_id}
            }
        }
    )

# Register Module Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(analysis.router)
app.include_router(history.router)
app.include_router(notifications.router)
app.include_router(dashboard.router)
app.include_router(report.router)

@app.get("/")
async def root():
    return {
        "app": "RecruitSafe API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/api/health/ai")
async def health_ai():
    import time
    from fastapi.responses import JSONResponse
    from app.services.ai.ai_provider import AIFactory
    
    start_time = time.time()
    provider_name = settings.AI_PROVIDER
    
    if provider_name.lower().strip() == "groq":
        model_name = settings.GROQ_MODEL
    elif provider_name.lower().strip() == "gemini":
        model_name = settings.GEMINI_MODEL
    else:
        model_name = "mock"

    fallback_available = True
    
    try:
        provider = AIFactory.get_provider()
        # Verify connectivity using a tiny string summary check
        await provider.generate_job_summary("Ping")
        latency_ms = int((time.time() - start_time) * 1000)
        
        return {
            "status": "healthy",
            "provider": provider_name,
            "model": model_name,
            "latency_ms": latency_ms,
            "fallback_available": fallback_available
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "provider": provider_name,
                "model": model_name,
                "latency_ms": latency_ms,
                "fallback_available": fallback_available,
                "error": str(e)
            }
        )
