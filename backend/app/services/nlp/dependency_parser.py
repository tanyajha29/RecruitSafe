import logging
from typing import Dict, Any

logger = logging.getLogger("recruitsafe")

class DependencyParser:
    """
    Parses structural linguistic components from a processed spaCy Doc.
    No business logic or risk analysis.
    """
    def __init__(self):
        logger.info("DependencyParser initialized.")

    @staticmethod
    def parse(doc: Any) -> Dict[str, Any]:
        """
        Extracts structural tokens, sentences, entities, and noun chunks from a doc.
        """
        sentences = [sent.text.strip() for sent in doc.sents]
        
        entities = [
            {"text": ent.text, "label": ent.label_, "start_char": ent.start_char, "end_char": ent.end_char}
            for ent in doc.ents
        ]
        
        noun_chunks = [chunk.text.strip() for chunk in doc.noun_chunks]
        
        dependency_tree = [
            {
                "text": token.text,
                "dep": token.dep_,
                "head_text": token.head.text,
                "head_pos": token.head.pos_,
                "pos": token.pos_
            }
            for token in doc
        ]
        
        return {
            "sentences": sentences,
            "entities": entities,
            "noun_chunks": noun_chunks,
            "dependency_tree": dependency_tree
        }
