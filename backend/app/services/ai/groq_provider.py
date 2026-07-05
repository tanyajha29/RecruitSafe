import logging
import asyncio
from typing import List, Dict, Any, Optional
from groq import AsyncGroq, GroqError
from groq.types.chat import ChatCompletion

from app.config import settings
from app.services.ai.ai_provider import AIService
from app.services.ai.prompt_builder import PromptBuilder
from app.services.ai.response_parser import parse_and_validate_analysis, generate_local_fallback

logger = logging.getLogger("recruitsafe")

class GroqProvider(AIService):
    """
    Concrete implementation of AIService utilizing the Groq Chat Completions API.
    Supports asynchronous completions, configurable models, exponential backoff,
    and fallback reasoning.
    """
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = settings.GROQ_MODEL
        self.enabled = False
        self.client = None

        if self.api_key and self.api_key != "mock_gemini_api_key" and self.api_key != "mock_groq_api_key":
            try:
                # Initialize AsyncGroq client
                self.client = AsyncGroq(api_key=self.api_key)
                self.enabled = True
                logger.info(f"Groq AI Service initialized successfully with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.enabled = False
        else:
            logger.warning("No valid GROQ_API_KEY found. Running in mock/fallback mode.")
            self.enabled = False

    async def _execute_with_backoff(self, prompt: str, temperature: float = 0.1, max_retries: int = 3, initial_delay: float = 1.0) -> str:
        """
        Executes a chat completion call with exponential backoff on retryable exceptions.
        """
        if not self.client:
            raise GroqError("Groq client is not initialized.")

        delay = initial_delay
        last_exception = None

        for attempt in range(max_retries):
            try:
                logger.info(f"Sending prompt to Groq (Attempt {attempt + 1}/{max_retries})...")
                # Enforce a reasonable timeout per request (e.g. 15 seconds)
                completion: ChatCompletion = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        model=self.model_name,
                        temperature=temperature
                    ),
                    timeout=15.0
                )
                
                content = completion.choices[0].message.content
                if not content:
                    raise ValueError("Groq returned an empty response body.")
                return content.strip()

            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(f"Groq request timed out on attempt {attempt + 1}.")
            except Exception as e:
                last_exception = e
                # Check for rate limits, connection errors, or temporary HTTP issues
                err_msg = str(e).lower()
                is_retryable = "429" in err_msg or "rate limit" in err_msg or "timeout" in err_msg or "connection" in err_msg
                
                if not is_retryable:
                    logger.error(f"Non-retryable Groq exception: {e}")
                    raise e
                
                logger.warning(f"Retryable Groq exception on attempt {attempt + 1}: {e}")

            # Apply exponential backoff wait
            if attempt < max_retries - 1:
                wait_time = delay * (2.0 ** attempt)
                logger.info(f"Retrying Groq API call in {wait_time:.2f} seconds...")
                await asyncio.sleep(wait_time)

        raise last_exception or GroqError("Groq API execution failed after all retry attempts.")

    async def generate_job_summary(self, text: str) -> str:
        """
        Generates a concise 2-3 sentence overview of the job description text.
        """
        if not self.enabled:
            fallback = generate_local_fallback(text, [])
            return fallback["ai_summary"]

        try:
            prompt = PromptBuilder.build_summary_prompt(text)
            summary = await self._execute_with_backoff(prompt)
            return summary
        except Exception as e:
            logger.error(f"Groq summary generation failed: {e}. Falling back to local heuristics.")
            fallback = generate_local_fallback(text, [])
            return fallback["ai_summary"]

    async def analyze_job(self, text: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs semantic reasoning for safety analysis.
        Validates JSON responses against Pydantic models.
        """
        if not self.enabled:
            return generate_local_fallback(text, evidence)

        try:
            prompt = PromptBuilder.build_analysis_prompt(text, evidence)
            response_text = await self._execute_with_backoff(prompt)
            
            # Parse and validate response text using Pydantic schemas
            parsed_analysis = parse_and_validate_analysis(response_text)
            logger.info("Groq analysis parsed and validated successfully against Pydantic schema.")
            return parsed_analysis
            
        except Exception as e:
            logger.error(f"Groq analysis reasoning failed: {e}. Falling back to local heuristic reasoning.")
            return generate_local_fallback(text, evidence)

class MockProvider(AIService):
    """
    Mock AI Provider implementation that runs entirely locally using heuristics.
    Useful for unit testing, rate-limited developers, or offline testing.
    """
    def __init__(self):
        self.enabled = False

    async def generate_job_summary(self, text: str) -> str:
        fallback = generate_local_fallback(text, [])
        return fallback["ai_summary"]

    async def analyze_job(self, text: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        return generate_local_fallback(text, evidence)
