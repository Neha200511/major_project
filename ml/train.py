"""
ML Training Script for Child Safety Classifier.

Trains a unified Scikit-learn Pipeline with word-level and character-level
TF-IDF FeatureUnion and Logistic Regression.
Saves model artifacts and evaluation metrics with full backward compatibility.

Usage:
    python -m ml.train
"""

import os
import json
import time
import pickle
import numpy as np
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
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
from ml.preprocessing import normalize_text, augment_data

# Output directory
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')


def train():
    """Main training pipeline."""
    print("=" * 60)
    print("Child Safety ML Classifier - Training Pipeline")
    print("Feature Extraction: Word TF-IDF + Character TF-IDF (FeatureUnion)")
    print("=" * 60)
    
    # Step 1: Load dataset
    print("\n[1/8] Loading dataset...")
    raw_data = get_training_data()
    stats = get_dataset_stats()
    print(f"  Total raw samples: {stats['total_samples']}")
    print(f"  Categories: {stats['num_labels']}")
    for label, count in sorted(stats['label_counts'].items(), key=lambda x: -x[1]):
        print(f"    {label}: {count}")
    
    raw_texts = [text for text, _ in raw_data]
    raw_labels = [label for _, label in raw_data]

    # Step 2: Split train/test BEFORE augmentation to prevent data leakage
    print("\n[2/8] Splitting train/test (80/20, stratified, leakage-free)...")
    X_train_raw, X_test_raw, y_train_raw, y_test = train_test_split(
        raw_texts, raw_labels, test_size=0.20, random_state=42, stratify=raw_labels
    )
    print(f"  Raw Train: {len(X_train_raw)} samples")
    print(f"  Held-out Test: {len(X_test_raw)} samples")

    # Step 3: Normalize texts consistently using normalize_text
    print("\n[3/8] Normalizing text (consistent across training & inference)...")
    X_train_clean = [normalize_text(text) for text in X_train_raw]
    X_test_clean = [normalize_text(text) for text in X_test_raw]
    print(f"  Normalized {len(X_train_clean)} train and {len(X_test_clean)} test texts")

    # Step 4: Augment ONLY the training split for minority classes
    print("\n[4/8] Augmenting training set for class balance (no test leakage)...")
    train_samples = list(zip(X_train_clean, y_train_raw))
    label_counts = Counter(y_train_raw)
    max_count = max(label_counts.values())
    
    augmented_train_samples = []
    for label, count in label_counts.items():
        class_samples = [(t, l) for t, l in train_samples if l == label]
        if count < max_count * 0.65:
            factor = max(1, int((max_count * 0.75 - count) / count))
            aug = augment_data(class_samples, augment_factor=min(factor, 3))
            augmented_train_samples.extend(aug)
        else:
            augmented_train_samples.extend(class_samples)

    X_train = [text for text, _ in augmented_train_samples]
    y_train = [label for _, label in augmented_train_samples]
    
    print(f"  Train samples after augmentation: {len(X_train)}")
    aug_counts = Counter(y_train)
    for label, count in sorted(aug_counts.items(), key=lambda x: -x[1]):
        print(f"    {label}: {count}")

    # Step 5: Encode labels
    print("\n[5/8] Encoding labels...")
    label_encoder = LabelEncoder()
    y_train_enc = label_encoder.fit_transform(y_train)
    y_test_enc = label_encoder.transform(y_test)
    classes = list(label_encoder.classes_)
    print(f"  Classes ({len(classes)}): {classes}")

    # Step 6: Construct Feature Union (Word TF-IDF + Char TF-IDF) and Pipeline
    print("\n[6/8] Building FeatureUnion (Word + Char n-grams) & Pipeline...")
    word_vectorizer = TfidfVectorizer(
        analyzer='word',
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,
    )
    
    char_vectorizer = TfidfVectorizer(
        analyzer='char',
        ngram_range=(3, 5),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
    )
    
    feature_union = FeatureUnion([
        ('word_tfidf', word_vectorizer),
        ('char_tfidf', char_vectorizer),
    ])

    classifier = LogisticRegression(
        class_weight='balanced',
        max_iter=1000,
        C=1.2,
        solver='lbfgs',
        random_state=42,
    )

    pipeline = Pipeline([
        ('features', feature_union),
        ('classifier', classifier),
    ])

    # Step 7: Train model pipeline
    print("\n[7/8] Fitting Pipeline on training data...")
    t0 = time.perf_counter()
    pipeline.fit(X_train, y_train_enc)
    fit_duration = time.perf_counter() - t0
    print(f"  Pipeline fitted in {fit_duration:.2f}s")
    
    # Inspect feature count
    transformed_sample = pipeline.named_steps['features'].transform(X_train[:1])
    total_features = transformed_sample.shape[1]
    print(f"  Total extracted features: {total_features}")

    # Step 8: Evaluate on pristine held-out test set
    print("\n[8/8] Evaluating model on held-out test set...")
    t_inf_start = time.perf_counter()
    y_pred = pipeline.predict(X_test_clean)
    y_pred_proba = pipeline.predict_proba(X_test_clean)
    inf_duration = time.perf_counter() - t_inf_start
    latency_ms_per_sample = (inf_duration / len(X_test_clean)) * 1000.0

    y_pred_labels = label_encoder.inverse_transform(y_pred)
    y_test_labels = label_encoder.inverse_transform(y_test_enc)

    accuracy = accuracy_score(y_test_enc, y_pred)
    precision_macro = precision_score(y_test_enc, y_pred, average='macro', zero_division=0)
    recall_macro = recall_score(y_test_enc, y_pred, average='macro', zero_division=0)
    f1_macro = f1_score(y_test_enc, y_pred, average='macro', zero_division=0)

    # Compute False Positives (Safe predicted as Risky) and False Negatives (Risky predicted as Safe)
    safe_idx = classes.index('SAFE') if 'SAFE' in classes else -1
    fp_count = 0
    fn_count = 0
    for true_lbl, pred_lbl in zip(y_test_labels, y_pred_labels):
        if true_lbl == 'SAFE' and pred_lbl != 'SAFE':
            fp_count += 1
        elif true_lbl != 'SAFE' and pred_lbl == 'SAFE':
            fn_count += 1

    print(f"\n{'=' * 60}")
    print("EVALUATION RESULTS")
    print(f"{'=' * 60}")
    print(f"  Accuracy:                 {accuracy:.4f}")
    print(f"  Precision (macro):        {precision_macro:.4f}")
    print(f"  Recall (macro):           {recall_macro:.4f}")
    print(f"  F1 Score (macro):         {f1_macro:.4f}")
    print(f"  False Positives (Safe->Risk): {fp_count}")
    print(f"  False Negatives (Risk->Safe): {fn_count}")
    print(f"  Avg Inference Latency:    {latency_ms_per_sample:.3f} ms / sample")

    print(f"\n{'=' * 60}")
    print("CLASSIFICATION REPORT")
    print(f"{'=' * 60}")
    print(classification_report(y_test_labels, y_pred_labels, zero_division=0))

    print(f"\n{'=' * 60}")
    print("CONFUSION MATRIX")
    print(f"{'=' * 60}")
    cm = confusion_matrix(y_test_enc, y_pred)
    header = '          ' + '  '.join(f'{c[:6]:>6}' for c in classes)
    print(header)
    for i, row in enumerate(cm):
        row_str = f'{classes[i][:8]:>8}  ' + '  '.join(f'{val:>6}' for val in row)
        print(row_str)

    # Step 9: Save model artifacts
    print(f"\n{'=' * 60}")
    print("SAVING MODEL ARTIFACTS")
    print(f"{'=' * 60}")
    os.makedirs(MODEL_DIR, exist_ok=True)

    # 1. Complete unified pipeline
    pipeline_path = os.path.join(MODEL_DIR, 'pipeline.pkl')
    with open(pipeline_path, 'wb') as f:
        pickle.dump(pipeline, f)
    print(f"  Complete Pipeline saved to: {pipeline_path}")

    # 2. Backward-compatible individual artifacts (classifier & feature_union)
    model_path = os.path.join(MODEL_DIR, 'model.pkl')
    vectorizer_path = os.path.join(MODEL_DIR, 'vectorizer.pkl')
    encoder_path = os.path.join(MODEL_DIR, 'label_encoder.pkl')
    metrics_path = os.path.join(MODEL_DIR, 'metrics.json')

    with open(model_path, 'wb') as f:
        pickle.dump(pipeline.named_steps['classifier'], f)
    print(f"  Classifier (backward-compat) saved to: {model_path}")

    with open(vectorizer_path, 'wb') as f:
        pickle.dump(pipeline.named_steps['features'], f)
    print(f"  FeatureUnion (backward-compat) saved to: {vectorizer_path}")

    with open(encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    print(f"  Label encoder saved to: {encoder_path}")

    # Save metrics JSON
    per_class_report = classification_report(y_test_labels, y_pred_labels, output_dict=True, zero_division=0)
    metrics = {
        'model_version': '2.0.0-featureunion',
        'pipeline_architecture': 'FeatureUnion(Word_TFIDF(1,2) + Char_TFIDF(3,5)) -> LogisticRegression(balanced)',
        'accuracy': round(accuracy, 4),
        'precision_macro': round(precision_macro, 4),
        'recall_macro': round(recall_macro, 4),
        'f1_macro': round(f1_macro, 4),
        'false_positives': fp_count,
        'false_negatives': fn_count,
        'latency_ms_per_sample': round(latency_ms_per_sample, 3),
        'total_features': total_features,
        'training_samples': len(X_train),
        'test_samples': len(X_test_clean),
        'classes': classes,
        'per_class': {},
        'confusion_matrix': cm.tolist(),
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
    return metrics


if __name__ == '__main__':
    train()
