from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, ASCENDING

class PasswordResetToken(Document):
    user_id: PydanticObjectId
    token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used: bool = False

    class Settings:
        name = "password_reset_tokens"
        indexes = [
            IndexModel([("token", ASCENDING)], unique=True),
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("expires_at", ASCENDING)])
        ]
