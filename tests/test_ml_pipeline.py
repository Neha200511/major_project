"""
Unit and integration tests for ML Pipeline, FeatureUnion, and Inference Engine.
"""

import os
import time
import pytest
from backend.monitoring.ml_model import MLClassifier
from ml.predict import predict, load_model


class TestMLPipeline:
    """Test suite for the ML classification pipeline."""

    @pytest.fixture(scope="class")
    def classifier(self):
        """Fixture that loads the classifier once for the test class."""
        clf = MLClassifier()
        assert clf.is_loaded is True, "Trained ML model artifacts must be present in ml/model/"
        return clf

    def test_model_loading_and_classes(self, classifier):
        """Verify model loads correctly and has all 8 safety classes."""
        expected_classes = {'BULLYING', 'GROOMING', 'MANIPULATION', 'PRIVACY_RISK', 'SAFE', 'SCAM', 'SELF_HARM', 'THREAT'}
        actual_classes = set(classifier.label_encoder.classes_)
        assert expected_classes.issubset(actual_classes), f"Missing classes in model: {expected_classes - actual_classes}"

    def test_feature_extraction_word_and_char(self, classifier):
        """Verify FeatureUnion produces both word and character n-gram features."""
        if classifier.pipeline is not None:
            features = classifier.pipeline.named_steps['features']
            transformer_list = dict(features.transformer_list)
            assert 'word_tfidf' in transformer_list, "Word TF-IDF must be in FeatureUnion"
            assert 'char_tfidf' in transformer_list, "Char TF-IDF must be in FeatureUnion"
            
            # Verify feature dimension on sample text
            vec = features.transform(["sample text for verification"])
            assert vec.shape[1] > 1000, "Combined feature space should contain thousands of features"

    def test_prediction_output_structure(self, classifier):
        """Verify inference returns all required fields."""
        res = classifier.predict("Are you coming to school tomorrow?")
        required_keys = {'score', 'category', 'confidence', 'probabilities', 'is_uncertain', 'confidence_margin', 'cleaned_text'}
        assert required_keys.issubset(res.keys()), f"Missing keys in predict output: {required_keys - res.keys()}"
        assert isinstance(res['score'], int)
        assert 0 <= res['score'] <= 100
        assert 0.0 <= res['confidence'] <= 1.0
        assert isinstance(res['probabilities'], dict)
        assert isinstance(res['is_uncertain'], bool)
        assert isinstance(res['confidence_margin'], float)

    def test_probabilities_sum_to_one(self, classifier):
        """Verify class probabilities approximate 1.0."""
        res = classifier.predict("How was your homework?")
        total_prob = sum(res['probabilities'].values())
        assert abs(total_prob - 1.0) < 0.05, f"Probabilities do not sum to 1: {total_prob}"

    def test_inference_latency(self, classifier):
        """Benchmark inference latency and verify it is lightweight for real-time chat (< 15ms)."""
        samples = [
            "How was your day at school?",
            "I'll destroy you in Fortnite lol 😂",
            "I will hurt you after school",
            "Send me your address right now",
            "This movie is amazing!",
        ]
        
        # Warmup
        for s in samples:
            classifier.predict(s)
            
        start = time.perf_counter()
        iterations = 50
        for _ in range(iterations):
            for s in samples:
                classifier.predict(s)
        total_time = time.perf_counter() - start
        
        avg_latency_ms = (total_time / (iterations * len(samples))) * 1000.0
        print(f"\n[LATENCY BENCHMARK] Average inference latency: {avg_latency_ms:.3f} ms / message")
        assert avg_latency_ms < 15.0, f"Inference latency too slow: {avg_latency_ms:.2f} ms"

    def test_missing_model_fallback(self):
        """Verify graceful fallback when model files are not found."""
        mock_clf = MLClassifier.__new__(MLClassifier)
        mock_clf.is_loaded = False
        mock_clf.pipeline = None
        mock_clf.model = None
        mock_clf.vectorizer = None
        mock_clf.label_encoder = None
        mock_clf.metrics = {}
        
        res = mock_clf.predict("Any message")
        assert res['category'] == 'SAFE'
        assert res['score'] <= 10
        assert res['is_uncertain'] is True

    def test_predict_utility_module(self):
        """Verify standalone ml.predict function works identically."""
        res = predict("Hello how are you?")
        assert 'category' in res
        assert 'confidence' in res
        assert 'probabilities' in res
