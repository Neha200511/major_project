"""
ML Training Script for Child Safety Classifier.

Trains a Logistic Regression model on TF-IDF features.
Saves model artifacts and evaluation metrics.

Usage:
    python -m ml.train
"""

import os
import json
import pickle
import numpy as np
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

from ml.dataset import get_training_data, get_dataset_stats
from ml.preprocessing import clean_for_ml, augment_data

# Output directory
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')


def train():
    """Main training pipeline."""
    print("=" * 60)
    print("Child Safety ML Classifier - Training Pipeline")
    print("=" * 60)
    
    # Step 1: Load dataset
    print("\n[1/8] Loading dataset...")
    raw_data = get_training_data()
    stats = get_dataset_stats()
    print(f"  Total samples: {stats['total_samples']}")
    print(f"  Categories: {stats['num_labels']}")
    for label, count in sorted(stats['label_counts'].items(), key=lambda x: -x[1]):
        print(f"    {label}: {count}")
    
    # Step 2: Augment data for minority classes
    print("\n[2/8] Augmenting data for balance...")
    label_counts = Counter(label for _, label in raw_data)
    max_count = max(label_counts.values())
    
    # Augment minority classes
    augmented_data = []
    for label in label_counts:
        class_samples = [(text, lbl) for text, lbl in raw_data if lbl == label]
        if label_counts[label] < max_count * 0.6:
            # Augment this class
            factor = max(1, int((max_count * 0.7 - label_counts[label]) / label_counts[label]))
            aug = augment_data(class_samples, augment_factor=min(factor, 3))
            augmented_data.extend(aug)
        else:
            augmented_data.extend(class_samples)
    
    print(f"  After augmentation: {len(augmented_data)} samples")
    aug_counts = Counter(label for _, label in augmented_data)
    for label, count in sorted(aug_counts.items(), key=lambda x: -x[1]):
        print(f"    {label}: {count}")
    
    # Step 3: Preprocess
    print("\n[3/8] Preprocessing texts...")
    texts = [clean_for_ml(text) for text, _ in augmented_data]
    labels = [label for _, label in augmented_data]
    print(f"  Processed {len(texts)} texts")
    
    # Step 4: Split train/test
    print("\n[4/8] Splitting train/test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    print(f"  Train: {len(X_train)} samples")
    print(f"  Test:  {len(X_test)} samples")
    
    # Step 5: Vectorize
    print("\n[5/8] Creating TF-IDF features...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 3),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    print(f"  Feature matrix: {X_train_vec.shape}")
    
    # Step 6: Encode labels
    print("\n[6/8] Encoding labels...")
    label_encoder = LabelEncoder()
    y_train_enc = label_encoder.fit_transform(y_train)
    y_test_enc = label_encoder.transform(y_test)
    print(f"  Classes: {list(label_encoder.classes_)}")
    
    # Step 7: Train model
    print("\n[7/8] Training Logistic Regression...")
    model = LogisticRegression(
        class_weight='balanced',
        max_iter=1000,
        C=1.0,
        solver='lbfgs',
        random_state=42,
    )
    model.fit(X_train_vec, y_train_enc)
    print("  Model trained successfully!")
    
    # Step 8: Evaluate
    print("\n[8/8] Evaluating model...")
    y_pred = model.predict(X_test_vec)
    y_pred_labels = label_encoder.inverse_transform(y_pred)
    y_test_labels = label_encoder.inverse_transform(y_test_enc)
    
    accuracy = accuracy_score(y_test_enc, y_pred)
    precision = precision_score(y_test_enc, y_pred, average='macro', zero_division=0)
    recall = recall_score(y_test_enc, y_pred, average='macro', zero_division=0)
    f1 = f1_score(y_test_enc, y_pred, average='macro', zero_division=0)
    
    print(f"\n{'=' * 60}")
    print("EVALUATION RESULTS")
    print(f"{'=' * 60}")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f} (macro)")
    print(f"  Recall:    {recall:.4f} (macro)")
    print(f"  F1 Score:  {f1:.4f} (macro)")
    
    print(f"\n{'=' * 60}")
    print("CLASSIFICATION REPORT")
    print(f"{'=' * 60}")
    print(classification_report(y_test_labels, y_pred_labels, zero_division=0))
    
    print(f"\n{'=' * 60}")
    print("CONFUSION MATRIX")
    print(f"{'=' * 60}")
    cm = confusion_matrix(y_test_enc, y_pred)
    classes = label_encoder.classes_
    
    # Print header
    header = '          ' + '  '.join(f'{c[:6]:>6}' for c in classes)
    print(header)
    for i, row in enumerate(cm):
        row_str = f'{classes[i][:8]:>8}  ' + '  '.join(f'{val:>6}' for val in row)
        print(row_str)
    
    # Save model artifacts
    print(f"\n{'=' * 60}")
    print("SAVING MODEL ARTIFACTS")
    print(f"{'=' * 60}")
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    model_path = os.path.join(MODEL_DIR, 'model.pkl')
    vectorizer_path = os.path.join(MODEL_DIR, 'vectorizer.pkl')
    encoder_path = os.path.join(MODEL_DIR, 'label_encoder.pkl')
    metrics_path = os.path.join(MODEL_DIR, 'metrics.json')
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"  Model saved to: {model_path}")
    
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"  Vectorizer saved to: {vectorizer_path}")
    
    with open(encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    print(f"  Label encoder saved to: {encoder_path}")
    
    # Save metrics
    per_class_report = classification_report(y_test_labels, y_pred_labels, output_dict=True, zero_division=0)
    
    metrics = {
        'accuracy': round(accuracy, 4),
        'precision_macro': round(precision, 4),
        'recall_macro': round(recall, 4),
        'f1_macro': round(f1, 4),
        'per_class': {},
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'feature_count': X_train_vec.shape[1],
        'classes': list(classes),
    }
    
    for cls in classes:
        if cls in per_class_report:
            metrics['per_class'][cls] = {
                'precision': round(per_class_report[cls].get('precision', 0), 4),
                'recall': round(per_class_report[cls].get('recall', 0), 4),
                'f1': round(per_class_report[cls].get('f1-score', 0), 4),
                'support': int(per_class_report[cls].get('support', 0)),
            }
    
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"  Metrics saved to: {metrics_path}")
    
    print(f"\n{'=' * 60}")
    print("Training complete! Model artifacts saved to ml/model/")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    train()
