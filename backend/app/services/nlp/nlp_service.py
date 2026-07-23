import spacy
import logging
from typing import Any

logger = logging.getLogger("recruitsafe")

class NLPService:
    _instance = None
    _nlp = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(NLPService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if self._nlp is None:
            logger.info("NLP model loading...")
            try:
                self._nlp = spacy.load("en_core_web_sm")
                logger.info("NLP model loaded.")
            except Exception as e:
                logger.error(f"Failed to load spaCy model en_core_web_sm: {e}")
                raise e

    def analyze(self, text: str) -> Any:
        """
        Processes text through the shared single spaCy pipeline instance and returns a Doc object.
        """
        if not text:
            return self._nlp("")
        return self._nlp(text)
