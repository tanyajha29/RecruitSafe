import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr

class Settings(BaseSettings):
    # Application Mode & Logging
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000

    # Database Configuration (MongoDB Atlas/Local URI)
    MONGODB_URI: str

    # Authentication Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # AI Engine Integration (Multi-Provider Support)
    AI_PROVIDER: str = "groq"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Tesseract OCR Configuration
    TESSERACT_CMD: str = "tesseract"

    # SMTP Configuration (Optional during local development)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = "noreply@recruitsafe.com"

    # Security & Protection limits
    FRONTEND_URL: str = "http://localhost:5173"
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 100

    # Pydantic Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate the settings instance
settings = Settings()
