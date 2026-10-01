"""
Layer 2: ML Classification for Child Safety Monitoring.

Loads a pre-trained sklearn model to classify messages into
risk categories (SAFE, BULLYING, THREAT, GROOMING, etc.).
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
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.is_loaded = False
        self.metrics: Dict = {}
        self._load_model()

    def _load_model(self):
        """Try to load saved model artifacts from ml/model/ directory."""
        model_path = os.path.join(MODEL_DIR, 'model.pkl')
        vectorizer_path = os.path.join(MODEL_DIR, 'vectorizer.pkl')
        encoder_path = os.path.join(MODEL_DIR, 'label_encoder.pkl')
        metrics_path = os.path.join(MODEL_DIR, 'metrics.json')

        try:
            if not all(os.path.exists(p) for p in [model_path, vectorizer_path, encoder_path]):
                logger.warning("ML model files not found at %s. Classifier will return default predictions.", MODEL_DIR)
                return

            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open(encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)

            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    self.metrics = json.load(f)

            self.is_loaded = True
            logger.info("ML model loaded successfully from %s", MODEL_DIR)
        except Exception as e:
            logger.error("Failed to load ML model: %s", str(e))
            self.is_loaded = False

    def predict(self, text: str) -> Dict:
        """
        Predict risk category for given text.

        Returns:
            dict with score (0-100), category, confidence (0-1), probabilities
        """
        default_response = {
            'score': 5,
            'category': 'SAFE',
            'confidence': 0.3,
            'probabilities': {'SAFE': 0.7},
        }

        if not self.is_loaded or not text or not text.strip():
            return default_response

        try:
            # Vectorize the text
            text_vector = self.vectorizer.transform([text.lower().strip()])

            # Get prediction and probabilities
            prediction = self.model.predict(text_vector)[0]
            probabilities = self.model.predict_proba(text_vector)[0]

            # Decode label
            category = str(self.label_encoder.inverse_transform([prediction])[0])
            classes = self.label_encoder.classes_

            # Build probability dict
            prob_dict = {}
            for cls, prob in zip(classes, probabilities):
                prob_dict[str(cls)] = round(float(prob), 4)

            # Confidence is the max probability
            confidence = float(max(probabilities))

            # Calculate score based on prediction and confidence
            score = self._calculate_score(category, confidence, prob_dict)

            return {
                'score': score,
                'category': category,
                'confidence': round(confidence, 3),
                'probabilities': prob_dict,
            }
        except Exception as e:
            logger.error("ML prediction failed: %s", str(e))
            return default_response

    def _calculate_score(self, category: str, confidence: float, probabilities: dict) -> int:
        """
        Map prediction to a risk score (0-100).

        Score mapping:
        - SAFE prediction with high confidence (>0.7) -> 0-10
        - SAFE prediction with low confidence (<0.7) -> 10-25
        - Risky prediction with low confidence (<0.6) -> 25-50
        - Risky prediction with high confidence (>0.6) -> 50-90
        """
        is_safe = (category == 'SAFE')

        if is_safe:
            if confidence > 0.7:
                # High confidence safe: 0-10
                score = int((1.0 - confidence) * 33)  # 0.7->10, 1.0->0
                return max(0, min(10, score))
            else:
                # Low confidence safe: 10-25
                score = int(10 + (0.7 - confidence) * 42)  # 0.7->10, 0.35->25
                return max(10, min(25, score))
        else:
            # Risky category
            # Also consider how far the risky probability is from SAFE
            safe_prob = probabilities.get('SAFE', 0.0)
            risk_margin = confidence - safe_prob  # How much more confident in risk vs safe

            if confidence < 0.6:
                # Low confidence risky: 25-50
                score = int(25 + confidence * 42)  # 0.0->25, 0.6->50
                return max(25, min(50, score))
            else:
                # High confidence risky: 50-90
                score = int(50 + (confidence - 0.6) * 100)  # 0.6->50, 1.0->90
                # Boost for high-danger categories
                if category in ('GROOMING', 'SELF_HARM', 'THREAT'):
                    score = min(90, score + 5)
                return max(50, min(90, score))

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
            'note': 'No metrics available. Run ml.train to generate metrics.',
        }
