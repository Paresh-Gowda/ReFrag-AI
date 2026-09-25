#!/usr/bin/env python3
"""
ReFrag AI - Forensic Model Evaluator & Inspection Utility
Loads serialized models from ml/saved/, computes in-depth classification
metrics, confusion matrices, and tests inference against individual
fragments or holdout datasets.
"""

from __future__ import annotations

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    import numpy as np
    import pandas as pd
    import joblib
    from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, balanced_accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def check_dependencies():
    if not SKLEARN_AVAILABLE:
        print("[!] Missing required libraries (numpy, pandas, scikit-learn, joblib).")
        sys.exit(1)


def print_confusion_matrix(cm: list[list[int]], classes: list[str]):
    """Pretty prints a text-based confusion matrix."""
    header = "True \\ Pred".ljust(14) + "".join([c[:7].rjust(8) for c in classes])
    print(header)
    print("-" * len(header))
    for idx, row in enumerate(cm):
        row_str = classes[idx][:12].ljust(14) + "".join([str(val).rjust(8) for val in row])
        print(row_str)


def evaluate_dataset(
    features_csv: Path,
    model_dir: Path,
):
    """Evaluates the saved model against a features dataset."""
    check_dependencies()
    model_path = model_dir / "fragment_classifier.joblib"
    encoder_path = model_dir / "label_encoder.joblib"
    meta_path = model_dir / "model_metadata.json"

    if not model_path.exists() or not encoder_path.exists():
        print(f"[!] Saved model artifacts not found in {model_dir}")
        print("    Please run 'ml/training/train_classifier.py' first.")
        sys.exit(1)

    print(f"[*] Loading trained model from {model_path}...")
    pipeline = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    df = pd.read_csv(features_csv)
    feature_cols = meta["features"]
    missing_cols = [c for c in feature_cols if c not in df.columns]
    if missing_cols:
        print(f"[!] Warning: Dataset is missing {len(missing_cols)} expected feature columns.")

    X = df[[c for c in feature_cols if c in df.columns]].fillna(0.0)
    y_true_labels = df["file_type"]

    classes = list(label_encoder.classes_)
    y_true = label_encoder.transform(y_true_labels)

    # Predictions
    y_pred = pipeline.predict(X)
    probabilities = pipeline.predict_proba(X)
    max_probs = np.max(probabilities, axis=1)

    accuracy = accuracy_score(y_true, y_pred)
    balanced_acc = balanced_accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred).tolist()

    print("\n" + "=" * 60)
    print("           REFRAG AI - MODEL EVALUATION REPORT")
    print("=" * 60)
    print(f"Total Fragments Evaluated: {len(X)}")
    print(f"Overall Accuracy:          {accuracy * 100:.2f}%")
    print(f"Balanced Accuracy:         {balanced_acc * 100:.2f}%")
    print(f"Mean Confidence Score:     {np.mean(max_probs) * 100:.2f}%")
    print(f"Median Confidence Score:   {np.median(max_probs) * 100:.2f}%")
    print("\nPer-Class Classification Report:")
    print(classification_report(y_true, y_pred, target_names=classes, zero_division=0))

    print("\nConfusion Matrix:")
    print_confusion_matrix(cm, classes)
    print("=" * 60 + "\n")


def evaluate_single_fragment(fragment_path: Path, model_dir: Path):
    """Evaluates an individual raw fragment binary."""
    check_dependencies()
    from features.extract_features import extract_features_from_bytes

    model_path = model_dir / "fragment_classifier.joblib"
    encoder_path = model_dir / "label_encoder.joblib"
    meta_path = model_dir / "model_metadata.json"

    if not model_path.exists():
        print(f"[!] Model not found at {model_path}")
        sys.exit(1)

    pipeline = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    raw_bytes = fragment_path.read_bytes()
    features = extract_features_from_bytes(raw_bytes)
    feature_vector = [features.get(col, 0.0) for col in meta["features"]]
    X_input = pd.DataFrame(
        [feature_vector],
        columns=meta["features"]
    )

    pred_idx = pipeline.predict(X_input)[0]
    probs = pipeline.predict_proba(X_input)[0]
    pred_label = label_encoder.inverse_transform([pred_idx])[0]
    confidence = probs[pred_idx]

    print("\n" + "-" * 50)
    print(f"Fragment: {fragment_path.name}")
    print(f"Size:     {len(raw_bytes)} bytes")
    print(f"Entropy:  {features.get('entropy', 0.0):.2f} / 8.00")
    print(f"Predicted Type: {pred_label.upper()}")
    print(f"Confidence:     {confidence * 100:.2f}%")
    print("\nClass Probabilities:")
    for cls_name, p in sorted(zip(label_encoder.classes_, probs), key=lambda x: x[1], reverse=True):
        bar = "#" * int(p * 25)
        print(f"  {cls_name:10s} : {p * 100:5.1f}% | {bar}")
    print("-" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="ReFrag AI - Forensic Model Evaluator"
    )
    parser.add_argument(
        "--features-csv",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "features" / "extracted_features.csv"),
        help="Path to features dataset CSV",
    )
    parser.add_argument(
        "--model-dir",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "saved"),
        help="Directory with saved models (default: ml/saved)",
    )
    parser.add_argument(
        "--fragment",
        type=str,
        default=None,
        help="Path to an individual raw .bin fragment to classify",
    )

    args = parser.parse_args()
    model_dir = Path(args.model_dir)

    if args.fragment:
        evaluate_single_fragment(Path(args.fragment), model_dir)
    else:
        evaluate_dataset(Path(args.features_csv), model_dir)


if __name__ == "__main__":
    main()
