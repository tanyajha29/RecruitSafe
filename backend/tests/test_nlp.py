import pytest
from app.services.nlp.nlp_service import NLPService
from app.services.nlp.dependency_parser import DependencyParser
from app.services.nlp.matcher import Matcher
from app.services.nlp.context_analyzer import ContextAnalyzer
from app.services.nlp.intent_classifier import IntentClassifier

def test_nlp_infrastructure_run():
    nlp = NLPService()
    parser = DependencyParser()
    matcher = Matcher()
    analyzer = ContextAnalyzer()
    classifier = IntentClassifier()

    text = "Candidates may complete an optional paid certification."
    print(f"\n--- Processing Sample Text: '{text}' ---")
    
    doc = nlp.analyze(text)

    parsed = parser.parse(doc)
    print("\n[Sentences]")
    for s in parsed["sentences"]:
        print(f" - {s}")

    print("\n[Noun Chunks]")
    for nc in parsed["noun_chunks"]:
        print(f" - {nc}")

    print("\n[Tokens & Dependencies]")
    for token in parsed["dependency_tree"]:
        print(f" - Token: {token['text']:15} | Relation: {token['dep']:8} | Head: {token['head_text']:12} ({token['pos']})")

    payment_matches = matcher.match_payment_terms(doc)
    training_matches = matcher.match_training_terms(doc)
    
    print("\n[Matched Phrases]")
    for match in payment_matches:
        print(f" - Payment match: '{match.matched_text}' (Label: {match.label})")
        print(f"   Context: {match.context.model_dump()}")
        
    for match in training_matches:
        print(f" - Training match: '{match.matched_text}' (Label: {match.label})")
        print(f"   Context: {match.context.model_dump()}")

    intent = classifier.classify(text)
    print(f"\n[Intent Classifier Result]\n - Intent: {intent}")

    assert doc is not None
    assert len(parsed["sentences"]) == 1
    assert intent == "OPTIONAL_TRAINING"

if __name__ == "__main__":
    test_nlp_infrastructure_run()
