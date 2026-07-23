import os
import json
import logging
from typing import Dict, Any
from app.services.nlp.models import ContextMetadata

logger = logging.getLogger("recruitsafe")

# Resolve configuration file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SEVERITY_CONFIG_PATH = os.path.join(BASE_DIR, "config", "severity_config.json")
SCORE_CONFIG_PATH = os.path.join(BASE_DIR, "config", "score_config.json")


class IntentClassifier:
    """
    Classifies a matched context into semantic intents based on dependency
    relationships, noun phrases, and surrounding linguistic modifiers.
    """
    @staticmethod
    def classify(context: Any) -> str:
        if isinstance(context, str):
            sentence = context.lower()
            matched = ""
        else:
            sentence = context.sentence.lower()
            matched = context.matched_text.lower()
                
        # 1. Check for reimbursement
        if any(w in sentence for w in ["reimburse", "refund", "pay back", "returned", "refunding"]):
            return "COMPANY_REIMBURSEMENT"
            
        # 2. Check for optional training/certification
        if any(w in sentence for w in ["optional", "voluntary", "choose", "may complete", "may undergo"]):
            return "OPTIONAL_TRAINING"
            
        # 3. Check for training vs general payment
        if "training" in sentence or "certification" in sentence or "course" in sentence:
            if any(w in sentence for w in ["must", "required", "mandatory", "before", "fee", "cost"]):
                return "MANDATORY_TRAINING"
            return "OPTIONAL_TRAINING"
            
        # 4. Check for mandatory payment (e.g. registration fee)
        if any(w in sentence for w in ["fee", "deposit", "payment", "pay", "charge", "cost"]):
            return "MANDATORY_PAYMENT"

        # 5. Check for no interview
        if any(w in sentence for w in ["no interview", "without interview", "direct joining", "direct selection", "spot selection"]):
            return "NO_INTERVIEW"

        # 6. Check for urgent recruitment
        if any(w in sentence for w in ["urgent", "immediate", "hurry", "within"]):
            return "URGENT_RECRUITMENT"

        # 7. Check for communication intents (Telegram, WhatsApp)
        if "telegram" in sentence or "whatsapp" in sentence:
            if any(w in sentence for w in ["only", "must", "mandatory", "exclusively", "solely", "required"]):
                return "MANDATORY_COMMUNICATION"
            else:
                return "OPTIONAL_COMMUNICATION"
            
        return "UNKNOWN"


class SeverityCalculator:
    """
    Maps dynamic context intents to severity levels using configuration settings.
    """
    _config: Dict[str, str] = {}

    @classmethod
    def _load_config(cls) -> None:
        if not cls._config:
            try:
                with open(SEVERITY_CONFIG_PATH, "r", encoding="utf-8") as f:
                    cls._config = json.load(f)
                logger.info("SeverityCalculator: Config loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load severity_config.json: {e}")
                cls._config = {
                    "MANDATORY_PAYMENT": "HIGH",
                    "OPTIONAL_TRAINING": "LOW",
                    "COMPANY_REIMBURSEMENT": "NONE",
                    "MANDATORY_TRAINING": "HIGH",
                    "MANDATORY_COMMUNICATION": "HIGH",
                    "OPTIONAL_COMMUNICATION": "NONE",
                    "UNKNOWN": "LOW"
                }

    @classmethod
    def calculate(cls, intent: str) -> str:
        cls._load_config()
        return cls._config.get(intent, "LOW")


class RuleScoreMapper:
    """
    Maps severity levels to point deduction scores using configuration settings.
    """
    _config: Dict[str, int] = {}

    @classmethod
    def _load_config(cls) -> None:
        if not cls._config:
            try:
                with open(SCORE_CONFIG_PATH, "r", encoding="utf-8") as f:
                    cls._config = json.load(f)
                logger.info("RuleScoreMapper: Config loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load score_config.json: {e}")
                cls._config = {
                    "NONE": 0,
                    "LOW": 5,
                    "MEDIUM": 20,
                    "HIGH": 40,
                    "CRITICAL": 60
                }

    @classmethod
    def map_severity_to_score(cls, severity: str) -> int:
        cls._load_config()
        return cls._config.get(severity, 5)
