#!/usr/bin/env python3
"""
ReFrag AI - Fragment File Type Classifier & Reconstructor Model Trainer
Trains a machine learning classifier on extracted byte-level forensic features
to identify the file type and category of isolated or damaged storage fragments.
Saves serialized models, encoders, and evaluation metrics to ml/saved/.
"""

from __future__ import annotations

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to sys.path to allow sibling imports
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
    from sklearn.pipeline import Pipeline
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def check_dependencies():
    """Verify that required ML libraries are installed."""
    if not SKLEARN_AVAILABLE:
        print("[!] Required machine learning libraries are missing.")
        print("    Please install them via:")
        print("    pip install numpy pandas scikit-learn joblib")
        sys.exit(1)


def load_dataset(features_csv: Path) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Loads features from CSV and splits into X (features) and y (target labels)."""
    if not features_csv.exists():
        raise FileNotFoundError(
            f"Feature dataset not found at {features_csv}.\n"
            "Run 'ml/features/extract_features.py' first to generate features."
        )

    df = pd.read_csv(features_csv)

    # Metadata columns to exclude from training features
    meta_cols = [
        "fragment_id",
        "source_file",
        "file_type",
        "fragment_index",
        "is_header",
        "is_footer",
    ]

    feature_cols = [c for c in df.columns if c not in meta_cols]
    X = df[feature_cols].copy()
    y = df["file_type"].copy()

    # Fill any potential NaN values
    X = X.fillna(0.0)

    return df, X, y, feature_cols


def train_classifier(
    features_csv: Path,
    output_dir: Path,
    test_size: float = 0.25,
    random_state: int = 42,
    model_type: str = "random_forest",
):
    """Trains a classifier and saves artifacts to output_dir."""
    check_dependencies()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Loading feature dataset from {features_csv}...")
    df, X, y, feature_cols = load_dataset(features_csv)

    print(f"  Samples: {len(X)}")
    print(f"  Features: {len(feature_cols)}")
    print(f"  Classes ({len(y.unique())}): {list(y.unique())}")

    # Encode target labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    classes = list(label_encoder.classes_)

    # Group-based split by source_file to prevent data leakage between train and test
    if "source_file" in df.columns and df["source_file"].nunique() > 1:
        unique_sources = df[["source_file", "file_type"]].drop_duplicates()
        type_counts = unique_sources["file_type"].value_counts()
        stratify_source = unique_sources["file_type"] if type_counts.min() >= 2 else None

        train_sources, test_sources = train_test_split(
            unique_sources["source_file"],
            test_size=test_size,
            random_state=random_state,
            stratify=stratify_source,
        )

        train_mask = df["source_file"].isin(train_sources)
        test_mask = df["source_file"].isin(test_sources)

        X_train, y_train = X[train_mask], y_encoded[train_mask]
        X_test, y_test = X[test_mask], y_encoded[test_mask]
        print(f"[*] Group Split: {len(train_sources)} train source files ({len(X_train)} frags), {len(test_sources)} test source files ({len(X_test)} frags). Zero fragment leakage!")
    else:
        stratify = y_encoded if min(np.bincount(y_encoded)) >= 2 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y_encoded,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify,
        )
        print(f"[*] Standard Split: {len(X_train)} train frags | {len(X_test)} test frags")

    # Initialize model
    if model_type == "gradient_boosting":
        print("[*] Initializing Gradient Boosting Classifier...")
        clf = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=random_state,
        )
    else:
        print("[*] Initializing Random Forest Classifier (Forensic Ensemble)...")
        clf = RandomForestClassifier(
            n_estimators=120,
            max_depth=16,
            min_samples_split=2,
            n_jobs=-1,
            random_state=random_state,
            class_weight="balanced",
        )

    # Direct classifier pipeline without StandardScaler for tree ensembles
    pipeline = Pipeline([
        ("classifier", clf),
    ])

    print("[*] Fitting model to forensic feature patterns...")
    pipeline.fit(X_train, y_train)

    # Evaluate model
    print("[*] Evaluating on holdout test set...")
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    report_dict = classification_report(
        y_test,
        y_pred,
        target_names=classes,
        output_dict=True,
        zero_division=0,
    )
    conf_matrix = confusion_matrix(y_test, y_pred).tolist()

    print(f"\n[+] Test Accuracy: {accuracy * 100:.2f}%\n")
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=classes, zero_division=0))

    # Feature Importance (if tree-based)
    feature_importances = {}
    if hasattr(clf, "feature_importances_"):
        top_indices = np.argsort(clf.feature_importances_)[::-1][:15]
        print("Top 15 Most Discriminative Forensic Features:")
        for rank, idx in enumerate(top_indices, 1):
            feat_name = feature_cols[idx]
            importance = float(clf.feature_importances_[idx])
            feature_importances[feat_name] = round(importance, 5)
            print(f"  {rank:2d}. {feat_name:20s}: {importance * 100:.2f}%")

    # Serialize artifacts
    model_save_path = output_dir / "fragment_classifier.joblib"
    encoder_save_path = output_dir / "label_encoder.joblib"
    metadata_save_path = output_dir / "model_metadata.json"

    joblib.dump(pipeline, model_save_path)
    joblib.dump(label_encoder, encoder_save_path)

    metrics_payload = {
        "model_type": model_type,
        "accuracy": round(accuracy, 4),
        "classes": classes,
        "features": feature_cols,
        "feature_importances_top15": feature_importances,
        "classification_report": report_dict,
        "confusion_matrix": conf_matrix,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
    }

    with open(metadata_save_path, "w", encoding="utf-8") as jf:
        json.dump(metrics_payload, jf, indent=2)

    print("\n[+] Training artifacts successfully saved!")
    print(f"  Model Pipeline:  {model_save_path}")
    print(f"  Label Encoder:   {encoder_save_path}")
    print(f"  Model Metadata:  {metadata_save_path}")


def predict_fragment(
    fragment_bytes: bytes,
    model_dir: Path,
) -> dict:
    """
    Given raw bytes of an unknown fragment, extracts features and
    returns predicted file type and probability confidence score.
    """
    from features.extract_features import extract_features_from_bytes

    model_path = model_dir / "fragment_classifier.joblib"
    encoder_path = model_dir / "label_encoder.joblib"
    meta_path = model_dir / "model_metadata.json"

    if not model_path.exists() or not encoder_path.exists():
        raise FileNotFoundError("Trained model artifacts not found in ml/saved/")

    pipeline = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Extract features matching the model's feature column expectations
    features_dict = extract_features_from_bytes(fragment_bytes)
    feature_vector = [features_dict.get(col, 0.0) for col in meta["features"]]
    X_input = pd.DataFrame(
        [feature_vector],
        columns=meta["features"]
    )

    pred_idx = pipeline.predict(X_input)[0]
    probabilities = pipeline.predict_proba(X_input)[0]

    predicted_label = label_encoder.inverse_transform([pred_idx])[0]
    confidence = float(probabilities[pred_idx])

    # Class probability breakdown
    prob_breakdown = {
        label: round(float(prob), 4)
        for label, prob in zip(label_encoder.classes_, probabilities)
    }

    return {
        "predicted_type": predicted_label,
        "confidence": round(confidence, 4),
        "probabilities": prob_breakdown,
        "entropy": features_dict.get("entropy", 0.0),
    }


def main():
    parser = argparse.ArgumentParser(
        description="ReFrag AI - Train Fragment File Type Classifier"
    )
    parser.add_argument(
        "--features-csv",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "features" / "extracted_features.csv"),
        help="Path to extracted features CSV",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "saved"),
        help="Directory to save trained models and artifacts (default: ml/saved)",
    )
    parser.add_argument(
        "--model-type",
        type=str,
        choices=["random_forest", "gradient_boosting"],
        default="random_forest",
        help="Model architecture: random_forest or gradient_boosting",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.25,
        help="Holdout validation split ratio (default: 0.25)",
    )

    args = parser.parse_args()

    train_classifier(
        features_csv=Path(args.features_csv),
        output_dir=Path(args.output_dir),
        test_size=args.test_size,
        model_type=args.model_type,
    )


if __name__ == "__main__":
    main()
