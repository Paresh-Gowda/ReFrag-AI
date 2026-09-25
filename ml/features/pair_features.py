#!/usr/bin/env python3
"""
ReFrag AI - Pairwise Relational Feature Extractor
Extracts boundary/seam transition metrics, byte-frequency vector distances
(cosine, euclidean, manhattan), and statistical consistency features
between fragment pairs to determine continuation probability.
"""

from __future__ import annotations

import os
import sys
import math
import csv
import json
import argparse
from pathlib import Path
from collections import Counter

# Add parent directory to path to import single-fragment extractor
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    import numpy as np
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from features.extract_features import extract_features_from_bytes


def compute_bfa_distances(bfa_a: np.ndarray, bfa_b: np.ndarray) -> dict[str, float]:
    """Computes distance and similarity metrics between two 256-D BFA vectors."""
    norm_a = np.linalg.norm(bfa_a)
    norm_b = np.linalg.norm(bfa_b)

    # Cosine Similarity
    if norm_a > 0 and norm_b > 0:
        cosine_sim = float(np.dot(bfa_a, bfa_b) / (norm_a * norm_b))
    else:
        cosine_sim = 0.0

    # Euclidean Distance (L2)
    euclidean_dist = float(np.linalg.norm(bfa_a - bfa_b))

    # Manhattan Distance (L1)
    manhattan_dist = float(np.sum(np.abs(bfa_a - bfa_b)))

    # Pearson Correlation
    std_a = np.std(bfa_a)
    std_b = np.std(bfa_b)
    if std_a > 0 and std_b > 0:
        corr = float(np.corrcoef(bfa_a, bfa_b)[0, 1])
    else:
        corr = 0.0

    return {
        "bfa_cosine_sim": round(cosine_sim, 5),
        "bfa_euclidean_dist": round(euclidean_dist, 5),
        "bfa_manhattan_dist": round(manhattan_dist, 5),
        "bfa_correlation": round(corr, 5),
    }


