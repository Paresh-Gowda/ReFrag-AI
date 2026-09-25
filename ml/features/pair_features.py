#!/usr/bin/env python3

"""
ReFrag AI - Pairwise Relational Feature Extractor

Creates numerical features describing the relationship between
two fragments for the Fragment Relationship Model.
"""

from pathlib import Path
import argparse

import numpy as np
import pandas as pd


ML_DIR = Path(__file__).resolve().parent.parent

DEFAULT_PAIRS = ML_DIR / "data" / "pairs.csv"
DEFAULT_SINGLE_FEATURES = ML_DIR / "features" / "extracted_features.csv"
DEFAULT_FRAGMENTS = ML_DIR / "data" / "fragments"
DEFAULT_OUTPUT = ML_DIR / "features" / "pair_features.csv"


def compute_bfa_features(a, b):
    """Compare the 256-dimensional byte-frequency vectors."""

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a > 0 and norm_b > 0:
        cosine = float(np.dot(a, b) / (norm_a * norm_b))
    else:
        cosine = 0.0

    euclidean = float(np.linalg.norm(a - b))
    manhattan = float(np.sum(np.abs(a - b)))

    std_a = np.std(a)
    std_b = np.std(b)

    if std_a > 0 and std_b > 0:
        correlation = float(np.corrcoef(a, b)[0, 1])
    else:
        correlation = 0.0

    return {
        "bfa_cosine_similarity": cosine,
        "bfa_euclidean_distance": euclidean,
        "bfa_manhattan_distance": manhattan,
        "bfa_correlation": correlation,
    }


def compute_seam_features(bytes_a, bytes_b):
    """
    Analyze the boundary between fragment A and fragment B.
    """

    if not bytes_a or not bytes_b:
        return {
            "seam_byte_difference": 255.0,
            "seam_avg_difference_4": 255.0,
            "seam_avg_difference_16": 255.0,
            "seam_identical": 0,
            "seam_both_null": 0,
            "seam_both_printable": 0,
        }

    tail = bytes_a[-1]
    head = bytes_b[0]

    printable = set(
        b"abcdefghijklmnopqrstuvwxyz"
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        b"0123456789"
        b"!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ \t\r\n"
    )

    k4 = min(4, len(bytes_a), len(bytes_b))
    k16 = min(16, len(bytes_a), len(bytes_b))

    diff4 = sum(
        abs(bytes_a[-i] - bytes_b[i - 1])
        for i in range(1, k4 + 1)
    ) / k4

    diff16 = sum(
        abs(bytes_a[-i] - bytes_b[i - 1])
        for i in range(1, k16 + 1)
    ) / k16

    return {
        "seam_byte_difference": float(abs(tail - head)),
        "seam_avg_difference_4": float(diff4),
        "seam_avg_difference_16": float(diff16),
        "seam_identical": int(tail == head),
        "seam_both_null": int(tail == 0 and head == 0),
        "seam_both_printable": int(
            tail in printable and head in printable
        ),
    }


