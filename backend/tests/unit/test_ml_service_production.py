import threading
import pytest
from app.services.ml.ml_service import MLService
from app.config import settings

def test_ml_health_endpoint():
    """Verify that health endpoint lazy-loads models and returns correct status schemas."""
    status = MLService.health()
    assert "loaded" in status
    assert "model_name" in status
    assert "model_version" in status
    assert "vectorizer_loaded" in status
    assert "model_loaded" in status
    assert status["loaded"] is True
    assert status["model_name"] == "recruitsafe_xgb"

def test_ml_metadata_exposed():
    """Verify metadata parameters are exposed correctly as class properties."""
    MLService.health() # Ensure loaded
    assert MLService.model_name == "recruitsafe_xgb"
    assert MLService.model_version == "1.0.0"
    assert MLService.dataset_version == "v4_golden"
    assert MLService.algorithm == "XGBoost Classifier"

def test_ml_input_validation():
    """Verify invalid inputs return default safe values without logging exceptions."""
    # Test None
    pred, prob = MLService.predict(None)
    assert pred == 0
    assert prob == 0.0

    # Test Empty String
    pred, prob = MLService.predict("")
    assert pred == 0
    assert prob == 0.0

    # Test Whitespace
    pred, prob = MLService.predict("    ")
    assert pred == 0
    assert prob == 0.0

def test_ml_caching_and_redundant_inference():
    """Verify caching minimizes inference runs by returning identical predictions."""
    test_text = "Acme Corp is hiring software engineer assistant."
    
    # First run (populates cache)
    pred1, prob1 = MLService.predict(test_text)
    
    # Check cache presence
    import hashlib
    text_hash = hashlib.sha256(test_text.strip().encode("utf-8")).hexdigest()
    assert text_hash in MLService._cache

    # Second run (cache hit)
    pred2, prob2 = MLService.predict(test_text)
    assert pred1 == pred2
    assert prob1 == prob2

def test_ml_threshold_configuration():
    """Verify prediction adapts correctly based on configurable ML classification threshold."""
    test_text = "Acme Corp is hiring software engineer assistant."
    
    # Save original threshold
    orig_threshold = settings.ML_THRESHOLD

    # Clear cache to force clean inference evaluation
    MLService._cache.clear()

    try:
        # High threshold (e.g. 0.99) should predict 0
        settings.ML_THRESHOLD = 0.99
        pred_high, prob_high = MLService.predict(test_text)
        assert pred_high == 0

        # Clear cache again
        MLService._cache.clear()

        # Low threshold (e.g. 0.01) should predict 1
        settings.ML_THRESHOLD = 0.01
        pred_low, prob_low = MLService.predict(test_text)
        if prob_low > 0.01:
            assert pred_low == 1
    finally:
        # Restore threshold
        settings.ML_THRESHOLD = orig_threshold

def test_ml_thread_safety_lazy_loading():
    """Verify concurrent lazy loading queries do not result in race conditions."""
    # Force reset model load states
    MLService._vectorizer = None
    MLService._model = None

    def load_task():
        MLService.health()

    threads = [threading.Thread(target=load_task) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert MLService._vectorizer is not None
    assert MLService._model is not None
