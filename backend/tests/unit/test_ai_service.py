import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from groq import GroqError

from app.services.ai.ai_provider import AIFactory, ai_service, AIProxy
from app.services.ai.groq_provider import GroqProvider, MockProvider
from app.services.ai.response_parser import parse_and_validate_analysis, generate_local_fallback

@pytest.mark.asyncio
async def test_factory_resolution():
    """
    Verifies that the factory resolves the correct AI provider class based on config.
    """
    with patch("app.config.settings.AI_PROVIDER", "groq"):
        provider = AIFactory.get_provider()
        assert isinstance(provider, GroqProvider)

    with patch("app.config.settings.AI_PROVIDER", "mock"):
        # Clear cached instances to force reload
        AIFactory._instances.pop("mock", None)
        provider = AIFactory.get_provider()
        assert isinstance(provider, MockProvider)

@pytest.mark.asyncio
async def test_mock_provider_heuristics():
    """
    Verifies that the MockProvider runs fully local fallback heuristic reasoning.
    """
    provider = MockProvider()
    text = "Software Developer at Infosys. Rs 5 Lakhs per annum. Urgent requirements."
    evidence = [
        {"category": "urgency", "id": "urgent_deadline", "severity": "medium", "score": -10}
    ]

    summary = await provider.generate_job_summary(text)
    assert isinstance(summary, str)
    assert "Infosys" in summary or "job listing" in summary

    analysis = await provider.analyze_job(text, evidence)
    assert isinstance(analysis, dict)
    assert analysis["overall_risk"] == "Suspicious"
    assert len(analysis["red_flags"]) == 1
    assert "payment_requests" in analysis

@pytest.mark.asyncio
async def test_groq_provider_fallback_on_invalid_key():
    """
    Verifies that GroqProvider gracefully degrades and returns local fallbacks
    if it is initialized with invalid/empty keys.
    """
    with patch("app.config.settings.GROQ_API_KEY", "mock_groq_api_key"):
        provider = GroqProvider()
        assert provider.enabled is False
        
        text = "TCS Trainee Position. Rs 1500 registration deposit needed."
        evidence = [
            {"category": "financial_fraud", "id": "registration_fee", "severity": "high", "score": -25}
        ]
        
        summary = await provider.generate_job_summary(text)
        assert isinstance(summary, str)
        assert "TCS" in summary or "job listing" in summary
        
        analysis = await provider.analyze_job(text, evidence)
        assert isinstance(analysis, dict)
        assert analysis["overall_risk"] == "High Risk"
        assert analysis["payment_requests"] == "High"

@pytest.mark.asyncio
async def test_groq_provider_api_error_handling():
    """
    Verifies that GroqProvider catches API connection/execution errors
    and degrades gracefully without throwing crashes to callers.
    """
    provider = GroqProvider()
    # Force enabled to simulate a registered client that fails during execution
    provider.enabled = True
    provider.client = MagicMock()
    
    # Mock the wait_for call to throw a GroqError
    with patch("asyncio.wait_for", side_effect=GroqError("API Rate Limit exceeded 429")):
        text = "Software intern role."
        summary = await provider.generate_job_summary(text)
        # Should return local fallback summary
        assert "Software intern" in summary or "job listing" in summary
