"""
ReFrag AI - Live Recovery Engine

Runs the trained ReFrag AI models on an uploaded file.

Pipeline:
    raw bytes
        ↓
    fragment generation
        ↓
    feature extraction
        ↓
    fragment classification
        ↓
    relationship analysis
        ↓
    reconstruction candidate
        ↓
    integrity analysis
        ↓
    evidence prioritization
"""

from __future__ import annotations

import sys
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ============================================================
# PYTHON PATH
# ============================================================

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================
# REFRAG AI MODULE
# ============================================================

from features.extract_features import extract_features_from_bytes


# ============================================================
# MODEL PATHS
# ============================================================

SAVED_DIR = ROOT / "saved"

CLASSIFIER_PATH = SAVED_DIR / "fragment_classifier.joblib"
LABEL_ENCODER_PATH = SAVED_DIR / "label_encoder.joblib"
CLASSIFIER_META_PATH = SAVED_DIR / "model_metadata.json"

RELATIONSHIP_PATH = SAVED_DIR / "relationship_model.joblib"
RELATIONSHIP_META_PATH = SAVED_DIR / "relationship_model_metadata.json"


# ============================================================
# MODEL LOADING
# ============================================================

def load_models():

    classifier = joblib.load(CLASSIFIER_PATH)

    label_encoder = joblib.load(LABEL_ENCODER_PATH)

    relationship_model = joblib.load(RELATIONSHIP_PATH)

    with open(
        CLASSIFIER_META_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        classifier_meta = json.load(file)

    with open(
        RELATIONSHIP_META_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        relationship_meta = json.load(file)

    return (
        classifier,
        label_encoder,
        classifier_meta,
        relationship_model,
        relationship_meta,
    )


# ============================================================
# ENTROPY
# ============================================================

def entropy(data: bytes) -> float:

    if not data:
        return 0.0

    values = np.frombuffer(
        data,
        dtype=np.uint8,
    )

    counts = np.bincount(
        values,
        minlength=256,
    )

    probabilities = counts[counts > 0] / len(data)

    return float(
        -np.sum(
            probabilities * np.log2(probabilities)
        )
    )


# ============================================================
# FILE TYPE DETECTION
# ============================================================

def detect_file_type(data: bytes) -> str:

    if data.startswith(b"\xff\xd8\xff"):
        return "JPEG"

    if data.startswith(
        b"\x89PNG\r\n\x1a\n"
    ):
        return "PNG"

    if data.startswith(b"%PDF"):
        return "PDF"

    if data.startswith(b"PK"):
        return "ZIP"

    if (
        data.startswith(b"GIF87a")
        or data.startswith(b"GIF89a")
    ):
        return "GIF"

    return "UNKNOWN"


# ============================================================
# INTEGRITY ANALYSIS
# ============================================================

def check_integrity(
    file_type: str,
    data: bytes,
) -> tuple[str, str]:

    if not data:
        return (
            "CORRUPTED",
            "No data available.",
        )

    # --------------------------------------------------------
    # JPEG
    # --------------------------------------------------------

    if file_type == "JPEG":

        if (
            data.startswith(b"\xff\xd8\xff")
            and data.endswith(b"\xff\xd9")
        ):
            return (
                "VALID",
                "JPEG header and EOI marker detected.",
            )

        return (
            "PARTIAL",
            "JPEG header detected but EOI marker is missing.",
        )

    # --------------------------------------------------------
    # PNG
    # --------------------------------------------------------

    if file_type == "PNG":

        if (
            data.startswith(
                b"\x89PNG\r\n\x1a\n"
            )
            and data.endswith(
                b"IEND\xaeB`\x82"
            )
        ):
            return (
                "VALID",
                "PNG signature and IEND marker detected.",
            )

        return (
            "PARTIAL",
            "PNG signature detected but IEND marker is missing.",
        )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if file_type == "PDF":

        if (
            data.startswith(b"%PDF")
            and b"%%EOF" in data[-1024:]
        ):
            return (
                "VALID",
                "PDF header and EOF marker detected.",
            )

        return (
            "PARTIAL",
            "PDF header detected but EOF marker is missing.",
        )

    # --------------------------------------------------------
    # ZIP
    # --------------------------------------------------------

    if file_type == "ZIP":

        if (
            data.startswith(b"PK")
            and (
                b"PK\x05\x06" in data[-1024:]
                or b"PK\x01\x02" in data[-1024:]
            )
        ):
            return (
                "VALID",
                "ZIP header and archive marker detected.",
            )

        return (
            "PARTIAL",
            "ZIP signature detected but archive termination is incomplete.",
        )

    return (
        "UNKNOWN",
        "File format could not be structurally validated.",
    )


# ============================================================
# FRAGMENT GENERATION
# ============================================================

def create_fragments(
    data: bytes,
    fragment_size: int = 4096,
):

    fragments = []

    for offset in range(
        0,
        len(data),
        fragment_size,
    ):

        chunk = data[
            offset:
            offset + fragment_size
        ]

        fragments.append(
            {
                "index": len(fragments),
                "offset": offset,
                "size": len(chunk),
                "bytes": chunk,
            }
        )

    return fragments


# ============================================================
# FRAGMENT CLASSIFICATION
# ============================================================

def classify_fragments(
    fragments,
    classifier,
    label_encoder,
    metadata,
):

    feature_columns = metadata.get(
        "features",
        metadata.get(
            "feature_columns",
            [],
        ),
    )

    results = []

    for fragment in fragments:

        features = extract_features_from_bytes(
            fragment["bytes"],
            include_bfa=True,
        )

        frame = pd.DataFrame(
            [features]
        )

        # Match training feature order exactly.
        if feature_columns:

            for column in feature_columns:

                if column not in frame.columns:
                    frame[column] = 0.0

            frame = frame[
                feature_columns
            ]

        probabilities = classifier.predict_proba(
            frame
        )[0]

        predicted_index = int(
            np.argmax(probabilities)
        )

        predicted_label = (
            label_encoder.inverse_transform(
                [predicted_index]
            )[0]
        )

        confidence = float(
            probabilities[predicted_index]
        )

        results.append(
            {
                "index": fragment["index"],
                "offset": fragment["offset"],
                "size": fragment["size"],
                "entropy": round(
                    entropy(fragment["bytes"]),
                    4,
                ),
                "predicted_type": str(
                    predicted_label
                ).upper(),
                "classification_confidence": round(
                    confidence,
                    4,
                ),
                "features": features,
            }
        )

    return results


# ============================================================
# RELATIONSHIP FEATURE HELPERS
# ============================================================

def compute_bfa_distances(
    bfa_a,
    bfa_b,
):

    norm_a = np.linalg.norm(bfa_a)
    norm_b = np.linalg.norm(bfa_b)

    if norm_a > 0 and norm_b > 0:

        cosine_sim = float(
            np.dot(bfa_a, bfa_b)
            / (norm_a * norm_b)
        )

    else:
        cosine_sim = 0.0

    euclidean_dist = float(
        np.linalg.norm(
            bfa_a - bfa_b
        )
    )

    manhattan_dist = float(
        np.sum(
            np.abs(
                bfa_a - bfa_b
            )
        )
    )

    std_a = np.std(bfa_a)
    std_b = np.std(bfa_b)

    if std_a > 0 and std_b > 0:

        correlation = float(
            np.corrcoef(
                bfa_a,
                bfa_b,
            )[0, 1]
        )

    else:
        correlation = 0.0

    return {
        "bfa_cosine_sim": round(
            cosine_sim,
            5,
        ),
        "bfa_euclidean_dist": round(
            euclidean_dist,
            5,
        ),
        "bfa_manhattan_dist": round(
            manhattan_dist,
            5,
        ),
        "bfa_correlation": round(
            correlation,
            5,
        ),
    }


def compute_seam_features(
    bytes_a: bytes,
    bytes_b: bytes,
):

    if not bytes_a or not bytes_b:

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

    seam_byte_diff = abs(
        tail_byte - head_byte
    )

    seam_identical = int(
        tail_byte == head_byte
    )

    seam_both_null = int(
        tail_byte == 0
        and head_byte == 0
    )

    printable_set = set(
        b"abcdefghijklmnopqrstuvwxyz"
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        b"0123456789"
        b"!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ "
        b"\t\r\n"
    )

    seam_both_printable = int(
        tail_byte in printable_set
        and head_byte in printable_set
    )

    k4 = min(
        4,
        len(bytes_a),
        len(bytes_b),
    )

    diff_4 = sum(
        abs(
            bytes_a[-i]
            - bytes_b[i - 1]
        )
        for i in range(1, k4 + 1)
    ) / k4

    k16 = min(
        16,
        len(bytes_a),
        len(bytes_b),
    )

    diff_16 = sum(
        abs(
            bytes_a[-i]
            - bytes_b[i - 1]
        )
        for i in range(1, k16 + 1)
    ) / k16

    return {
        "seam_byte_diff": float(
            seam_byte_diff
        ),
        "seam_avg_diff_4": round(
            diff_4,
            4,
        ),
        "seam_avg_diff_16": round(
            diff_16,
            4,
        ),
        "seam_both_null": seam_both_null,
        "seam_both_printable": seam_both_printable,
        "seam_identical": seam_identical,
    }


# ============================================================
# LIVE RELATIONSHIP FEATURES
# ============================================================

def build_relationship_features(
    fragment_a,
    fragment_b,
    index_distance,
):

    bytes_a = fragment_a["bytes"]
    bytes_b = fragment_b["bytes"]

    features_a = fragment_a["features"]
    features_b = fragment_b["features"]

    # --------------------------------------------------------
    # Byte frequency analysis
    # --------------------------------------------------------

    bfa_a = np.array(
        [
            features_a[
                f"byte_freq_{i:02x}"
            ]
            for i in range(256)
        ],
        dtype=float,
    )

    bfa_b = np.array(
        [
            features_b[
                f"byte_freq_{i:02x}"
            ]
            for i in range(256)
        ],
        dtype=float,
    )

    bfa = compute_bfa_distances(
        bfa_a,
        bfa_b,
    )

    # --------------------------------------------------------
    # Boundary seam analysis
    # --------------------------------------------------------

    seam = compute_seam_features(
        bytes_a,
        bytes_b,
    )

    # --------------------------------------------------------
    # Predicted file types
    # --------------------------------------------------------

    type_a = fragment_a[
        "predicted_type"
    ]

    type_b = fragment_b[
        "predicted_type"
    ]

    same_file_type = int(
        type_a == type_b
    )

    # --------------------------------------------------------
    # Relationship feature vector
    # --------------------------------------------------------

    return {

        # Seam
        **seam,

        # Byte-frequency distances
        **bfa,

        # Statistical consistency
        "diff_entropy": abs(
            features_a["entropy"]
            - features_b["entropy"]
        ),

        "avg_entropy": (
            features_a["entropy"]
            + features_b["entropy"]
        ) / 2.0,

        "diff_mean": abs(
            features_a["mean"]
            - features_b["mean"]
        ),

        "diff_std": abs(
            features_a["std"]
            - features_b["std"]
        ),

        "diff_variance": abs(
            features_a["variance"]
            - features_b["variance"]
        ),

        "diff_printable": abs(
            features_a["printable_ratio"]
            - features_b["printable_ratio"]
        ),

        "diff_null": abs(
            features_a["null_ratio"]
            - features_b["null_ratio"]
        ),

        "diff_high_byte": abs(
            features_a["high_byte_ratio"]
            - features_b["high_byte_ratio"]
        ),

        "diff_control": abs(
            features_a["control_ratio"]
            - features_b["control_ratio"]
        ),

        "diff_max_consecutive": abs(
            features_a["max_consecutive"]
            - features_b["max_consecutive"]
        ),

        # File-type relationship
        "same_file_type": same_file_type,

        # Fragment ordering
        "index_distance": index_distance,

        # Structural markers
        "is_header_a": int(
            features_a.get(
                "has_magic_header",
                0,
            )
        ),

        "is_footer_b": int(
            features_b.get(
                "has_magic_footer",
                0,
            )
        ),

        "has_magic_header_a": int(
            features_a.get(
                "has_magic_header",
                0,
            )
        ),

        "has_magic_footer_b": int(
            features_b.get(
                "has_magic_footer",
                0,
            )
        ),

        "invalid_boundary": int(
            features_a.get(
                "has_magic_footer",
                0,
            ) == 1
            or
            features_b.get(
                "has_magic_header",
                0,
            ) == 1
        ),
    }


# ============================================================
# RELATIONSHIP ANALYSIS
# ============================================================

def analyze_relationships(
    fragments,
    relationship_model,
    metadata,
):

    feature_columns = metadata.get(
        "features",
        metadata.get(
            "feature_columns",
            [],
        ),
    )

    relationships = []

    # Analyze neighboring fragments.
    for i in range(
        len(fragments) - 1
    ):

        a = fragments[i]
        b = fragments[i + 1]

        pair_features = build_relationship_features(
            a,
            b,
            index_distance=1,
        )

        frame = pd.DataFrame(
            [pair_features]
        )

        # Match relationship model's
        # training feature order.
        if feature_columns:

            for column in feature_columns:

                if column not in frame.columns:
                    frame[column] = 0.0

            frame = frame[
                feature_columns
            ]

        probability = float(
            relationship_model.predict_proba(
                frame
            )[0][1]
        )

        relationships.append(
            {
                "fragment_a": a["index"],
                "fragment_b": b["index"],
                "relationship_probability": round(
                    probability,
                    4,
                ),
                "same_file_type": pair_features[
                    "same_file_type"
                ],
            }
        )

    return relationships


# ============================================================
# RECONSTRUCTION
# ============================================================

def build_reconstruction(
    fragments,
    relationships,
    threshold=0.80,
):

    if not fragments:
        return None

    selected = [
        fragments[0]
    ]

    probabilities = []

    for relationship in relationships:

        probability = relationship[
            "relationship_probability"
        ]

        if probability >= threshold:

            index_b = relationship[
                "fragment_b"
            ]

            selected.append(
                fragments[index_b]
            )

            probabilities.append(
                probability
            )

        else:
            break

    if probabilities:

        confidence = float(
            np.mean(probabilities)
        )

    else:
        confidence = 0.0

    reconstructed = b"".join(
        fragment["bytes"]
        for fragment in selected
    )

    return {
        "fragment_count": len(
            selected
        ),
        "confidence": round(
            confidence,
            4,
        ),
        "data": reconstructed,
        "relationships_used": len(
            probabilities
        ),
    }


# ============================================================
# PRIORITY
# ============================================================

def calculate_priority(
    integrity,
    reconstruction_confidence,
    fragment_count,
):

    integrity_scores = {
        "VALID": 1.0,
        "PARTIAL": 0.5,
        "CORRUPTED": 0.1,
        "UNKNOWN": 0.0,
    }

    integrity_score = (
        integrity_scores.get(
            integrity,
            0.0,
        )
        * 100
    )

    reconstruction_score = (
        reconstruction_confidence
        * 100
    )

    fragment_score = (
        min(
            fragment_count,
            20,
        )
        / 20
        * 100
    )

    score = (
        integrity_score * 0.60
        + reconstruction_score * 0.30
        + fragment_score * 0.10
    )

    if score >= 85:
        priority = "HIGH"

    elif score >= 60:
        priority = "MEDIUM"

    else:
        priority = "LOW"

    return (
        round(score, 2),
        priority,
    )


# ============================================================
# MAIN LIVE ANALYSIS
# ============================================================

def analyze_bytes(
    data: bytes,
    fragment_size: int = 4096,
    relationship_threshold: float = 0.80,
):

    if not data:
        raise ValueError(
            "Uploaded file contains no data."
        )

    # --------------------------------------------------------
    # Load trained models
    # --------------------------------------------------------

    (
        classifier,
        label_encoder,
        classifier_meta,
        relationship_model,
        relationship_meta,
    ) = load_models()

    # --------------------------------------------------------
    # Detect file
    # --------------------------------------------------------

    file_type = detect_file_type(
        data
    )

    # --------------------------------------------------------
    # Generate fragments
    # --------------------------------------------------------

    fragments = create_fragments(
        data,
        fragment_size,
    )

    # --------------------------------------------------------
    # ML fragment classification
    # --------------------------------------------------------

    classified = classify_fragments(
        fragments,
        classifier,
        label_encoder,
        classifier_meta,
    )

    # Attach raw bytes internally.
    for original, classified_fragment in zip(
        fragments,
        classified,
    ):

        classified_fragment["bytes"] = (
            original["bytes"]
        )

    # --------------------------------------------------------
    # Relationship model
    # --------------------------------------------------------

    relationships = analyze_relationships(
        classified,
        relationship_model,
        relationship_meta,
    )

    # --------------------------------------------------------
    # Reconstruction candidate
    # --------------------------------------------------------

    reconstruction = build_reconstruction(
        classified,
        relationships,
        relationship_threshold,
    )

    # --------------------------------------------------------
    # Integrity
    # --------------------------------------------------------

    integrity, integrity_reason = (
        check_integrity(
            file_type,
            data,
        )
    )

    if reconstruction:

        reconstruction_confidence = (
            reconstruction["confidence"]
        )

    else:

        reconstruction_confidence = 0.0

    # --------------------------------------------------------
    # Evidence priority
    # --------------------------------------------------------

    priority_score, priority = (
        calculate_priority(
            integrity,
            reconstruction_confidence,
            len(fragments),
        )
    )

    # --------------------------------------------------------
    # Clean fragment response
    # --------------------------------------------------------

    clean_fragments = []

    for fragment in classified:

        clean_fragments.append(
            {
                "fragment_id":
                    fragment["index"] + 1,

                "offset":
                    fragment["offset"],

                "size":
                    fragment["size"],

                "entropy":
                    fragment["entropy"],

                "predicted_type":
                    fragment["predicted_type"],

                "classification_confidence":
                    fragment[
                        "classification_confidence"
                    ],
            }
        )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {

        "file_type":
            file_type,

        "fragment_count":
            len(fragments),

        "fragment_size":
            fragment_size,

        "entropy":
            round(
                entropy(data),
                4,
            ),

        "integrity":
            integrity,

        "integrity_reason":
            integrity_reason,

        "reconstruction_confidence":
            reconstruction_confidence,

        "reconstruction_fragment_count":
            (
                reconstruction[
                    "fragment_count"
                ]
                if reconstruction
                else 0
            ),

        "relationships_analyzed":
            len(relationships),

        "strong_relationships":
            sum(
                1
                for relationship in relationships
                if relationship[
                    "relationship_probability"
                ] >= relationship_threshold
            ),

        "priority_score":
            priority_score,

        "priority":
            priority,

        "fragments":
            clean_fragments,

        "relationships":
            relationships,
    }