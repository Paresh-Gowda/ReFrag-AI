import json
from pathlib import Path

import cv2
import numpy as np

from config import FRAGMENTS_DIR


# ============================================================
# ReFrag AI
# Visual Fragment Feature Extraction
# ============================================================


FEATURES_OUTPUT = (
    FRAGMENTS_DIR.parent /
    "artifacts" /
    "fragment_features.json"
)


# ------------------------------------------------------------
# Basic statistics
# ------------------------------------------------------------

def calculate_entropy(image):
    """
    Calculate Shannon entropy of a grayscale image.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    histogram = cv2.calcHist(
        [gray],
        [0],
        None,
        [256],
        [0, 256],
    )

    histogram = histogram.flatten()

    total = histogram.sum()

    if total == 0:
        return 0.0

    probabilities = (
        histogram / total
    )

    probabilities = probabilities[
        probabilities > 0
    ]

    entropy = -np.sum(
        probabilities *
        np.log2(probabilities)
    )

    return float(entropy)


def calculate_color_features(image):
    """
    Calculate RGB/BGR and HSV statistics.
    """

    mean_bgr = np.mean(
        image,
        axis=(0, 1)
    )

    std_bgr = np.std(
        image,
        axis=(0, 1)
    )

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    mean_hsv = np.mean(
        hsv,
        axis=(0, 1)
    )

    std_hsv = np.std(
        hsv,
        axis=(0, 1)
    )

    return {
        "mean_b": float(mean_bgr[0]),
        "mean_g": float(mean_bgr[1]),
        "mean_r": float(mean_bgr[2]),

        "std_b": float(std_bgr[0]),
        "std_g": float(std_bgr[1]),
        "std_r": float(std_bgr[2]),

        "mean_h": float(mean_hsv[0]),
        "mean_s": float(mean_hsv[1]),
        "mean_v": float(mean_hsv[2]),

        "std_h": float(std_hsv[0]),
        "std_s": float(std_hsv[1]),
        "std_v": float(std_hsv[2]),
    }


# ------------------------------------------------------------
# Edge features
# ------------------------------------------------------------

def calculate_edge_features(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    edges = cv2.Canny(
        gray,
        50,
        150
    )

    edge_pixels = np.count_nonzero(
        edges
    )

    total_pixels = edges.size

    edge_density = (
        edge_pixels /
        total_pixels
    )

    return {
        "edge_density": float(
            edge_density
        )
    }


# ------------------------------------------------------------
# Texture
# ------------------------------------------------------------

def calculate_texture_features(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Local gradient.
    gx = cv2.Sobel(
        gray,
        cv2.CV_64F,
        1,
        0,
        ksize=3
    )

    gy = cv2.Sobel(
        gray,
        cv2.CV_64F,
        0,
        1,
        ksize=3
    )

    magnitude = cv2.magnitude(
        gx.astype(np.float32),
        gy.astype(np.float32),
    )

    return {
        "gradient_mean": float(
            np.mean(magnitude)
        ),

        "gradient_std": float(
            np.std(magnitude)
        ),

        "gradient_max": float(
            np.max(magnitude)
        ),
    }


# ------------------------------------------------------------
# Boundary extraction
# ------------------------------------------------------------

def extract_boundary_features(image):

    """
    Extract the pixels along the four boundaries.

    These are the most important features for determining
    whether two fragments can be neighbors.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    ).astype(np.float32)

    height, width = gray.shape

    # Use several pixels instead of a single row/column
    # to make the comparison more stable.

    band = 5

    top = gray[
        0:band,
        :
    ]

    bottom = gray[
        height - band:height,
        :
    ]

    left = gray[
        :,
        0:band
    ]

    right = gray[
        :,
        width - band:width
    ]

    return {
        "top": top.mean(
            axis=0
        ).tolist(),

        "bottom": bottom.mean(
            axis=0
        ).tolist(),

        "left": left.mean(
            axis=1
        ).tolist(),

        "right": right.mean(
            axis=1
        ).tolist(),
    }


# ------------------------------------------------------------
# Boundary color features
# ------------------------------------------------------------

def extract_color_boundaries(image):

    image_float = image.astype(
        np.float32
    )

    band = 5

    top = image_float[
        0:band,
        :
    ]

    bottom = image_float[
        -band:,
        :
    ]

    left = image_float[
        :,
        0:band
    ]

    right = image_float[
        :,
        -band:
    ]

    return {
        "top_color": np.mean(
            top,
            axis=0
        ).tolist(),

        "bottom_color": np.mean(
            bottom,
            axis=0
        ).tolist(),

        "left_color": np.mean(
            left,
            axis=1
        ).tolist(),

        "right_color": np.mean(
            right,
            axis=1
        ).tolist(),
    }


# ------------------------------------------------------------
# Complete feature extraction
# ------------------------------------------------------------

def extract_features(image):

    features = {}

    features.update(
        calculate_color_features(
            image
        )
    )

    features.update(
        calculate_edge_features(
            image
        )
    )

    features.update(
        calculate_texture_features(
            image
        )
    )

    features["entropy"] = (
        calculate_entropy(image)
    )

    features.update(
        extract_boundary_features(
            image
        )
    )

    features.update(
        extract_color_boundaries(
            image
        )
    )

    return features


# ------------------------------------------------------------
# Process all fragments
# ------------------------------------------------------------

def extract_all_fragments():

    print("=" * 60)
    print(
        " ReFrag AI — Visual Feature Extraction"
    )
    print("=" * 60)

    fragment_files = sorted(
        FRAGMENTS_DIR.glob(
            "F*.png"
        )
    )

    if not fragment_files:

        raise FileNotFoundError(
            f"No fragments found in:\n"
            f"{FRAGMENTS_DIR}"
        )

    print(
        f"\nFragments found: "
        f"{len(fragment_files)}"
    )

    results = {}

    for index, fragment_path in enumerate(
        fragment_files,
        start=1
    ):

        image = cv2.imread(
            str(fragment_path)
        )

        if image is None:

            print(
                f"WARNING: "
                f"Could not read "
                f"{fragment_path.name}"
            )

            continue

        fragment_id = (
            fragment_path.stem
        )

        features = extract_features(
            image
        )

        results[fragment_id] = {
            "fragment_id": fragment_id,

            "file": str(
                fragment_path
            ),

            "width": int(
                image.shape[1]
            ),

            "height": int(
                image.shape[0]
            ),

            "features": features,
        }

        if index % 8 == 0:

            print(
                f"  Processed "
                f"{index}/{len(fragment_files)}"
            )

    # --------------------------------------------------------
    # Save features
    # --------------------------------------------------------

    FEATURES_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        FEATURES_OUTPUT,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
        )

    print(
        f"\nFeature file:"
        f"\n  {FEATURES_OUTPUT}"
    )

    print(
        "\nFeatures extracted:"
    )

    print(
        "  ✓ Color statistics"
    )

    print(
        "  ✓ HSV statistics"
    )

    print(
        "  ✓ Edge density"
    )

    print(
        "  ✓ Gradient statistics"
    )

    print(
        "  ✓ Entropy"
    )

    print(
        "  ✓ Boundary signatures"
    )

    print(
        "  ✓ Boundary color signatures"
    )

    print(
        "\n" + "=" * 60
    )

    print(
        f" FEATURE EXTRACTION COMPLETE"
    )

    print(
        f" {len(results)} fragments processed."
    )

    print(
        "=" * 60
    )

    return results


if __name__ == "__main__":
    extract_all_fragments()