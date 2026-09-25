#!/usr/bin/env python3
"""
ReFrag AI - Fragment Pair Dataset Generator
Generates positive pairs (consecutive fragments from the same source file)
and negative pairs (fragments from different source files, including same-type
hard negatives and cross-type negatives) for binary relationship modeling.
Saves pairs metadata to ml/data/fragment_pairs.json and ml/data/fragment_pairs.csv.
"""

from __future__ import annotations

import os
import sys
import json
import csv
import random
import argparse
from pathlib import Path
from collections import defaultdict


def generate_pairs(
    metadata_path: Path,
    output_dir: Path,
    negative_ratio: float = 1.0,
    seed: int = 42,
) -> list[dict]:
    """
    Generates balanced positive and negative pairs from fragments metadata.
    """
    rng = random.Random(seed)

    if not metadata_path.exists():
        raise FileNotFoundError(f"Fragments metadata not found at {metadata_path}")

    with open(metadata_path, "r", encoding="utf-8") as f:
        fragments = json.load(f)

    print(f"[*] Loaded {len(fragments)} fragments from {metadata_path}")

    # Group fragments by source_file and sort by fragment_index
    by_source: dict[str, list[dict]] = defaultdict(list)
    by_type: dict[str, list[dict]] = defaultdict(list)

    for frag in fragments:
        by_source[frag["source_file"]].append(frag)
        by_type[frag["file_type"]].append(frag)

    # Sort each file's fragments sequentially
    for src in by_source:
        by_source[src].sort(key=lambda x: x["fragment_index"])

    # 1. Generate Positive Pairs (Consecutive neighbors in the same file)
    positive_pairs = []
    for src, frags in by_source.items():
        if len(frags) < 2:
            continue
        for i in range(len(frags) - 1):
            frag_a = frags[i]
            frag_b = frags[i + 1]

            pair = {
                "pair_id": f"PAIR_POS_{len(positive_pairs) + 1:06d}",
                "frag_a_id": frag_a["fragment_id"],
                "frag_b_id": frag_b["fragment_id"],
                "frag_a_file": frag_a["fragment_file"],
                "frag_b_file": frag_b["fragment_file"],
                "source_a": frag_a["source_file"],
                "source_b": frag_b["source_file"],
                "type_a": frag_a["file_type"],
                "type_b": frag_b["file_type"],
                "index_a": frag_a["fragment_index"],
                "index_b": frag_b["fragment_index"],
                "is_header_a": int(frag_a.get("is_header", False)),
                "is_footer_b": int(frag_b.get("is_footer", False)),
                "label": 1,
                "pair_type": "consecutive_neighbor",
            }
            positive_pairs.append(pair)

    num_positives = len(positive_pairs)
    target_negatives = int(num_positives * negative_ratio)
    print(f"[+] Generated {num_positives} positive (sequential neighbor) pairs.")

    # 2. Generate Negative Pairs (from DIFFERENT source files)
    # Split into:
    #   - 50% Hard Negatives: same file type, but different source files (e.g. JPEG_file1 with JPEG_file2)
    #   - 50% Cross-type Negatives: different file types, different source files (e.g. JPEG with PDF)
    negative_pairs = []
    seen_neg_pairs: set[tuple[str, str]] = set()

    sources_list = list(by_source.keys())
    target_hard_neg = target_negatives // 2
    target_cross_neg = target_negatives - target_hard_neg

    # A) Hard negatives (same type, different source file)
    types_with_multiple_sources = [
        t for t, frags in by_type.items()
        if len(set(f["source_file"] for f in frags)) > 1
    ]

    attempts = 0
    max_attempts = target_hard_neg * 20
    while len(negative_pairs) < target_hard_neg and attempts < max_attempts:
        attempts += 1
        t = rng.choice(types_with_multiple_sources)
        type_frags = by_type[t]
        fa = rng.choice(type_frags)
        fb = rng.choice(type_frags)

        if fa["source_file"] == fb["source_file"]:
            continue

        pair_key = (fa["fragment_id"], fb["fragment_id"])
        if pair_key in seen_neg_pairs:
            continue
        seen_neg_pairs.add(pair_key)

        pair = {
            "pair_id": f"PAIR_NEG_{len(negative_pairs) + 1:06d}",
            "frag_a_id": fa["fragment_id"],
            "frag_b_id": fb["fragment_id"],
            "frag_a_file": fa["fragment_file"],
            "frag_b_file": fb["fragment_file"],
            "source_a": fa["source_file"],
            "source_b": fb["source_file"],
            "type_a": fa["file_type"],
            "type_b": fb["file_type"],
            "index_a": fa["fragment_index"],
            "index_b": fb["fragment_index"],
            "is_header_a": int(fa.get("is_header", False)),
            "is_footer_b": int(fb.get("is_footer", False)),
            "label": 0,
            "pair_type": "negative_same_type",
        }
        negative_pairs.append(pair)

    # B) Cross-type negatives (different types, different source files)
    attempts = 0
    max_attempts = target_cross_neg * 20
    types_list = list(by_type.keys())

    while len(negative_pairs) < target_negatives and attempts < max_attempts:
        attempts += 1
        if len(types_list) >= 2:
            t1, t2 = rng.sample(types_list, 2)
            fa = rng.choice(by_type[t1])
            fb = rng.choice(by_type[t2])
        else:
            fa = rng.choice(fragments)
            fb = rng.choice(fragments)

        if fa["source_file"] == fb["source_file"]:
            continue

        pair_key = (fa["fragment_id"], fb["fragment_id"])
        if pair_key in seen_neg_pairs:
            continue
        seen_neg_pairs.add(pair_key)

        pair = {
            "pair_id": f"PAIR_NEG_{len(negative_pairs) + 1:06d}",
            "frag_a_id": fa["fragment_id"],
            "frag_b_id": fb["fragment_id"],
            "frag_a_file": fa["fragment_file"],
            "frag_b_file": fb["fragment_file"],
            "source_a": fa["source_file"],
            "source_b": fb["source_file"],
            "type_a": fa["file_type"],
            "type_b": fb["file_type"],
            "index_a": fa["fragment_index"],
            "index_b": fb["fragment_index"],
            "is_header_a": int(fa.get("is_header", False)),
            "is_footer_b": int(fb.get("is_footer", False)),
            "label": 0,
            "pair_type": "negative_diff_type",
        }
        negative_pairs.append(pair)

    print(f"[+] Generated {len(negative_pairs)} negative (non-related) pairs.")

    # Combine and shuffle
    all_pairs = positive_pairs + negative_pairs
    rng.shuffle(all_pairs)

    # Save to JSON and CSV
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "fragment_pairs.json"
    csv_path = output_dir / "fragment_pairs.csv"

    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(all_pairs, jf, indent=2)

    if all_pairs:
        fieldnames = list(all_pairs[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as cf:
            writer = csv.DictWriter(cf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_pairs)

    print("\n[+] Pair Dataset Generation Complete!")
    print(f"  Total Pairs:    {len(all_pairs)} ({num_positives} positive, {len(negative_pairs)} negative)")
    print(f"  Saved JSON:     {json_path}")
    print(f"  Saved CSV:      {csv_path}")

    return all_pairs


def main():
    parser = argparse.ArgumentParser(
        description="ReFrag AI - Generate Fragment Pairs for Relationship Modeling"
    )
    parser.add_argument(
        "--metadata-path",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "data" / "fragments_metadata.json"),
        help="Path to fragments metadata JSON (default: ml/data/fragments_metadata.json)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "data"),
        help="Output directory for fragment pairs (default: ml/data)",
    )
    parser.add_argument(
        "--negative-ratio",
        type=float,
        default=1.0,
        help="Ratio of negative pairs to positive pairs (default: 1.0 for balanced 50/50)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )

    args = parser.parse_args()

    generate_pairs(
        metadata_path=Path(args.metadata_path),
        output_dir=Path(args.output_dir),
        negative_ratio=args.negative_ratio,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
