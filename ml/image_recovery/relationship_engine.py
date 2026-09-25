import json
from itertools import combinations

import cv2
import numpy as np

from config import (
    FRAGMENTS_DIR,
    STRONG_RELATIONSHIP_THRESHOLD,
)


# ============================================================
# ReFrag AI
# Visual Fragment Relationship Engine
# ============================================================

FEATURE_FILE = (
    FRAGMENTS_DIR.parent
    / "artifacts"
    / "fragment_features.json"
)

RELATIONSHIP_FILE = (
    FRAGMENTS_DIR.parent
    / "artifacts"
    / "fragment_relationships.json"
)


# ------------------------------------------------------------
# Utility
# ------------------------------------------------------------

def normalize_score(value):
    return float(
        np.clip(
            value,
            0.0,
            1.0,
        )
    )


def similarity_from_difference(
    difference,
    scale=255.0,
):
    """
    Convert an absolute pixel difference into
    a 0-1 similarity score.
    """

    score = 1.0 - (
        difference / scale
    )

    return normalize_score(score)


# ------------------------------------------------------------
# Load fragments
# ------------------------------------------------------------

def load_fragments():

    fragment_files = sorted(
        FRAGMENTS_DIR.glob(
            "F*.png"
        )
    )

    fragments = {}

    for path in fragment_files:

        image = cv2.imread(
            str(path)
        )

        if image is None:
            continue

        fragments[path.stem] = image

    if not fragments:

        raise FileNotFoundError(
            f"No fragments found in:\n"
            f"{FRAGMENTS_DIR}"
        )

    return fragments


# ------------------------------------------------------------
# Edge extraction
# ------------------------------------------------------------

def get_edge_band(
    image,
    direction,
    band_size=5,
):
    """
    Extract a small boundary band from a fragment.
    """

    if direction == "left":

        return image[
            :,
            :band_size
        ]

    if direction == "right":

        return image[
            :,
            -band_size:
        ]

    if direction == "top":

        return image[
            :band_size,
            :
        ]

    if direction == "bottom":

        return image[
            -band_size:,
            :
        ]

    raise ValueError(
        f"Unknown direction: {direction}"
    )


# ------------------------------------------------------------
# Seam comparison
# ------------------------------------------------------------

def compare_seam(
    image_a,
    image_b,
    direction,
):
    """
    Compare the touching boundaries of two fragments.

    RIGHT:
        A.right ↔ B.left

    LEFT:
        A.left ↔ B.right

    TOP:
        A.top ↔ B.bottom

    BOTTOM:
        A.bottom ↔ B.top
    """

    if direction == "right":

        boundary_a = get_edge_band(
            image_a,
            "right"
        )

        boundary_b = get_edge_band(
            image_b,
            "left"
        )

    elif direction == "left":

        boundary_a = get_edge_band(
            image_a,
            "left"
        )

        boundary_b = get_edge_band(
            image_b,
            "right"
        )

    elif direction == "top":

        boundary_a = get_edge_band(
            image_a,
            "top"
        )

        boundary_b = get_edge_band(
            image_b,
            "bottom"
        )

    elif direction == "bottom":

        boundary_a = get_edge_band(
            image_a,
            "bottom"
        )

        boundary_b = get_edge_band(
            image_b,
            "top"
        )

    else:

        raise ValueError(
            f"Unknown direction: {direction}"
        )

    # Convert to float.
    a = boundary_a.astype(
        np.float32
    )

    b = boundary_b.astype(
        np.float32
    )

    # --------------------------------------------------------
    # Color difference
    # --------------------------------------------------------

    color_difference = np.mean(
        np.abs(a - b)
    )

    color_similarity = (
        similarity_from_difference(
            color_difference
        )
    )

    # --------------------------------------------------------
    # Grayscale difference
    # --------------------------------------------------------

    gray_a = cv2.cvtColor(
        boundary_a,
        cv2.COLOR_BGR2GRAY
    ).astype(np.float32)

    gray_b = cv2.cvtColor(
        boundary_b,
        cv2.COLOR_BGR2GRAY
    ).astype(np.float32)

    gray_difference = np.mean(
        np.abs(
            gray_a - gray_b
        )
    )

    boundary_similarity = (
        similarity_from_difference(
            gray_difference
        )
    )

    # --------------------------------------------------------
    # Gradient compatibility
    # --------------------------------------------------------

    grad_a_x = cv2.Sobel(
        gray_a,
        cv2.CV_32F,
        1,
        0,
        ksize=3,
    )

    grad_a_y = cv2.Sobel(
        gray_a,
        cv2.CV_32F,
        0,
        1,
        ksize=3,
    )

    grad_b_x = cv2.Sobel(
        gray_b,
        cv2.CV_32F,
        1,
        0,
        ksize=3,
    )

    grad_b_y = cv2.Sobel(
        gray_b,
        cv2.CV_32F,
        0,
        1,
        ksize=3,
    )

    gradient_difference = np.mean(
        np.abs(
            grad_a_x - grad_b_x
        )
        +
        np.abs(
            grad_a_y - grad_b_y
        )
    )

    gradient_similarity = (
        1.0 -
        np.clip(
            gradient_difference
            / 255.0,
            0.0,
            1.0,
        )
    )

    # --------------------------------------------------------
    # Final seam score
    # --------------------------------------------------------

    confidence = (
        0.40 * boundary_similarity
        +
        0.30 * color_similarity
        +
        0.30 * gradient_similarity
    )

    return {
        "color_similarity": float(
            color_similarity
        ),

        "boundary_similarity": float(
            boundary_similarity
        ),

        "gradient_similarity": float(
            gradient_similarity
        ),

        "confidence": float(
            normalize_score(
                confidence
            )
        ),
    }