def compute_seam_features(bytes_a: bytes, bytes_b: bytes) -> dict[str, float]:
    """
    Extracts microscopic continuity features across the boundary seam
    between the tail of fragment A and the head of fragment B.
    """
    len_a = len(bytes_a)
    len_b = len(bytes_b)

    if len_a == 0 or len_b == 0:
        return {
            "seam_byte_diff": 255.0,
            "seam_avg_diff_4": 255.0,
            "seam_avg_diff_16": 255.0,
            "seam_both_null": 0,
            "seam_both_printable": 0,
            "seam_identical": 0,
        }

    tail_byte = bytes_a[-1]
    head_byte = bytes_b[0]

    seam_byte_diff = abs(tail_byte - head_byte)
    seam_identical = int(tail_byte == head_byte)
    seam_both_null = int(tail_byte == 0 and head_byte == 0)

    printable_set = set(b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ \t\r\n")
    seam_both_printable = int(tail_byte in printable_set and head_byte in printable_set)

    # 4-byte boundary window
    k4 = min(4, len_a, len_b)
    diff_4 = sum(abs(bytes_a[-i] - bytes_b[i - 1]) for i in range(1, k4 + 1)) / k4

    # 16-byte boundary window
    k16 = min(16, len_a, len_b)
    diff_16 = sum(abs(bytes_a[-i] - bytes_b[i - 1]) for i in range(1, k16 + 1)) / k16

    return {
        "seam_byte_diff": float(seam_byte_diff),
        "seam_avg_diff_4": round(diff_4, 4),
        "seam_avg_diff_16": round(diff_16, 4),
        "seam_both_null": seam_both_null,
        "seam_both_printable": seam_both_printable,
        "seam_identical": seam_identical,
    }


def extract_pair_features_from_bytes(bytes_a: bytes, bytes_b: bytes) -> dict:
    """
    Computes complete pair features directly from two raw byte sequences.
    Used during live inference and reconstruction graph building.
    """
    feat_a = extract_features_from_bytes(bytes_a, include_bfa=True)
    feat_b = extract_features_from_bytes(bytes_b, include_bfa=True)

    bfa_a = np.array([feat_a[f"byte_freq_{b:02x}"] for b in range(256)])
    bfa_b = np.array([feat_b[f"byte_freq_{b:02x}"] for b in range(256)])
    bfa_dists = compute_bfa_distances(bfa_a, bfa_b)

    seam = compute_seam_features(bytes_a, bytes_b)

    pair_feat = {
        # Boundary seam
        **seam,
        # BFA vector distances
        **bfa_dists,
        # Statistical consistency differences
        "diff_entropy": round(abs(feat_a["entropy"] - feat_b["entropy"]), 4),
        "avg_entropy": round((feat_a["entropy"] + feat_b["entropy"]) / 2.0, 4),
        "diff_mean": round(abs(feat_a["mean"] - feat_b["mean"]), 4),
        "diff_std": round(abs(feat_a["std"] - feat_b["std"]), 4),
        "diff_variance": round(abs(feat_a["variance"] - feat_b["variance"]), 4),
        "diff_printable": round(abs(feat_a["printable_ratio"] - feat_b["printable_ratio"]), 4),
        "diff_null": round(abs(feat_a["null_ratio"] - feat_b["null_ratio"]), 4),
        "diff_high_byte": round(abs(feat_a["high_byte_ratio"] - feat_b["high_byte_ratio"]), 4),
        "diff_control": round(abs(feat_a["control_ratio"] - feat_b["control_ratio"]), 4),
        "diff_max_consecutive": abs(feat_a["max_consecutive"] - feat_b["max_consecutive"]),
        # Structural flags
        "has_magic_header_a": feat_a.get("has_magic_header", 0),
        "has_magic_footer_b": feat_b.get("has_magic_footer", 0),
        "invalid_boundary": int(feat_a.get("has_magic_footer", 0) == 1 or feat_b.get("has_magic_header", 0) == 1),
    }

    return pair_feat


def generate_pair_features_dataset(
    pairs_csv: Path,
    single_features_csv: Path,
    fragments_dir: Path,
    output_csv: Path,
):
    """
    Reads pairs from pairs_csv, combines single-fragment features and raw seam metrics,
    and produces the pair_features.csv dataset for relationship classifier training.
    """
    if not pairs_csv.exists():
        raise FileNotFoundError(f"Pairs file not found at {pairs_csv}")
    if not single_features_csv.exists():
        raise FileNotFoundError(f"Single features CSV not found at {single_features_csv}")

    print(f"[*] Loading single-fragment features from {single_features_csv}...")
    single_df = pd.read_csv(single_features_csv).set_index("fragment_id")

    print(f"[*] Loading fragment pairs from {pairs_csv}...")
    pairs_df = pd.read_csv(pairs_csv)

    print(f"[*] Extracting relational features for {len(pairs_df)} pairs...")
    pair_rows = []

    # Cache for BFA vectors to avoid rebuilding arrays repeatedly
    bfa_cols = [f"byte_freq_{b:02x}" for b in range(256)]
    bfa_cache: dict[str, np.ndarray] = {}

    for idx, row in pairs_df.iterrows():
        fa_id = row["frag_a_id"]
        fb_id = row["frag_b_id"]

        if fa_id not in single_df.index or fb_id not in single_df.index:
            continue

        feat_a = single_df.loc[fa_id]
        feat_b = single_df.loc[fb_id]

        # BFA vectors
        if fa_id not in bfa_cache:
            bfa_cache[fa_id] = feat_a[bfa_cols].to_numpy(dtype=float)
        if fb_id not in bfa_cache:
            bfa_cache[fb_id] = feat_b[bfa_cols].to_numpy(dtype=float)

        bfa_dists = compute_bfa_distances(bfa_cache[fa_id], bfa_cache[fb_id])

        # Raw boundary seam metrics
        file_a_path = fragments_dir / row["frag_a_file"]
        file_b_path = fragments_dir / row["frag_b_file"]

        if file_a_path.exists() and file_b_path.exists():
            bytes_a = file_a_path.read_bytes()
            bytes_b = file_b_path.read_bytes()
            seam = compute_seam_features(bytes_a, bytes_b)
        else:
            seam = {
                "seam_byte_diff": 128.0,
                "seam_avg_diff_4": 128.0,
                "seam_avg_diff_16": 128.0,
                "seam_both_null": 0,
                "seam_both_printable": 0,
                "seam_identical": 0,
            }

        same_type = int(str(row["type_a"]).lower() == str(row["type_b"]).lower())

        pair_record = {
            # Metadata identifiers (preserved for group-aware splitting)
            "pair_id": row["pair_id"],
            "frag_a_id": fa_id,
            "frag_b_id": fb_id,
            "source_a": row["source_a"],
            "source_b": row["source_b"],
            "type_a": row["type_a"],
            "type_b": row["type_b"],
            "same_file_type": same_type,
            # Target Label
            "label": int(row["label"]),
            # Seam features
            **seam,
            # BFA distribution distances
            **bfa_dists,
            # Statistical consistency differences
            "diff_entropy": round(abs(float(feat_a["entropy"]) - float(feat_b["entropy"])), 4),
            "avg_entropy": round((float(feat_a["entropy"]) + float(feat_b["entropy"])) / 2.0, 4),
            "diff_mean": round(abs(float(feat_a["mean"]) - float(feat_b["mean"])), 4),
            "diff_std": round(abs(float(feat_a["std"]) - float(feat_b["std"])), 4),
            "diff_variance": round(abs(float(feat_a["variance"]) - float(feat_b["variance"])), 4),
            "diff_printable": round(abs(float(feat_a["printable_ratio"]) - float(feat_b["printable_ratio"])), 4),
            "diff_null": round(abs(float(feat_a["null_ratio"]) - float(feat_b["null_ratio"])), 4),
            "diff_high_byte": round(abs(float(feat_a["high_byte_ratio"]) - float(feat_b["high_byte_ratio"])), 4),
            "diff_control": round(abs(float(feat_a["control_ratio"]) - float(feat_b["control_ratio"])), 4),
            "diff_max_consecutive": abs(int(feat_a["max_consecutive"]) - int(feat_b["max_consecutive"])),
            # Structural ordering markers
            "is_header_a": int(row.get("is_header_a", 0)),
            "is_footer_b": int(row.get("is_footer_b", 0)),
            "has_magic_header_a": int(feat_a.get("has_magic_header", 0)),
            "has_magic_footer_b": int(feat_b.get("has_magic_footer", 0)),
            "invalid_boundary": int(int(feat_a.get("has_magic_footer", 0)) == 1 or int(feat_b.get("has_magic_header", 0)) == 1),
        }
        pair_rows.append(pair_record)

        if (idx + 1) % 500 == 0 or (idx + 1) == len(pairs_df):
            print(f"  Processed {idx + 1}/{len(pairs_df)} pairs")

    out_df = pd.DataFrame(pair_rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_csv, index=False)

    print(f"\n[+] Relational Pair Features saved to: {output_csv}")
    print(f"  Total Pairs:    {len(out_df)}")
    print(f"  Positive Pairs: {(out_df['label'] == 1).sum()}")
    print(f"  Negative Pairs: {(out_df['label'] == 0).sum()}")


def main():
    parser = argparse.ArgumentParser(
        description="ReFrag AI - Pairwise Relational Feature Extractor"
    )
    parser.add_argument(
        "--pairs-csv",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "data" / "fragment_pairs.csv"),
        help="Path to pairs metadata CSV (default: ml/data/fragment_pairs.csv)",
    )
    parser.add_argument(
        "--single-features-csv",
        type=str,
        default=str(Path(__file__).resolve().parent / "extracted_features.csv"),
        help="Path to single-fragment features CSV (default: ml/features/extracted_features.csv)",
    )
    parser.add_argument(
        "--fragments-dir",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "data" / "fragments"),
        help="Directory with raw binary fragments (default: ml/data/fragments)",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default=str(Path(__file__).resolve().parent / "pair_features.csv"),
        help="Output CSV for pair features (default: ml/features/pair_features.csv)",
    )

    args = parser.parse_args()

    generate_pair_features_dataset(
        pairs_csv=Path(args.pairs_csv),
        single_features_csv=Path(args.single_features_csv),
        fragments_dir=Path(args.fragments_dir),
        output_csv=Path(args.output_csv),
    )


if __name__ == "__main__":
    main()