def create_pair_features(
    pairs_csv,
    single_features_csv,
    fragments_dir,
    output_csv,
):
    print(f"Loading pairs: {pairs_csv}")
    pairs = pd.read_csv(pairs_csv)

    print(f"Loading fragment features: {single_features_csv}")
    features = pd.read_csv(single_features_csv)

    features = features.set_index("fragment_id")

    required_pair_columns = {
        "fragment_a",
        "fragment_b",
        "source_a",
        "source_b",
        "index_a",
        "index_b",
        "label",
    }

    missing = required_pair_columns - set(pairs.columns)

    if missing:
        raise ValueError(
            f"Missing columns in pairs.csv: {sorted(missing)}"
        )

    byte_columns = [
        f"byte_freq_{i:02x}"
        for i in range(256)
    ]

    statistical_columns = [
        "entropy",
        "mean",
        "variance",
        "std",
        "printable_ratio",
        "null_ratio",
        "high_byte_ratio",
        "control_ratio",
        "max_consecutive",
    ]

    rows = []

    print(f"Processing {len(pairs)} pairs...")

    for count, row in pairs.iterrows():

        fragment_a = row["fragment_a"]
        fragment_b = row["fragment_b"]

        if fragment_a not in features.index:
            continue

        if fragment_b not in features.index:
            continue

        feat_a = features.loc[fragment_a]
        feat_b = features.loc[fragment_b]

        # --------------------------------------------------
        # Byte-frequency similarity
        # --------------------------------------------------

        bfa = feat_a[byte_columns].to_numpy(dtype=float)
        bfb = feat_b[byte_columns].to_numpy(dtype=float)

        bfa_features = compute_bfa_features(bfa, bfb)

        # --------------------------------------------------
        # Statistical relationship
        # --------------------------------------------------

        statistical_features = {}

        for column in statistical_columns:
            statistical_features[f"diff_{column}"] = abs(
                float(feat_a[column]) -
                float(feat_b[column])
            )

        # --------------------------------------------------
        # Fragment ordering
        # --------------------------------------------------

        index_distance = abs(
            int(row["index_a"]) -
            int(row["index_b"])
        )

        # --------------------------------------------------
        # File-type compatibility
        #
        # We do NOT use source_file as an ML feature.
        # --------------------------------------------------

        type_a = str(feat_a.get("file_type", "unknown"))
        type_b = str(feat_b.get("file_type", "unknown"))

        same_file_type = int(type_a == type_b)

        # --------------------------------------------------
        # Raw boundary/seam features
        # --------------------------------------------------

        path_a = fragments_dir / f"{fragment_a}.bin"
        path_b = fragments_dir / f"{fragment_b}.bin"

        if path_a.exists() and path_b.exists():
            bytes_a = path_a.read_bytes()
            bytes_b = path_b.read_bytes()

            seam_features = compute_seam_features(
                bytes_a,
                bytes_b,
            )
        else:
            seam_features = {
                "seam_byte_difference": 128.0,
                "seam_avg_difference_4": 128.0,
                "seam_avg_difference_16": 128.0,
                "seam_identical": 0,
                "seam_both_null": 0,
                "seam_both_printable": 0,
            }

        # --------------------------------------------------
        # Final feature record
        # --------------------------------------------------

        record = {
            "fragment_a": fragment_a,
            "fragment_b": fragment_b,

            # Metadata retained for analysis/splitting.
            # These MUST NOT be used as model features.
            "source_a": row["source_a"],
            "source_b": row["source_b"],

            "index_a": int(row["index_a"]),
            "index_b": int(row["index_b"]),

            # Relationship features
            "index_distance": index_distance,
            "same_file_type": same_file_type,

            **bfa_features,
            **statistical_features,
            **seam_features,

            # Target
            "label": int(row["label"]),
        }

        rows.append(record)

        if (count + 1) % 500 == 0:
            print(f"Processed {count + 1}/{len(pairs)} pairs")

    output = pd.DataFrame(rows)

    output_csv.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.to_csv(
        output_csv,
        index=False,
    )

    print()
    print("Pair feature extraction complete.")
    print(f"Total pairs:    {len(output)}")
    print(
        f"Positive pairs: {(output['label'] == 1).sum()}"
    )
    print(
        f"Negative pairs: {(output['label'] == 0).sum()}"
    )
    print(f"Features saved: {output_csv}")


def main():

    parser = argparse.ArgumentParser(
        description="ReFrag AI pairwise feature extraction"
    )

    parser.add_argument(
        "--pairs-csv",
        default=str(DEFAULT_PAIRS),
    )

    parser.add_argument(
        "--single-features-csv",
        default=str(DEFAULT_SINGLE_FEATURES),
    )

    parser.add_argument(
        "--fragments-dir",
        default=str(DEFAULT_FRAGMENTS),
    )

    parser.add_argument(
        "--output-csv",
        default=str(DEFAULT_OUTPUT),
    )

    args = parser.parse_args()

    create_pair_features(
        pairs_csv=Path(args.pairs_csv),
        single_features_csv=Path(args.single_features_csv),
        fragments_dir=Path(args.fragments_dir),
        output_csv=Path(args.output_csv),
    )


if __name__ == "__main__":
    main()