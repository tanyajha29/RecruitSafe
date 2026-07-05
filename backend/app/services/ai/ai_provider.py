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
        provider = AIFactory.get_provider()
        return await provider.analyze_job(text, evidence)

# Export a single global proxy instance that other services can import directly
ai_service = AIProxy()
