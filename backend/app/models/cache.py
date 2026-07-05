from datetime import datetime
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING

class CacheEntry(Document):
    """
    MongoDB-backed cache for DNS, WHOIS, SSL, and Gemini API requests.
    Features a MongoDB TTL index to automatically purge expired records.
    """
    key: str  # Unique hash or domain name
    value: dict  # Serialized dictionary value cache
    expires_at: datetime  # Time at which MongoDB purges this record

    class Settings:
        name = "caches"
        indexes = [
            IndexModel([("key", ASCENDING)], unique=True),
            # MongoDB automatically deletes documents when their 'expires_at' passes
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0)
        ]
