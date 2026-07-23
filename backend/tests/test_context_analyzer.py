import pytest
from app.services.nlp.nlp_service import NLPService
from app.services.nlp.matcher import Matcher

def test_context_analyzer_scenarios():
    nlp = NLPService()
    matcher = Matcher()

    # Scenario 1: Certification
    text1 = "Candidates may complete an optional paid certification."
    doc1 = nlp.analyze(text1)
    matches1 = matcher.match_training_terms(doc1)
    
    print("\n\n=== Scenario 1: Certification ===")
    assert len(matches1) > 0
    for match in matches1:
        ctx = match.context
        print(f"Matched Text: {match.matched_text}")
        print(f"Sentence: {ctx.sentence}")
        print(f"Tokens/Deps Count: {len(ctx.tokens)}")
        print(f"Entities: {ctx.entities}")
        print(f"Noun Chunks: {ctx.noun_chunks}")
        print(f"Window Before: '{ctx.window_before}'")
        print(f"Window After: '{ctx.window_after}'")
        assert "certification" in match.matched_text
        assert ctx.sentence == text1

    # Scenario 2: Payment Fee
    text2 = "Pay INR 500 registration fee before interview."
    doc2 = nlp.analyze(text2)
    matches2 = matcher.match_payment_terms(doc2)

    print("\n=== Scenario 2: Payment ===")
    assert len(matches2) > 0
    for match in matches2:
        ctx = match.context
        print(f"Matched Text: {match.matched_text}")
        print(f"Sentence: {ctx.sentence}")
        print(f"Entities: {ctx.entities}")
        print(f"Noun Chunks: {ctx.noun_chunks}")
        assert "fee" in match.matched_text or "payment" in match.matched_text

    # Scenario 3: Training reimbursement
    text3 = "Training costs will be reimbursed after joining."
    doc3 = nlp.analyze(text3)
    matches3 = matcher.match_training_terms(doc3)

    print("\n=== Scenario 3: Training ===")
    assert len(matches3) > 0
    for match in matches3:
        ctx = match.context
        print(f"Matched Text: {match.matched_text}")
        print(f"Sentence: {ctx.sentence}")
        print(f"Noun Chunks: {ctx.noun_chunks}")
        assert "training" in match.matched_text.lower()

    # Scenario 4: Telegram app
    text4 = "Contact us only on Telegram."
    doc4 = nlp.analyze(text4)
    matches4 = matcher.match_telegram_terms(doc4)

    print("\n=== Scenario 4: Telegram ===")
    assert len(matches4) > 0
    for match in matches4:
        ctx = match.context
        print(f"Matched Text: {match.matched_text}")
        print(f"Sentence: {ctx.sentence}")
        print(f"Noun Chunks: {ctx.noun_chunks}")
        assert "telegram" in match.matched_text.lower()

if __name__ == "__main__":
    test_context_analyzer_scenarios()
