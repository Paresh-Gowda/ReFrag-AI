"""
ReFrag AI
Visual Image Recovery Pipeline

Pipeline:

    BROKEN IMAGE
         ↓
    VISUAL FEATURE EXTRACTION
         ↓
    REFERENCE DATABASE SEARCH
         ↓
    BEST REFERENCE MATCH
         ↓
    DAMAGE ANALYSIS
         ↓
    EVIDENCE CLASSIFICATION
         ↓
    REFERENCE-ASSISTED RESTORATION
         ↓
    OUTPUT ARTIFACTS

Important forensic distinction:

DIRECT INPUT EVIDENCE
    Pixels directly supported by the uploaded image.

REFERENCE DIFFERENCE
    Pixels that differ from the matched reference.

REFERENCE-ASSISTED
    Pixels replaced/inferred using the matched reference.

The restoration output is therefore NOT treated as direct recovery.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np


# ============================================================
# PATHS
# ============================================================

IMAGE_RECOVERY_DIR = Path(__file__).resolve().parent

BASE = (
    IMAGE_RECOVERY_DIR
    / "reference_database"
)

CLEAN_DIR = BASE / "clean"
BROKEN_DIR = BASE / "broken"

FEATURE_INDEX = (
    BASE
    / "feature_index.json"
)

OUTPUT_DIR = (
    IMAGE_RECOVERY_DIR
    / "test"
    / "output"
    / "api_recovery"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# CONFIGURATION
# ============================================================

FEATURE_SIZE = 32

REFERENCE_MATCH_THRESHOLD = 0.70

DAMAGE_THRESHOLD = 30

MORPH_KERNEL_SIZE = 3

TOP_MATCHES = 5


# ============================================================
# IMAGE LOADING
# ============================================================

def load_image(path: Path):
    """
    Load an image using OpenCV.
    """

    image = cv2.imread(
        str(path),
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise FileNotFoundError(
            f"Unable to read image:\n{path}"
        )

    return image


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def extract_features(image):
    """
    Extract a compact visual descriptor.

    Components:

    1. HSV histogram
    2. LAB resized image
    3. Canny edge map

    These features are designed for controlled
    reference-image retrieval.
    """

    # --------------------------------------------------------
    # HSV COLOR HISTOGRAM
    # --------------------------------------------------------

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV,
    )

    histogram = cv2.calcHist(
        [hsv],
        [0, 1],
        None,
        [32, 32],
        [0, 180, 0, 256],
    )

    histogram = cv2.normalize(
        histogram,
        histogram,
    ).flatten()


    # --------------------------------------------------------
    # LAB STRUCTURE
    # --------------------------------------------------------

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB,
    )

    lab_small = cv2.resize(
        lab,
        (
            FEATURE_SIZE,
            FEATURE_SIZE,
        ),
        interpolation=cv2.INTER_AREA,
    )

    lab_features = (
        lab_small
        .astype(np.float32)
        .flatten()
        / 255.0
    )


    # --------------------------------------------------------
    # EDGE STRUCTURE
    # --------------------------------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    edges = cv2.Canny(
        gray,
        80,
        160,
    )

    edges_small = cv2.resize(
        edges,
        (
            FEATURE_SIZE,
            FEATURE_SIZE,
        ),
        interpolation=cv2.INTER_AREA,
    )

    edge_features = (
        edges_small
        .astype(np.float32)
        .flatten()
        / 255.0
    )


    # --------------------------------------------------------
    # COMBINE
    # --------------------------------------------------------

    feature_vector = np.concatenate(
        [
            histogram.astype(np.float32),
            lab_features,
            edge_features,
        ]
    )

    return feature_vector


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(a, b):
    """
    Calculate cosine similarity.
    """

    a = np.asarray(
        a,
        dtype=np.float32,
    )

    b = np.asarray(
        b,
        dtype=np.float32,
    )

    denominator = (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(a, b)
        / denominator
    )


# ============================================================
# BUILD REFERENCE INDEX
# ============================================================

def build_reference_index():
    """
    Build feature_index.json from the 100 clean images.
    """

    CLEAN_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_paths = sorted(
        [
            path
            for path in CLEAN_DIR.iterdir()
            if path.suffix.lower()
            in {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
            }
        ]
    )

    if not image_paths:
        raise RuntimeError(
            f"No reference images found in:\n{CLEAN_DIR}"
        )

    print()
    print("=" * 65)
    print("REFRAG AI — BUILDING VISUAL REFERENCE INDEX")
    print("=" * 65)

    records = []

    for index, image_path in enumerate(
        image_paths,
        start=1,
    ):

        print(
            f"[{index:03d}/{len(image_paths):03d}] "
            f"{image_path.name}"
        )

        image = load_image(
            image_path
        )

        features = extract_features(
            image
        )

        records.append(
            {
                "id": image_path.stem.replace(
                    "_clean",
                    "",
                ),
                "filename": image_path.name,
                "path": str(
                    image_path.resolve()
                ),
                "features": features.tolist(),
            }
        )

    with open(
        FEATURE_INDEX,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                "version": 1,
                "feature_size": int(
                    len(records[0]["features"])
                ),
                "images": records,
            },
            file,
            indent=2,
        )

    print()
    print("=" * 65)
    print("REFERENCE INDEX CREATED")
    print("=" * 65)

    print(
        f"Images : {len(records)}"
    )

    print(
        f"Index  : {FEATURE_INDEX}"
    )

    return records


# ============================================================
# LOAD REFERENCE INDEX
# ============================================================

def load_reference_index():
    """
    Load feature index.

    If it does not exist, build it automatically.
    """

    if not FEATURE_INDEX.exists():

        print(
            "Reference index not found."
        )

        print(
            "Building reference index..."
        )

        return build_reference_index()

    with open(
        FEATURE_INDEX,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    images = data.get(
        "images",
        [],
    )

    if not images:
        raise RuntimeError(
            "Reference index contains no images."
        )

    return images


# ============================================================
# REFERENCE SEARCH
# ============================================================

def search_references(
    image,
    top_k=TOP_MATCHES,
):
    """
    Search the reference database using
    visual feature similarity.
    """

    query_features = extract_features(
        image
    )

    references = load_reference_index()

    matches = []

    for reference in references:

        reference_features = np.asarray(
            reference["features"],
            dtype=np.float32,
        )

        similarity = cosine_similarity(
            query_features,
            reference_features,
        )

        matches.append(
            {
                "id": reference["id"],
                "filename": reference["filename"],
                "path": reference["path"],
                "similarity": similarity,
                "similarity_percent": round(
                    similarity * 100,
                    2,
                ),
            }
        )

    matches.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )

    return matches[:top_k]


# ============================================================
# RESIZE REFERENCE
# ============================================================

def prepare_reference(
    reference,
    target_shape,
):
    """
    Resize reference to match uploaded image dimensions.
    """

    height = target_shape[0]
    width = target_shape[1]

    return cv2.resize(
        reference,
        (
            width,
            height,
        ),
        interpolation=cv2.INTER_AREA,
    )


# ============================================================
# DAMAGE ANALYSIS
# ============================================================

def analyze_damage(
    broken,
    reference,
):
    """
    Compare uploaded image with matched reference.

    NOTE:
    This is controlled reference-difference analysis.

    A difference does not independently prove that
    information was deleted or corrupted.
    """

    reference = prepare_reference(
        reference,
        broken.shape,
    )

    difference = cv2.absdiff(
        broken,
        reference,
    )

    difference_gray = cv2.cvtColor(
        difference,
        cv2.COLOR_BGR2GRAY,
    )

    _, mask = cv2.threshold(
        difference_gray,
        DAMAGE_THRESHOLD,
        255,
        cv2.THRESH_BINARY,
    )

    kernel = np.ones(
        (
            MORPH_KERNEL_SIZE,
            MORPH_KERNEL_SIZE,
        ),
        np.uint8,
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel,
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel,
    )

    # --------------------------------------------------------
    # PIXEL COUNTS
    # --------------------------------------------------------

    total_pixels = int(
        mask.shape[0]
        * mask.shape[1]
    )

    damaged_pixels = int(
        np.count_nonzero(mask)
    )

    preserved_pixels = (
        total_pixels
        - damaged_pixels
    )

    recovered_percent = (
        preserved_pixels
        / total_pixels
        * 100
        if total_pixels
        else 0
    )

    damaged_percent = (
        damaged_pixels
        / total_pixels
        * 100
        if total_pixels
        else 0
    )


    # --------------------------------------------------------
    # CONNECTED COMPONENTS
    # --------------------------------------------------------

    count, labels, stats, centroids = (
        cv2.connectedComponentsWithStats(
            mask,
            connectivity=8,
        )
    )

    regions = []

    for component_id in range(
        1,
        count,
    ):

        x = int(
            stats[
                component_id,
                cv2.CC_STAT_LEFT,
            ]
        )

        y = int(
            stats[
                component_id,
                cv2.CC_STAT_TOP,
            ]
        )

        width = int(
            stats[
                component_id,
                cv2.CC_STAT_WIDTH,
            ]
        )

        height = int(
            stats[
                component_id,
                cv2.CC_STAT_HEIGHT,
            ]
        )

        area = int(
            stats[
                component_id,
                cv2.CC_STAT_AREA,
            ]
        )

        if area < 20:
            continue

        regions.append(
            {
                "region_id": len(regions) + 1,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "area_pixels": area,
                "area_percent": round(
                    area
                    / total_pixels
                    * 100,
                    3,
                ),
                "centroid_x": round(
                    float(
                        centroids[
                            component_id,
                            0,
                        ]
                    ),
                    2,
                ),
                "centroid_y": round(
                    float(
                        centroids[
                            component_id,
                            1,
                        ]
                    ),
                    2,
                ),
            }
        )


    # --------------------------------------------------------
    # EVIDENCE MAP
    # --------------------------------------------------------

    evidence_map = broken.copy()

    damaged_mask = (
        mask > 0
    )

    # Draw detected damage boundaries.
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    cv2.drawContours(
        evidence_map,
        contours,
        -1,
        (0, 0, 255),
        2,
    )


    # --------------------------------------------------------
    # RESTORATION
    # --------------------------------------------------------

    restored = broken.copy()

    restored[
        damaged_mask
    ] = reference[
        damaged_mask
    ]


    return {
        "reference": reference,
        "mask": mask,
        "evidence_map": evidence_map,
        "restored": restored,
        "total_pixels": total_pixels,
        "preserved_pixels": preserved_pixels,
        "damaged_pixels": damaged_pixels,
        "recovered_percent": round(
            recovered_percent,
            2,
        ),
        "damaged_percent": round(
            damaged_percent,
            2,
        ),
        "damage_regions": len(
            regions
        ),
        "regions": regions,
    }


# ============================================================
# SAVE OUTPUTS
# ============================================================

def save_outputs(
    broken,
    reference,
    mask,
    evidence_map,
    restored,
    analysis,
):
    """
    Save all visual-recovery artifacts.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    # --------------------------------------------------------
    # REFERENCE
    # --------------------------------------------------------

    reference_path = (
        OUTPUT_DIR
        / "reference.jpg"
    )

    if not cv2.imwrite(
        str(reference_path),
        reference,
    ):
        raise RuntimeError(
            "Failed to save reference image."
        )


    # --------------------------------------------------------
    # INPUT COPY
    # --------------------------------------------------------

    input_path = (
        OUTPUT_DIR
        / "input_image.jpg"
    )

    cv2.imwrite(
        str(input_path),
        broken,
    )


    # --------------------------------------------------------
    # DAMAGE MASK
    # --------------------------------------------------------

    damage_mask_path = (
        OUTPUT_DIR
        / "damage_mask.png"
    )

    cv2.imwrite(
        str(damage_mask_path),
        mask,
    )


    # --------------------------------------------------------
    # EVIDENCE MAP
    # --------------------------------------------------------

    evidence_map_path = (
        OUTPUT_DIR
        / "evidence_map.png"
    )

    cv2.imwrite(
        str(evidence_map_path),
        evidence_map,
    )


    # --------------------------------------------------------
    # RESTORED IMAGE
    # --------------------------------------------------------

    restored_path = (
        OUTPUT_DIR
        / "restored_image.png"
    )

    cv2.imwrite(
        str(restored_path),
        restored,
    )


    # --------------------------------------------------------
    # JSON REPORT
    # --------------------------------------------------------

    result_json_path = (
        OUTPUT_DIR
        / "visual_recovery_result.json"
    )

    with open(
        result_json_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                "analysis": analysis,
                "outputs": {
                    "input_image":
                        "/api/image-recovery/output/input_image.jpg",

                    "reference_image":
                        "/api/image-recovery/output/reference.jpg",

                    "damage_mask":
                        "/api/image-recovery/output/damage_mask.png",

                    "evidence_map":
                        "/api/image-recovery/output/evidence_map.png",

                    "restored_image":
                        "/api/image-recovery/output/restored_image.png",
                },
            },
            file,
            indent=2,
        )


    return {
        "input_image":
            "/api/image-recovery/output/input_image.jpg",

        "reference_image":
            "/api/image-recovery/output/reference.jpg",

        "damage_mask":
            "/api/image-recovery/output/damage_mask.png",

        "evidence_map":
            "/api/image-recovery/output/evidence_map.png",

        "restored_image":
            "/api/image-recovery/output/restored_image.png",

        "result_json":
            "/api/image-recovery/output/visual_recovery_result.json",
    }


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_visual_recovery(
    input_path,
):
    """
    Complete visual recovery pipeline.

    Parameters
    ----------
    input_path : str | Path
        Uploaded/broken image.

    Returns
    -------
    dict
        JSON-safe recovery result.
    """

    input_path = Path(
        input_path
    ).resolve()

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input image not found:\n{input_path}"
        )


    print()
    print("=" * 65)
    print("REFRAG AI — VISUAL RECOVERY")
    print("=" * 65)

    print(
        f"Input : {input_path.name}"
    )


    # --------------------------------------------------------
    # LOAD INPUT
    # --------------------------------------------------------

    broken = load_image(
        input_path
    )

    print(
        f"Size  : "
        f"{broken.shape[1]} x "
        f"{broken.shape[0]}"
    )


    # --------------------------------------------------------
    # REFERENCE SEARCH
    # --------------------------------------------------------

    matches = search_references(
        broken,
        top_k=TOP_MATCHES,
    )

    if not matches:
        raise RuntimeError(
            "No reference images available."
        )

    best = matches[0]

    print()
    print("REFERENCE MATCH")
    print(
        f"Reference  : "
        f"{best['filename']}"
    )

    print(
        f"Similarity : "
        f"{best['similarity_percent']:.2f}%"
    )


    # --------------------------------------------------------
    # RELIABILITY CHECK
    # --------------------------------------------------------

    reference_reliable = (
        best["similarity"]
        >= REFERENCE_MATCH_THRESHOLD
    )

    if not reference_reliable:

        print()
        print(
            "WARNING: reference similarity "
            "is below the reliability threshold."
        )


    # --------------------------------------------------------
    # LOAD REFERENCE
    # --------------------------------------------------------

    reference_path = Path(
        best["path"]
    )

    if not reference_path.exists():

        reference_path = (
            CLEAN_DIR
            / best["filename"]
        )

    reference = load_image(
        reference_path
    )


    # --------------------------------------------------------
    # DAMAGE ANALYSIS
    # --------------------------------------------------------

    damage = analyze_damage(
        broken,
        reference,
    )


    print()
    print("DAMAGE ANALYSIS")

    print(
        f"Total pixels : "
        f"{damage['total_pixels']:,}"
    )

    print(
        f"Preserved    : "
        f"{damage['preserved_pixels']:,}"
    )

    print(
        f"Damaged      : "
        f"{damage['damaged_pixels']:,}"
    )

    print(
        f"Recovered    : "
        f"{damage['recovered_percent']:.2f}%"
    )

    print(
        f"Damaged      : "
        f"{damage['damaged_percent']:.2f}%"
    )

    print(
        f"Regions      : "
        f"{damage['damage_regions']}"
    )


    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    evidence = {
        "preserved_content":
            "DIRECT_INPUT_EVIDENCE",

        "damaged_content":
            "DIFFERENCE_FROM_REFERENCE",

        "restored_content":
            "REFERENCE_ASSISTED",
    }


    # --------------------------------------------------------
    # ANALYSIS RECORD
    # --------------------------------------------------------

    analysis = {
        "total_pixels":
            damage["total_pixels"],

        "preserved_pixels":
            damage["preserved_pixels"],

        "damaged_pixels":
            damage["damaged_pixels"],

        "recovered_percent":
            damage["recovered_percent"],

        "damaged_percent":
            damage["damaged_percent"],

        "damage_regions":
            damage["damage_regions"],

        "regions":
            damage["regions"],

        "reference_reliable":
            reference_reliable,

        "damage_threshold":
            DAMAGE_THRESHOLD,
    }


    # --------------------------------------------------------
    # SAVE ARTIFACTS
    # --------------------------------------------------------

    outputs = save_outputs(
        broken=broken,
        reference=damage["reference"],
        mask=damage["mask"],
        evidence_map=damage["evidence_map"],
        restored=damage["restored"],
        analysis=analysis,
    )


    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    result = {
        "input": {
            "filename":
                input_path.name,

            "path":
                str(input_path),

            "width":
                int(broken.shape[1]),

            "height":
                int(broken.shape[0]),
        },

        "reference_match": {
            "reference_id":
                best["id"],

            "reference_filename":
                best["filename"],

            "similarity":
                round(
                    best["similarity"],
                    4,
                ),

            "similarity_percent":
                best["similarity_percent"],

            "reliable":
                reference_reliable,
        },

        "top_matches": [
            {
                "id":
                    match["id"],

                "filename":
                    match["filename"],

                "similarity":
                    round(
                        match["similarity"],
                        4,
                    ),

                "similarity_percent":
                    match["similarity_percent"],
            }

            for match in matches
        ],

        "damage_analysis": {
            "total_pixels":
                damage["total_pixels"],

            "preserved_pixels":
                damage["preserved_pixels"],

            "damaged_pixels":
                damage["damaged_pixels"],

            "recovered_percent":
                damage["recovered_percent"],

            "damaged_percent":
                damage["damaged_percent"],

            "damage_regions":
                damage["damage_regions"],

            "regions":
                damage["regions"],
        },

        "evidence":
            evidence,

        "outputs":
            outputs,
    }


    print()
    print("EVIDENCE")

    print(
        "  PRESERVED → "
        "DIRECT INPUT EVIDENCE"
    )

    print(
        "  DAMAGED   → "
        "REFERENCE DIFFERENCE"
    )

    print(
        "  RESTORED  → "
        "REFERENCE ASSISTED"
    )


    print()
    print("OUTPUTS")

    print(
        f"  Reference   : "
        f"{reference_path}"
    )

    print(
        f"  Damage mask : "
        f"{OUTPUT_DIR / 'damage_mask.png'}"
    )

    print(
        f"  Evidence    : "
        f"{OUTPUT_DIR / 'evidence_map.png'}"
    )

    print(
        f"  Restored    : "
        f"{OUTPUT_DIR / 'restored_image.png'}"
    )

    print()
    print("=" * 65)
    print("VISUAL RECOVERY COMPLETE")
    print("=" * 65)

    return result


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

def analyze_image(
    input_path,
):
    """
    Compatibility wrapper.
    """

    return run_visual_recovery(
        input_path
    )


def recover_image(
    input_path,
):
    """
    Compatibility wrapper.
    """

    return run_visual_recovery(
        input_path
    )


# ============================================================
# CLI
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "ReFrag AI Visual Recovery Pipeline"
        )
    )

    parser.add_argument(
        "image",
        nargs="?",
        help=(
            "Path to broken/damaged image"
        ),
    )

    parser.add_argument(
        "--build-index",
        action="store_true",
        help=(
            "Build the reference feature index"
        ),
    )

    args = parser.parse_args()


    if args.build_index:

        build_reference_index()

        return


    if not args.image:

        parser.error(
            "Provide an image path or use --build-index."
        )


    result = run_visual_recovery(
        args.image
    )

    print()

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

