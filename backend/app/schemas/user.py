from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., description="User password")
    full_name: str = Field(..., min_length=1, description="User full name")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Enforce strict validation matching requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - One lowercase letter
        - One number
        - One special character
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(...)

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        # Re-use password validation logic for resetting
        return RegisterRequest.validate_password_strength(v)

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: datetime
    last_login: Optional[datetime] = None

    @field_validator("id", mode="before")
    @classmethod
    def serialize_id(cls, v):
        if v is not None:
            return str(v)
        return v

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Profile Requests
class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., description="New password strength validated")

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        return RegisterRequest.validate_password_strength(v)
