"""
Prediction Utility for Child Safety ML Classifier.

Loads the trained model and provides prediction capabilities.

Usage:
    python -m ml.predict
"""

import os
import json
import pickle
import sys
from typing import Dict, Optional

from ml.preprocessing import normalize_text, clean_for_ml

# Model directory
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')


def load_model():
    """
    Load saved model/pipeline, vectorizer, and label encoder.
    
    Returns:
        tuple: (model_or_pipeline, vectorizer, label_encoder) or (None, None, None) if not found
    """
    pipeline_path = os.path.join(MODEL_DIR, 'pipeline.pkl')
    model_path = os.path.join(MODEL_DIR, 'model.pkl')
    vectorizer_path = os.path.join(MODEL_DIR, 'vectorizer.pkl')
    encoder_path = os.path.join(MODEL_DIR, 'label_encoder.pkl')
    
    if os.path.exists(pipeline_path) and os.path.exists(encoder_path):
        with open(pipeline_path, 'rb') as f:
            pipeline = pickle.load(f)
        with open(encoder_path, 'rb') as f:
            label_encoder = pickle.load(f)
        return pipeline, None, label_encoder
        
    if not all(os.path.exists(p) for p in [model_path, vectorizer_path, encoder_path]):
        print(f"Error: Model files not found in {MODEL_DIR}")
        print("Run 'python -m ml.train' first to train the model.")
        return None, None, None
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    with open(encoder_path, 'rb') as f:
        label_encoder = pickle.load(f)
    
    return model, vectorizer, label_encoder


def predict(text: str, model=None, vectorizer=None, label_encoder=None) -> Dict:
    """
    Predict the risk category for a given text.
    
    Args:
        text: Input text to classify
        model: Pre-loaded model or pipeline
        vectorizer: Pre-loaded vectorizer (if separate)
        label_encoder: Pre-loaded encoder
    
    Returns:
        dict with category, confidence, probabilities
    """
    if model is None or label_encoder is None:
        model, vectorizer, label_encoder = load_model()
        if model is None:
            return {
                'category': 'UNKNOWN',
                'confidence': 0.0,
                'probabilities': {},
                'error': 'Model not loaded',
            }
    
    # Preprocess
    cleaned = normalize_text(text)
    
    if hasattr(model, 'predict_proba') and vectorizer is None:
        # Full Pipeline
        prediction = model.predict([cleaned])[0]
        probabilities = model.predict_proba([cleaned])[0]
    else:
        # Separate Vectorizer + Classifier
        text_vector = vectorizer.transform([cleaned])
        prediction = model.predict(text_vector)[0]
        probabilities = model.predict_proba(text_vector)[0]
    
    # Decode
    category = str(label_encoder.inverse_transform([prediction])[0])
    classes = label_encoder.classes_
    
    prob_dict = {}
    for cls, prob in zip(classes, probabilities):
        prob_dict[str(cls)] = round(float(prob), 4)
    
    confidence = float(max(probabilities))
    
    # Sort probabilities by value
    sorted_probs = dict(sorted(prob_dict.items(), key=lambda x: -x[1]))
    
    return {
        'category': category,
        'confidence': round(confidence, 4),
        'probabilities': sorted_probs,
    }


def interactive_mode():
    """Run interactive prediction mode."""
    print("=" * 60)
    print("Child Safety ML Classifier - Interactive Prediction")
    print("=" * 60)
    print("\nLoading model...")
    
    model, vectorizer, label_encoder = load_model()
    if model is None:
        return
    
    print("Model loaded successfully!")
    print("\nEnter text to classify (type 'quit' or 'exit' to stop):")
    print("-" * 60)
    
    while True:
        try:
            text = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not text:
            continue
        if text.lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break
        
        result = predict(text, model, vectorizer, label_encoder)
        
        category = result['category']
        confidence = result['confidence']
        
        # Color coding (ASCII)
        if category == 'SAFE':
            indicator = '✅'
        elif category in ('BULLYING', 'MANIPULATION', 'SCAM'):
            indicator = '⚠️'
        else:
            indicator = '🚨'
        
        print(f"\n{indicator} Category: {category}")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Top probabilities:")
        for cat, prob in list(result['probabilities'].items())[:3]:
            print(f"     - {cat}: {prob:.1%}")

if __name__ == '__main__':
    interactive_mode()
