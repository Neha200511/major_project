"""
Layer 2: ML Classification for Child Safety Monitoring.

Loads a pre-trained Scikit-learn Pipeline (Word+Char FeatureUnion + Logistic Regression)
to classify messages into risk categories with calibrated confidence and uncertainty handling.
"""

import os
import json
import pickle
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Path to saved model artifacts
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ml', 'model')


class MLClassifier:
    """ML-based text classifier for child safety risk detection."""

    RISK_CATEGORIES = {'BULLYING', 'THREAT', 'GROOMING', 'SELF_HARM', 'PRIVACY_RISK', 'MANIPULATION', 'SCAM'}

    def __init__(self):
        self.pipeline = None
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.is_loaded = False
        self.metrics: Dict = {}
        self._load_model()

    def _load_model(self):
        """
        Load model artifacts from ml/model/ directory.
        Prefers unified pipeline.pkl, falls back to separate model.pkl + vectorizer.pkl.
        """
        pipeline_path = os.path.join(MODEL_DIR, 'pipeline.pkl')
        model_path = os.path.join(MODEL_DIR, 'model.pkl')
        vectorizer_path = os.path.join(MODEL_DIR, 'vectorizer.pkl')
        encoder_path = os.path.join(MODEL_DIR, 'label_encoder.pkl')
        metrics_path = os.path.join(MODEL_DIR, 'metrics.json')

        try:
            # 1. Try unified Pipeline first
            if os.path.exists(pipeline_path) and os.path.exists(encoder_path):
                with open(pipeline_path, 'rb') as f:
                    self.pipeline = pickle.load(f)
                with open(encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                self.is_loaded = True
                logger.info("Loaded complete ML Pipeline from %s", pipeline_path)
            # 2. Backward compatibility fallback: separate model + vectorizer
            elif os.path.exists(model_path) and os.path.exists(vectorizer_path) and os.path.exists(encoder_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                with open(encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                self.is_loaded = True
                logger.info("Loaded separate ML model + vectorizer from %s", MODEL_DIR)
            else:
                logger.warning("ML model files not found at %s. Classifier will return default predictions.", MODEL_DIR)
                self.is_loaded = False
                return

            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    self.metrics = json.load(f)

        except Exception as e:
            logger.error("Failed to load ML model: %s", str(e))
            self.is_loaded = False

    def predict(self, text: str) -> Dict:
        """
        Predict risk category for given text using standardized preprocessing.

        Returns:
            dict with score (0-100), category, confidence (0-1), probabilities,
            is_uncertain (bool), confidence_margin (float)
        """
        default_response = {
            'score': 5,
            'category': 'SAFE',
            'confidence': 0.3,
            'probabilities': {'SAFE': 0.7},
            'is_uncertain': True,
            'confidence_margin': 0.0,
            'cleaned_text': '',
        }

        if not self.is_loaded or not text or not str(text).strip():
            return default_response

        try:
            # Apply identical preprocessing used during training
            try:
                from ml.preprocessing import normalize_text
                cleaned = normalize_text(text)
            except ImportError:
                cleaned = str(text).lower().strip()

            if not cleaned:
                return default_response

            # Inference using pipeline or separate components
            if self.pipeline is not None:
                probabilities = self.pipeline.predict_proba([cleaned])[0]
                prediction = self.pipeline.predict([cleaned])[0]
            elif self.model is not None and self.vectorizer is not None:
                text_vector = self.vectorizer.transform([cleaned])
                probabilities = self.model.predict_proba(text_vector)[0]
                prediction = self.model.predict(text_vector)[0]
            else:
                return default_response

            # Decode label
            category = str(self.label_encoder.inverse_transform([prediction])[0])
            classes = self.label_encoder.classes_

            # Build probability dict sorted by score
            prob_dict = {}
            for cls, prob in zip(classes, probabilities):
                prob_dict[str(cls)] = round(float(prob), 4)

            # Sort probabilities descending
            sorted_probs = sorted(probabilities, reverse=True)
            confidence = float(sorted_probs[0])
            second_confidence = float(sorted_probs[1]) if len(sorted_probs) > 1 else 0.0
            margin = confidence - second_confidence

            # Uncertainty flag: low max confidence OR narrow gap between top 2 classes
            is_uncertain = (confidence < 0.40) or (category != 'SAFE' and margin < 0.12)

            # Calculate risk score (0-100) based on prediction, confidence, and margin
            score = self._calculate_score(category, confidence, prob_dict, is_uncertain, margin)

            return {
                'score': score,
                'category': category,
                'confidence': round(confidence, 4),
                'probabilities': prob_dict,
                'is_uncertain': is_uncertain,
                'confidence_margin': round(margin, 4),
                'cleaned_text': cleaned,
            }
        except Exception as e:
            logger.error("ML prediction failed: %s", str(e))
            return default_response

    def _calculate_score(self, category: str, confidence: float, probabilities: dict,
                         is_uncertain: bool = False, margin: float = 0.0) -> int:
        """
        Map prediction to a calibrated risk score (0-100).

        Calibration logic:
        - SAFE prediction with high confidence (>0.7) -> 0-10
        - SAFE prediction with moderate confidence -> 10-25
        - Risky prediction with low confidence or high uncertainty -> 20-40 (gives context/rules space to decide)
        - Risky prediction with moderate confidence (0.5 - 0.7) -> 45-65
        - Risky prediction with high confidence (>0.7) -> 65-90
        - Category-specific adjustments for physical harm (THREAT, SELF_HARM, GROOMING)
        """
        is_safe = (category == 'SAFE')

        if is_safe:
            if confidence > 0.70:
                # High confidence safe: 0-10
                score = int((1.0 - confidence) * 33)
                return max(0, min(10, score))
            else:
                # Moderate confidence safe: 10-25
                score = int(10 + (0.70 - confidence) * 40)
                return max(10, min(25, score))
        else:
            # Non-safe category
            if is_uncertain:
                # Narrow margin or low confidence: don't overreact, return 25-45
                base = 25 + int(confidence * 30)
                return max(20, min(45, base))

            if confidence < 0.55:
                # Low-moderate confidence: 35-55
                score = int(35 + (confidence - 0.35) * 100)
                return max(35, min(55, score))
            elif confidence < 0.75:
                # Moderate-high confidence: 55-75
                score = int(55 + (confidence - 0.55) * 100)
                if category in ('GROOMING', 'SELF_HARM', 'THREAT'):
                    score = min(80, score + 5)
                return max(55, min(75, score))
            else:
                # High confidence risky: 75-90
                score = int(75 + (confidence - 0.75) * 60)
                if category in ('GROOMING', 'SELF_HARM', 'THREAT'):
                    score = min(92, score + 5)
                return max(75, min(92, score))

    def get_metrics(self) -> Dict:
        """Return stored model metrics (accuracy, precision, recall, f1)."""
        if self.metrics:
            return self.metrics
        return {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1': 0.0,
            'loaded': self.is_loaded,
            'note': 'No metrics available. Run python -m ml.train to generate metrics.',
        }
