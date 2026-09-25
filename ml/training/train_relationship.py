#!/usr/bin/env python3
"""
ReFrag AI - Fragment Relationship & Sequence Model Trainer
Trains a Random Forest classifier to predict whether Fragment B follows
Fragment A (neighboring sequential relationship) using pairwise seam,
statistical consistency, and BFA vector distance features.
Uses strict group-aware train/test splitting by source_file to eliminate
data leakage and saves the trained model to ml/saved/relationship_model.joblib.
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
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (
        classification_report,
        accuracy_score,
        roc_auc_score,
        confusion_matrix,
        precision_score,
        recall_score,
        f1_score,
    )
    from sklearn.pipeline import Pipeline
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def check_dependencies():
    """Verify that required ML libraries are installed."""
    if not SKLEARN_AVAILABLE:
        print("[!] Required machine learning libraries are missing.")
        print("    Please run: pip install numpy pandas scikit-learn joblib")
        sys.exit(1)


def load_pair_dataset(features_csv: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, list[str]]:
    """
    Loads pairwise features from CSV, separating metadata columns
    from numerical features X and target label y.
    """
    if not features_csv.exists():
        raise FileNotFoundError(
            f"Pair feature dataset not found at {features_csv}.\n"
            "Run 'ml/features/pair_features.py' first to extract pair features."
        )

    df = pd.read_csv(features_csv)

    # Identifiers and non-feature columns
    meta_cols = [
        "pair_id",
        "frag_a_id",
        "frag_b_id",
        "source_a",
        "source_b",
        "type_a",
        "type_b",
        "label",
    ]

    feature_cols = [c for c in df.columns if c not in meta_cols]
    X = df[feature_cols].copy().fillna(0.0)
    y = df["label"].copy().astype(int)

    return df, X, y, feature_cols


def group_split_pairs(
    df: pd.DataFrame,
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.25,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, list[str], list[str]]:
    """
    Partitions pairs strictly by source_file to ensure zero data leakage.
    Any source file in the test partition has NEVER appeared in the training set.
    """
    all_sources = sorted(list(set(df["source_a"].unique()).union(set(df["source_b"].unique()))))

    # Stratify by category prefix if available (e.g. sample_jpeg_*, sample_pdf_*)
    def get_category(src_name: str) -> str:
        for cat in ["jpeg", "png", "pdf", "zip", "text"]:
            if cat in src_name.lower():
                return cat
        return "other"

    source_cats = [get_category(s) for s in all_sources]
    cat_counts = pd.Series(source_cats).value_counts()
    stratify = source_cats if cat_counts.min() >= 2 else None

    train_sources, test_sources = train_test_split(
        all_sources,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )
    train_sources_set = set(train_sources)
    test_sources_set = set(test_sources)

    # Strict isolation:
    # A training pair must have BOTH sources in train_sources
    # A test pair must have BOTH sources in test_sources
    train_mask = df["source_a"].isin(train_sources_set) & df["source_b"].isin(train_sources_set)
    test_mask = df["source_a"].isin(test_sources_set) & df["source_b"].isin(test_sources_set)

    X_train = X[train_mask]
    y_train = y[train_mask]
    X_test = X[test_mask]
    y_test = y[test_mask]

    return X_train, X_test, y_train, y_test, train_sources, test_sources


def train_relationship_model(
    features_csv: Path,
    output_dir: Path,
    test_size: float = 0.25,
    n_estimators: int = 140,
    random_state: int = 42,
):
    """
    Trains the Fragment Relationship Random Forest model.
    """
    check_dependencies()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Loading pair feature dataset from {features_csv}...")
    df, X, y, feature_cols = load_pair_dataset(features_csv)

    print(f"  Total Pairs:    {len(X)}")
    print(f"  Total Features: {len(feature_cols)}")
    print(f"  Positive Pairs: {(y == 1).sum()} (sequential neighbors)")
    print(f"  Negative Pairs: {(y == 0).sum()} (different files / non-neighbors)")

    # Group-aware split by source_file to eliminate leakage
    print("\n[*] Performing strict group-aware split by source_file...")
    X_train, X_test, y_train, y_test, train_srcs, test_srcs = group_split_pairs(
        df, X, y, test_size=test_size, random_state=random_state
    )

    print(f"  Source Files:   {len(train_srcs)} Train | {len(test_srcs)} Test")
    print(f"  Train Pairs:    {len(X_train)} (Pos: {(y_train == 1).sum()}, Neg: {(y_train == 0).sum()})")
    print(f"  Test Pairs:     {len(X_test)} (Pos: {(y_test == 1).sum()}, Neg: {(y_test == 0).sum()})")
    print("  [i] Zero-leakage verification: No test source file was ever seen during training.")

    # Initialize Random Forest Classifier
    print(f"\n[*] Training Random Forest Relationship Classifier ({n_estimators} trees)...")
    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=16,
        min_samples_split=2,
        class_weight="balanced",
        n_jobs=-1,
        random_state=random_state,
    )

    pipeline = Pipeline([
        ("classifier", clf),
    ])

    pipeline.fit(X_train, y_train)

    # Evaluate on the completely unseen holdout test set
    print("[*] Evaluating on holdout test set...")
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred).tolist()

    print("\n" + "=" * 60)
    print("      FRAGMENT RELATIONSHIP MODEL - EVALUATION RESULTS")
    print("=" * 60)
    print(f"Test Accuracy:     {accuracy * 100:.2f}%")
    print(f"ROC-AUC Score:     {roc_auc:.4f}")
    print(f"Precision:         {precision * 100:.2f}%")
    print(f"Recall:            {recall * 100:.2f}%")
    print(f"F1-Score:          {f1 * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Non-Neighbor (0)", "Neighbor (1)"], zero_division=0))

    print("Confusion Matrix:")
    print(f"  True Negatives:  {cm[0][0]:4d} | False Positives: {cm[0][1]:4d}")
    print(f"  False Negatives: {cm[1][0]:4d} | True Positives:  {cm[1][1]:4d}")
    print("=" * 60)

    # Top discriminative relational features
    feature_importances = {}
    if hasattr(clf, "feature_importances_"):
        top_indices = np.argsort(clf.feature_importances_)[::-1][:15]
        print("\nTop 15 Most Predictive Relational Features:")
        for rank, idx in enumerate(top_indices, 1):
            feat_name = feature_cols[idx]
            imp = float(clf.feature_importances_[idx])
            feature_importances[feat_name] = round(imp, 5)
            print(f"  {rank:2d}. {feat_name:22s}: {imp * 100:.2f}%")

    # Serialize artifacts
    model_save_path = output_dir / "relationship_model.joblib"
    meta_save_path = output_dir / "relationship_metadata.json"

    joblib.dump(pipeline, model_save_path)

    metadata_payload = {
        "model_name": "ReFrag Fragment Relationship Classifier",
        "algorithm": "RandomForestClassifier",
        "n_estimators": n_estimators,
        "features": feature_cols,
        "metrics": {
            "accuracy": round(accuracy, 4),
            "roc_auc": round(roc_auc, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
        },
        "feature_importances_top15": feature_importances,
        "confusion_matrix": cm,
        "train_pairs_count": len(X_train),
        "test_pairs_count": len(X_test),
        "train_source_files_count": len(train_srcs),
        "test_source_files_count": len(test_srcs),
    }

    with open(meta_save_path, "w", encoding="utf-8") as jf:
        json.dump(metadata_payload, jf, indent=2)

    print(f"\n[+] Saved trained model to:    {model_save_path}")
    print(f"[+] Saved evaluation specs to: {meta_save_path}")

    return pipeline, metadata_payload


def predict_relationship(
    frag_a_bytes: bytes,
    frag_b_bytes: bytes,
    model_dir: Path,
) -> dict:
    """
    Live inference function: given raw bytes of Fragment A and Fragment B,
    extracts relational features and predicts the probability that
    Fragment B directly continues from Fragment A.
    """
    from features.pair_features import extract_pair_features_from_bytes

    model_path = model_dir / "relationship_model.joblib"
    meta_path = model_dir / "relationship_metadata.json"

    if not model_path.exists() or not meta_path.exists():
        raise FileNotFoundError(f"Relationship model artifacts not found in {model_dir}")

    pipeline = joblib.load(model_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Compute pairwise features
    feat_dict = extract_pair_features_from_bytes(frag_a_bytes, frag_b_bytes)
    feature_vector = [feat_dict.get(c, 0.0) for c in meta["features"]]

    X_input = pd.DataFrame([feature_vector], columns=meta["features"])

    prob = float(pipeline.predict_proba(X_input)[0, 1])
    is_related = bool(prob >= 0.5)

    return {
        "is_related": is_related,
        "relationship_probability": round(prob, 4),
        "confidence": round(abs(prob - 0.5) * 2.0, 4),
        "bfa_cosine_sim": feat_dict.get("bfa_cosine_sim", 0.0),
        "seam_byte_diff": feat_dict.get("seam_byte_diff", 255.0),
        "diff_entropy": feat_dict.get("diff_entropy", 0.0),
    }


def main():
    parser = argparse.ArgumentParser(
        description="ReFrag AI - Train Fragment Relationship Model"
    )
    parser.add_argument(
        "--features-csv",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "features" / "pair_features.csv"),
        help="Path to pair features CSV (default: ml/features/pair_features.csv)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "saved"),
        help="Directory to save trained model (default: ml/saved)",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.25,
        help="Source-file holdout test split ratio (default: 0.25)",
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=140,
        help="Number of trees in Random Forest (default: 140)",
    )

    args = parser.parse_args()

    train_relationship_model(
        features_csv=Path(args.features_csv),
        output_dir=Path(args.output_dir),
        test_size=args.test_size,
        n_estimators=args.n_estimators,
    )


if __name__ == "__main__":
    main()
