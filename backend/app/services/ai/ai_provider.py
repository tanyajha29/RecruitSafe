import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger("recruitsafe")

class AIService(ABC):
    """
    Abstract Base Class defining the AI Service layer.
    Ensures that business logic remains decoupled from specific AI vendor APIs.
    """
    @abstractmethod
    async def generate_job_summary(self, text: str) -> str:
        """Generates a brief 2-3 sentence summary of a job description."""
        pass

    @abstractmethod
    async def analyze_job(self, text: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Performs semantic analysis, classifies safety and manipulation dimensions,
        and returns structured reasoning including classifications, summary,
        explanation, and recommendations.
        """
        pass

    @abstractmethod
    async def extract_missing_fields(self, text: str, missing_fields: List[str]) -> Dict[str, str]:
        """
        Uses AI to extract values for missing fields from the job description text.
        """
        pass

class AIFactory:
    """
    Factory to dynamically resolve and cache AI provider instances based on configuration.
    """
    _instances: Dict[str, AIService] = {}

    @classmethod
    def get_provider(cls) -> AIService:
        provider_name = settings.AI_PROVIDER.lower().strip()
        if provider_name not in cls._instances:
            if provider_name == "groq":
                from app.services.ai.groq_provider import GroqProvider
                cls._instances[provider_name] = GroqProvider()
            elif provider_name == "mock":
                from app.services.ai.groq_provider import MockProvider
                cls._instances[provider_name] = MockProvider()
            else:
                logger.warning(f"Unsupported AI_PROVIDER '{provider_name}'. Defaulting to MockProvider.")
                from app.services.ai.groq_provider import MockProvider
                cls._instances[provider_name] = MockProvider()
        return cls._instances[provider_name]

import hashlib
from datetime import datetime, timezone, timedelta
from app.models.cache import CacheEntry

class AIProxy(AIService):
    """
    Proxy wrapper that forwards all AI request invocations to the configured AI provider.
    Allows changing providers at runtime without re-instantiating importing clients.
    """
    @property
    def enabled(self) -> bool:
        provider = AIFactory.get_provider()
        return getattr(provider, "enabled", False)

    async def generate_job_summary(self, text: str) -> str:
        provider = AIFactory.get_provider()
        return await provider.generate_job_summary(text)

    async def analyze_job(self, text: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        # 1. Normalize input text and evidence list for deterministic cache hashing
        normalized_str = "".join(text.lower().split())
        evidence_keys = sorted([str(ev.get("id", "")) for ev in evidence])
        hash_input = f"{normalized_str}:{','.join(evidence_keys)}"
        
        md5_hash = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
        cache_key = f"ai_analysis:{md5_hash}"
        
        try:
            cached = await CacheEntry.find_one({"key": cache_key})
            if cached and cached.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                logger.info(f"AI response cache HIT for key: {cache_key}")
                return cached.value
        except Exception as e:
            logger.warning(f"Cache check failed in AIProxy: {e}")

        provider = AIFactory.get_provider()
        result = await provider.analyze_job(text, evidence)

        # 2. Store in cache for 24 hours
        try:
            await CacheEntry.find_one({"key": cache_key}).upsert(
                {"$set": {
                    "value": result,
                    "expires_at": datetime.utcnow() + timedelta(hours=24)
                }},
                on_insert=CacheEntry(
                    key=cache_key,
                    value=result,
                    expires_at=datetime.utcnow() + timedelta(hours=24)
                )
            )
            logger.info(f"AI response cached successfully under key: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache save failed in AIProxy: {e}")

        return result

    async def extract_missing_fields(self, text: str, missing_fields: List[str]) -> Dict[str, str]:
        provider = AIFactory.get_provider()
        return await provider.extract_missing_fields(text, missing_fields)

# Export a single global proxy instance that other services can import directly
ai_service = AIProxy()
