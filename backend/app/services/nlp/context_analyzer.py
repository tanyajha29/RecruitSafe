import logging
from typing import Dict, Any
from app.services.nlp.models import ContextMetadata, DependencyToken, NamedEntity

logger = logging.getLogger("recruitsafe")

class ContextAnalyzer:
    """
    Extracts structural context window around a matched spacy span.
    No risk calculation, scoring, or severity metrics.
    """
    def __init__(self):
        logger.info("ContextAnalyzer initialized.")

    @staticmethod
    def analyze_context(doc: Any, span: Any) -> ContextMetadata:
        """
        Analyzes the context surrounding a matched span within a spacy Doc.
        """
        span_sentence = span.sent
        
        # Word window before and after (approx. 40 words)
        start_char = span.start_char
        end_char = span.end_char
        
        text_before = doc.text[:start_char].strip()
        words_before = text_before.split()
        window_before = " ".join(words_before[-40:]) if words_before else ""
        
        text_after = doc.text[end_char:].strip()
        words_after = text_after.split()
        window_after = " ".join(words_after[:40]) if words_after else ""

        # Sentence context
        sentences_list = list(doc.sents)
        sent_index = -1
        for idx, s in enumerate(sentences_list):
            if s.start == span_sentence.start and s.end == span_sentence.end:
                sent_index = idx
                break
                
        previous_sentence = ""
        if sent_index > 0:
            previous_sentence = sentences_list[sent_index - 1].text.strip()
            
        next_sentence = ""
        if sent_index != -1 and sent_index < len(sentences_list) - 1:
            next_sentence = sentences_list[sent_index + 1].text.strip()

        # Dependencies and tokens
        tokens_list = []
        for token in span_sentence:
            tokens_list.append(DependencyToken(
                token=token.text,
                lemma=token.lemma_,
                dependency_label=token.dep_,
                head_token=token.head.text,
                part_of_speech=token.pos_
            ))

        # Entities
        entities_list = []
        for ent in doc.ents:
            if ent.start >= span_sentence.start and ent.end <= span_sentence.end:
                entities_list.append(NamedEntity(
                    text=ent.text,
                    label=ent.label_,
                    start_char=ent.start_char,
                    end_char=ent.end_char
                ))

        # Noun chunks
        noun_chunks_list = []
        for chunk in doc.noun_chunks:
            if chunk.start >= span_sentence.start and chunk.end <= span_sentence.end:
                noun_chunks_list.append(chunk.text.strip())

        return ContextMetadata(
            matched_text=span.text,
            sentence=span_sentence.text.strip(),
            previous_sentence=previous_sentence,
            next_sentence=next_sentence,
            window_before=window_before,
            window_after=window_after,
            tokens=tokens_list,
            dependencies=tokens_list,
            entities=entities_list,
            noun_chunks=noun_chunks_list
        )
