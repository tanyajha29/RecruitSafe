import os
import json
import logging
import hashlib
import threading
import joblib
from typing import Tuple, Dict, Any, Optional

from app.config import settings

logger = logging.getLogger("recruitsafe")

class MLService:
    """
    MLService encapsulates loading the scikit-learn TF-IDF vectorizer and
    the XGBoost classifier, running predictions with threat validation, caching
    recent inferences, and exposing service metadata and load health statistics.

    Lifecycle:
        - Lazy loads model pickles on the first predict() or health() call.
        - Synchronized via a thread Lock to prevent duplicate startup requests.
        - Caches inferences to minimize redundant computations.
    """
    _vectorizer = None
    _model = None
    _lock = threading.Lock()
    _cache = {}
    _cache_lock = threading.Lock()
    _cache_limit = 100

    # Metadata fields
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    dataset_version: Optional[str] = None
    algorithm: Optional[str] = None
    trained_at: Optional[str] = None

    @classmethod
    def _resolve_path(cls, config_path: str) -> str:
        """Resolves config path relative to project root directory if not absolute."""
        if os.path.isabs(config_path):
            return config_path
        
        # Traverse up three levels (app/services/ml/ -> backend/) to locate project root
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        return os.path.join(base_dir, config_path)

    @classmethod
    def _load_metadata(cls):
        """Loads metadata.json if present without blocking loading lifecycle."""
        meta_path = cls._resolve_path(settings.ML_METADATA_PATH)
        if not os.path.exists(meta_path):
            logger.info("MLService: Model metadata file not found. Running with empty metadata.")
            return

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            cls.model_name = meta.get("model_name")
            cls.model_version = meta.get("model_version")
            cls.dataset_version = meta.get("dataset_version")
            cls.algorithm = meta.get("algorithm")
            cls.trained_at = meta.get("trained_at")
            logger.info(f"MLService: Loaded model metadata: name={cls.model_name}, version={cls.model_version}")
        except Exception as e:
            logger.warning(f"MLService: Non-blocking metadata parse failure: {e}")

    @classmethod
    def _load_models(cls):
        """Thread-safe lazy initialization of the vectorizer and model pickles."""
        if cls._vectorizer is not None and cls._model is not None:
            return

        with cls._lock:
            # Double check to prevent initialization race conditions
            if cls._vectorizer is not None and cls._model is not None:
                return

            model_path = cls._resolve_path(settings.ML_MODEL_PATH)
            vectorizer_path = cls._resolve_path(settings.ML_VECTORIZER_PATH)

            logger.info("MLService: Starting model loading pipeline...")

            # 1. Load Metadata
            cls._load_metadata()

            # 2. Verify files presence
            if not os.path.exists(model_path):
                logger.error(f"MLService: Missing model pickle file at: {model_path}")
                return
            if not os.path.exists(vectorizer_path):
                logger.error(f"MLService: Missing vectorizer pickle file at: {vectorizer_path}")
                return

            # 3. Load pickles
            try:
                logger.info(f"MLService: Loading model pickle from: {model_path}")
                cls._model = joblib.load(model_path)
                logger.info("MLService: Model pickle loaded successfully.")

                logger.info(f"MLService: Loading vectorizer pickle from: {vectorizer_path}")
                cls._vectorizer = joblib.load(vectorizer_path)
                logger.info("MLService: Vectorizer pickle loaded successfully.")
            except Exception as e:
                logger.error(f"MLService: Fatal pickle load exception: {e}", exc_info=True)

    @classmethod
    def health(cls) -> Dict[str, Any]:
        """
        Returns load state and descriptor metadata of the machine learning model.
        """
        cls._load_models()
        return {
            "loaded": (cls._model is not None and cls._vectorizer is not None),
            "model_name": cls.model_name,
            "model_version": cls.model_version,
            "vectorizer_loaded": (cls._vectorizer is not None),
            "model_loaded": (cls._model is not None)
        }

    @classmethod
    def predict(cls, text: str) -> Tuple[int, float]:
        """
        Predicts scam probability and binary label classification for a job description.

        Args:
            text: Raw job listing details string.

        Returns:
            prediction: int (1 for Scam, 0 for Safe)
            probability: float (0.0 to 1.0)
        """
        # 1. Input Validation
        if text is None:
            logger.warning("MLService: Predict received None input.")
            return 0, 0.0

        normalized_text = text.strip()
        if not normalized_text:
            logger.warning("MLService: Predict received empty or whitespace-only input.")
            return 0, 0.0

        # 2. Check Cache (redundant inference optimization)
        text_hash = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
        with cls._cache_lock:
            if text_hash in cls._cache:
                logger.debug("MLService: Cache hit for prediction.")
                return cls._cache[text_hash]

        # 3. Lazy Load Check
        cls._load_models()

        if cls._vectorizer is None or cls._model is None:
            logger.error("MLService: Inference requested but models are not loaded.")
            return 0, 0.0

        # 4. Predict
        try:
            features = cls._vectorizer.transform([normalized_text])
            prob_arr = cls._model.predict_proba(features)
            prob_scam = float(prob_arr[0][1])

            # Apply threshold to derive binary prediction
            prediction = 1 if prob_scam >= settings.ML_THRESHOLD else 0

            # 5. Populate Cache
            with cls._cache_lock:
                if len(cls._cache) >= cls._cache_limit:
                    cls._cache.clear()  # Safe simple eviction strategy
                cls._cache[text_hash] = (prediction, prob_scam)

            return prediction, prob_scam
        except Exception as e:
            logger.error(f"MLService: Inference prediction failure occurred: {e}", exc_info=True)
            return 0, 0.0
