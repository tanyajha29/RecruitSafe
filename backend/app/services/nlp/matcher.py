import logging
from typing import List, Any
from spacy.matcher import Matcher as SpacyMatcher
from spacy.matcher import PhraseMatcher
from app.services.nlp.nlp_service import NLPService
from app.services.nlp.context_analyzer import ContextAnalyzer
from app.services.nlp.models import MatchedPhrase

logger = logging.getLogger("recruitsafe")

class Matcher:
    """
    Centralizes Matcher and PhraseMatcher rules.
    Provides reusable match functions returning list of MatchedPhrase models.
    """
    def __init__(self):
        nlp_service = NLPService()
        self.nlp = nlp_service._nlp
        
        self.matcher = SpacyMatcher(self.nlp.vocab)
        self.phrase_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        
        self._init_phrase_matchers()
        logger.info("Matcher initialized.")

    def _init_phrase_matchers(self):
        # 1. Payment Terms
        payment_phrases = ["fee", "deposit", "payment", "bank transfer", "upfront payment", "pay registration", "credit card"]
        payment_patterns = [self.nlp.make_doc(text) for text in payment_phrases]
        self.phrase_matcher.add("PAYMENT", payment_patterns)

        # 2. Salary Terms
        salary_phrases = ["salary", "lpa", "usd", "salary range", "compensation", "package", "stipend"]
        salary_patterns = [self.nlp.make_doc(text) for text in salary_phrases]
        self.phrase_matcher.add("SALARY", salary_patterns)

        # 3. Telegram Terms
        telegram_phrases = ["telegram", "t.me", "telegram app", "telegram messenger"]
        telegram_patterns = [self.nlp.make_doc(text) for text in telegram_phrases]
        self.phrase_matcher.add("TELEGRAM", telegram_patterns)

        # 4. Whatsapp Terms
        whatsapp_phrases = ["whatsapp", "wa.me", "whatsapp contact", "whatsapp chat"]
        whatsapp_patterns = [self.nlp.make_doc(text) for text in whatsapp_phrases]
        self.phrase_matcher.add("WHATSAPP", whatsapp_patterns)

        # 5. Training Terms
        training_phrases = ["training", "paid training", "course fee", "mandatory training", "certification course", "certification", "paid certification"]
        training_patterns = [self.nlp.make_doc(text) for text in training_phrases]
        self.phrase_matcher.add("TRAINING", training_patterns)

    def _wrap_and_log_matches(self, doc: Any, matches: List[Any], label_filter: str) -> List[MatchedPhrase]:
        wrapped = []
        for span in matches:
            if span.label_ == label_filter:
                context = ContextAnalyzer.analyze_context(doc, span)
                
                # Rule-specific logging requirements:
                # Rule ID, Matched phrase, Sentence extracted, Entities found, Window size.
                entities_str = ", ".join([ent.text for ent in context.entities]) or "None"
                w_before_count = len(context.window_before.split())
                w_after_count = len(context.window_after.split())
                
                logger.info(
                    f"Match Analyzed: Rule ID={span.label_} | Phrase='{span.text}' | "
                    f"Sentence='{context.sentence}' | Entities={entities_str} | "
                    f"Window Size: before={w_before_count} words, after={w_after_count} words"
                )

                wrapped.append(MatchedPhrase(
                    matched_text=span.text,
                    label=span.label_,
                    start_char=span.start_char,
                    end_char=span.end_char,
                    context=context
                ))
        return wrapped

    def match_payment_terms(self, doc: Any) -> List[MatchedPhrase]:
        matches = self.phrase_matcher(doc, as_spans=True)
        return self._wrap_and_log_matches(doc, matches, "PAYMENT")

    def match_salary_terms(self, doc: Any) -> List[MatchedPhrase]:
        matches = self.phrase_matcher(doc, as_spans=True)
        return self._wrap_and_log_matches(doc, matches, "SALARY")

    def match_telegram_terms(self, doc: Any) -> List[MatchedPhrase]:
        matches = self.phrase_matcher(doc, as_spans=True)
        return self._wrap_and_log_matches(doc, matches, "TELEGRAM")

    def match_whatsapp_terms(self, doc: Any) -> List[MatchedPhrase]:
        matches = self.phrase_matcher(doc, as_spans=True)
        return self._wrap_and_log_matches(doc, matches, "WHATSAPP")

    def match_training_terms(self, doc: Any) -> List[MatchedPhrase]:
        matches = self.phrase_matcher(doc, as_spans=True)
        return self._wrap_and_log_matches(doc, matches, "TRAINING")
