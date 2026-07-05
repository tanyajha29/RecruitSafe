from datetime import datetime
from typing import Optional
from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, ASCENDING, DESCENDING

class Notification(Document):
    user_id: PydanticObjectId
    type: str  # "analysis_started", "analysis_complete", "upload_error", "pdf_ready"
    title: str
    message: str
    analysis_id: Optional[PydanticObjectId] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("user_id", ASCENDING), ("is_read", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)])
        ]
