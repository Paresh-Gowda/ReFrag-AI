#!/usr/bin/env python3
"""
ReFrag AI - Forensic Byte-Level Feature Extractor
Extracts statistical, structural, and byte-frequency distribution (BFA)
features from raw binary fragments for file type classification and
evidence reconstruction compatibility.
"""

import os
import sys
import math
import json
import csv
import argparse
from pathlib import Path
from collections import Counter

# Known file signatures (magic bytes)
MAGIC_HEADERS = {
    "jpeg": b"\xFF\xD8\xFF",
    "png": b"\x89PNG\r\n\x1a\n",
    "gif": b"GIF8",
    "pdf": b"%PDF-",
    "zip": b"PK\x03\x04",
    "rar": b"Rar!\x1a\x07",
    "pe_exe": b"MZ",
    "elf": b"\x7FELF",
}

MAGIC_FOOTERS = {
    "jpeg": b"\xFF\xD9",
    "png": b"IEND\xaeB`\x82",
    "pdf": b"%%EOF",
    "zip": b"PK\x05\x06",
}


def calculate_entropy(byte_counts: Counter, length: int) -> float:
    """Calculates Shannon entropy in bits (0.0 to 8.0)."""
    if length == 0:
        return 0.0
    entropy = 0.0
    for count in byte_counts.values():
        p = count / length
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def extract_features_from_bytes(data: bytes, include_bfa: bool = True) -> dict:
    """
    Extracts forensic features from a raw byte sequence.
    Returns a dictionary of named numerical features.
    """
    length = len(data)
    if length == 0:
        features = {
            "size": 0,
            "entropy": 0.0,
            "mean": 0.0,
            "variance": 0.0,
            "std": 0.0,
            "printable_ratio": 0.0,
            "null_ratio": 0.0,
            "high_byte_ratio": 0.0,
            "control_ratio": 0.0,
            "max_consecutive": 0,
            "has_magic_header": 0,
            "has_magic_footer": 0,
        }
        if include_bfa:
            for b in range(256):
                features[f"byte_freq_{b:02x}"] = 0.0
        return features

    counts = Counter(data)

    # 1. Shannon Entropy
    entropy = calculate_entropy(counts, length)

    # 2. Statistical Moments
    mean = sum(data) / length
    variance = sum((b - mean) ** 2 for b in data) / length
    std = math.sqrt(variance)

    # 3. Byte Categorization Ratios
    printable_chars = set(b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ \t\r\n")
    printable_count = sum(1 for b in data if b in printable_chars)
    null_count = counts.get(0, 0)
    high_byte_count = sum(1 for b in data if b >= 128)
    control_count = sum(1 for b in data if b < 32 and b not in (9, 10, 13))

    printable_ratio = printable_count / length
    null_ratio = null_count / length
    high_byte_ratio = high_byte_count / length
    control_ratio = control_count / length

    # 4. Longest streak of consecutive identical bytes (e.g. 0x00 padding)
    max_consecutive = 1
    current_consecutive = 1
    for i in range(1, length):
        if data[i] == data[i - 1]:
            current_consecutive += 1
            if current_consecutive > max_consecutive:
                max_consecutive = current_consecutive
        else:
            current_consecutive = 1

    # 5. Magic Byte Header / Footer Detection
    has_magic_header = 0
    for sig in MAGIC_HEADERS.values():
        if data.startswith(sig):
            has_magic_header = 1
            break

    has_magic_footer = 0
    for sig in MAGIC_FOOTERS.values():
        if sig in data[-128:]:
            has_magic_footer = 1
            break

    features = {
        "size": length,
        "entropy": round(entropy, 4),
        "mean": round(mean, 4),
        "variance": round(variance, 4),
        "std": round(std, 4),
        "printable_ratio": round(printable_ratio, 4),
        "null_ratio": round(null_ratio, 4),
        "high_byte_ratio": round(high_byte_ratio, 4),
        "control_ratio": round(control_ratio, 4),
        "max_consecutive": max_consecutive,
        "has_magic_header": has_magic_header,
        "has_magic_footer": has_magic_footer,
    }

    # 6. Byte Frequency Distribution (BFA) - 256 normalized values
    if include_bfa:
        for b in range(256):
            features[f"byte_freq_{b:02x}"] = round(counts.get(b, 0) / length, 5)

    return features


def extract_dataset_features(
    fragments_dir: Path,
    metadata_path: Path,
    output_csv_path: Path,
    include_bfa: bool = True,
):
    """
    Reads fragments listed in metadata_path, extracts features,
    and writes out a consolidated CSV dataset for model training.
    """
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    with open(metadata_path, "r", encoding="utf-8") as f:
        fragments = json.load(f)

    print(f"[*] Extracting features for {len(fragments)} fragments...")
    dataset_rows = []

    for idx, item in enumerate(fragments):
        frag_filename = item["fragment_file"]
        frag_file_path = fragments_dir / frag_filename

        if not frag_file_path.exists():
            continue

        raw_bytes = frag_file_path.read_bytes()
        features = extract_features_from_bytes(raw_bytes, include_bfa=include_bfa)

        # Merge fragment identification and label
        row = {
            "fragment_id": item["fragment_id"],
            "source_file": item["source_file"],
            "file_type": item["file_type"],
            "is_header": int(item.get("is_header", False)),
            "is_footer": int(item.get("is_footer", False)),
            "fragment_index": item.get("fragment_index", 0),
            **features,
        }
        dataset_rows.append(row)

        if (idx + 1) % 100 == 0 or (idx + 1) == len(fragments):
            print(f"  Processed {idx + 1}/{len(fragments)} fragments")

    if dataset_rows:
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(dataset_rows[0].keys())
        with open(output_csv_path, "w", newline="", encoding="utf-8") as cf:
            writer = csv.DictWriter(cf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(dataset_rows)

        print(f"[+] Successfully extracted features and saved to {output_csv_path}")
        print(f"  Total Samples: {len(dataset_rows)}")
        print(f"  Total Features: {len(fieldnames) - 6} (excluding labels & IDs)")
    else:
        print("[!] No fragments processed.")


def main():
    parser = argparse.ArgumentParser(
        description="ReFrag AI - Forensic Byte-Level Feature Extractor"
    )
    parser.add_argument(
        "--fragments-dir",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "data" / "fragments"),
        help="Directory with raw binary fragments (default: ml/data/fragments)",
    )
    parser.add_argument(
        "--metadata-path",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "data" / "fragments_metadata.json"),
        help="Path to fragments metadata JSON (default: ml/data/fragments_metadata.json)",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default=str(Path(__file__).resolve().parent / "extracted_features.csv"),
        help="Output CSV path for extracted features (default: ml/features/extracted_features.csv)",
    )
    parser.add_argument(
        "--no-bfa",
        action="store_true",
        help="Disable 256-byte frequency distribution histogram features",
    )

    args = parser.parse_args()

    fragments_dir = Path(args.fragments_dir)
    metadata_path = Path(args.metadata_path)
    output_csv_path = Path(args.output_csv)

    extract_dataset_features(
        fragments_dir=fragments_dir,
        metadata_path=metadata_path,
        output_csv_path=output_csv_path,
        include_bfa=not args.no_bfa,
    )


if __name__ == "__main__":
    main()