# ------------------------------------------------------------
# Analyze one pair
# ------------------------------------------------------------

def analyze_pair(
    fragment_a_id,
    fragment_b_id,
    image_a,
    image_b,
):
    """
    Calculate relationship scores for all four possible
    directions between two fragments.
    """

    results = []

    directions = [
        "right",
        "left",
        "top",
        "bottom",
    ]

    for direction in directions:

        seam = compare_seam(
            image_a,
            image_b,
            direction,
        )

        results.append(
            {
                "fragment_a": (
                    fragment_a_id
                ),

                "fragment_b": (
                    fragment_b_id
                ),

                "direction": direction,

                **seam,
            }
        )

    return results


# ------------------------------------------------------------
# Build relationship graph
# ------------------------------------------------------------

def build_relationship_graph():

    print("=" * 60)
    print(
        " ReFrag AI — Fragment Relationship Analysis"
    )
    print("=" * 60)

    fragments = load_fragments()

    fragment_ids = sorted(
        fragments.keys()
    )

    print(
        f"\nFragments loaded: "
        f"{len(fragment_ids)}"
    )

    expected_pairs = (
        len(fragment_ids)
        * (len(fragment_ids) - 1)
        // 2
    )

    print(
        f"Unique fragment pairs: "
        f"{expected_pairs}"
    )

    relationships = []

    pair_counter = 0

    # --------------------------------------------------------
    # Compare every unique pair.
    # --------------------------------------------------------

    for id_a, id_b in combinations(
        fragment_ids,
        2
    ):

        pair_counter += 1

        pair_results = analyze_pair(
            id_a,
            id_b,
            fragments[id_a],
            fragments[id_b],
        )

        relationships.extend(
            pair_results
        )

        if (
            pair_counter % 256 == 0
            or
            pair_counter == expected_pairs
        ):

            print(
                f"  Pairs analyzed: "
                f"{pair_counter}/"
                f"{expected_pairs}"
            )

    # --------------------------------------------------------
    # Sort strongest relationships first.
    # --------------------------------------------------------

    relationships.sort(
        key=lambda item:
        item["confidence"],
        reverse=True,
    )

    strong = [
        item
        for item in relationships
        if item["confidence"]
        >= STRONG_RELATIONSHIP_THRESHOLD
    ]

    # --------------------------------------------------------
    # Build summary.
    # --------------------------------------------------------

    result = {
        "fragment_count": len(
            fragment_ids
        ),

        "unique_pairs": (
            expected_pairs
        ),

        "directional_relationships": (
            len(relationships)
        ),

        "strong_relationships": len(
            strong
        ),

        "threshold": (
            STRONG_RELATIONSHIP_THRESHOLD
        ),

        "relationships": relationships,
    }

    # --------------------------------------------------------
    # Save.
    # --------------------------------------------------------

    RELATIONSHIP_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        RELATIONSHIP_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
        )

    # --------------------------------------------------------
    # Report.
    # --------------------------------------------------------

    print(
        f"\nDirectional relationships:"
        f" {len(relationships)}"
    )

    print(
        f"Strong relationships:"
        f" {len(strong)}"
    )

    print(
        f"\nRelationship file:"
        f"\n  {RELATIONSHIP_FILE}"
    )

    print(
        "\nTop 10 relationships:"
    )

    for relationship in relationships[:10]:

        print(
            f"  "
            f"{relationship['fragment_a']} "
            f"→ "
            f"{relationship['fragment_b']} "
            f"| "
            f"{relationship['direction'].upper():6} "
            f"| "
            f"{relationship['confidence'] * 100:.2f}%"
        )

    print(
        "\n" + "=" * 60
    )

    print(
        " RELATIONSHIP ANALYSIS COMPLETE"
    )

    print(
        f" {len(relationships)} "
        f"directional relationships analyzed."
    )

    print(
        "=" * 60
    )

    return result


if __name__ == "__main__":
    build_relationship_graph()