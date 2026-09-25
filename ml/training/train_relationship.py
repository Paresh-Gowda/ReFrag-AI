#!/usr/bin/env python3

"""
ReFrag AI - Fragment Relationship Model

Trains a binary classifier to determine whether two fragments
are likely related/consecutive.
"""

from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split


ML_DIR = Path(__file__).resolve().parent.parent

PAIR_FEATURES_PATH = (
    ML_DIR / "features" / "pair_features.csv"
)

MODEL_PATH = (
    ML_DIR / "saved" / "relationship_model.joblib"
)

METADATA_PATH = (
    ML_DIR / "saved" / "relationship_model_metadata.json"
)

RANDOM_STATE = 42


def main():

    print("Loading pair features...")

    df = pd.read_csv(PAIR_FEATURES_PATH)

    print(f"Total pairs: {len(df)}")

    # --------------------------------------------------
    # Target
    # --------------------------------------------------

    if "label" not in df.columns:
        raise ValueError("Missing 'label' column.")

    y = df["label"].astype(int)

    # --------------------------------------------------
    # Metadata columns
    #
    # These must NOT be used as ML features.
    # --------------------------------------------------

    metadata_columns = [
        "fragment_a",
        "fragment_b",
        "source_a",
        "source_b",
        "index_a",
        "index_b",
        "label",
    ]

    feature_columns = [
        column
        for column in df.columns
        if column not in metadata_columns
    ]

    # Keep only numeric features
    X = df[feature_columns].select_dtypes(
        include=[np.number]
    )

    feature_columns = X.columns.tolist()

    print(f"Features: {len(feature_columns)}")

    # --------------------------------------------------
    # Leakage-safe split
    #
    # Split SOURCE FILES first.
    # No source file can appear in both train/test.
    # --------------------------------------------------

    sources = sorted(
        set(df["source_a"]) |
        set(df["source_b"])
    )

    train_sources, test_sources = train_test_split(
        sources,
        test_size=0.25,
        random_state=RANDOM_STATE,
    )

    train_sources = set(train_sources)
    test_sources = set(test_sources)

    train_mask = (
        df["source_a"].isin(train_sources) &
        df["source_b"].isin(train_sources)
    )

    test_mask = (
        df["source_a"].isin(test_sources) &
        df["source_b"].isin(test_sources)
    )

    X_train = X.loc[train_mask]
    y_train = y.loc[train_mask]

    X_test = X.loc[test_mask]
    y_test = y.loc[test_mask]

    print()
    print("Leakage-safe split")
    print("------------------")
    print(f"Train source files: {len(train_sources)}")
    print(f"Test source files:  {len(test_sources)}")
    print(f"Train pairs:        {len(X_train)}")
    print(f"Test pairs:         {len(X_test)}")

    # --------------------------------------------------
    # Safety checks
    # --------------------------------------------------

    overlap = train_sources.intersection(test_sources)

    if overlap:
        raise RuntimeError(
            f"Source leakage detected: {overlap}"
        )

    if len(X_train) == 0 or len(X_test) == 0:
        raise RuntimeError(
            "Train/test split produced an empty dataset."
        )

    # --------------------------------------------------
    # Model
    # --------------------------------------------------

    print()
    print("Training Random Forest...")

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=18,
        min_samples_split=4,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    # --------------------------------------------------
    # Evaluation
    # --------------------------------------------------

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_test,
        predictions,
    )

    print()
    print("MODEL 2 RESULTS")
    print("================")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    print()
    print("Confusion Matrix")
    print("----------------")
    print(matrix)

    print()
    print("Classification Report")
    print("---------------------")
    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "Unrelated",
                "Related",
            ],
            zero_division=0,
        )
    )

    # --------------------------------------------------
    # Feature importance
    # --------------------------------------------------

    importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": model.feature_importances_,
        }
    ).sort_values(
        "importance",
        ascending=False,
    )

    print("Top Features")
    print("------------")

    for _, row in importance.head(15).iterrows():
        print(
            f"{row['feature']:<35} "
            f"{row['importance']:.4f}"
        )

    # --------------------------------------------------
    # Save model
    # --------------------------------------------------

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    metadata = {
        "model": "RandomForestClassifier",
        "task": "fragment_relationship_classification",
        "random_state": RANDOM_STATE,
        "train_pairs": int(len(X_train)),
        "test_pairs": int(len(X_test)),
        "train_source_files": int(len(train_sources)),
        "test_source_files": int(len(test_sources)),
        "features": feature_columns,
        "metrics": {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
        },
        "confusion_matrix": matrix.tolist(),
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            metadata,
            f,
            indent=2,
        )

    print()
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metadata saved to: {METADATA_PATH}")


if __name__ == "__main__":
    main()