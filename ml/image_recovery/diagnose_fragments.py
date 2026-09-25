import json
from pathlib import Path

import cv2
import numpy as np


BASE = Path(__file__).resolve().parent

JUMBLED = BASE / "test" / "input" / "jumbled_dog.png"
TRUTH = BASE / "test" / "input" / "ground_truth.json"
FRAGMENTS = BASE / "test" / "fragments"


def mse(a, b):
    return float(
        np.mean(
            (
                a.astype(np.float32)
                - b.astype(np.float32)
            ) ** 2
        )
    )


def rotate_fragment(image, rotation):

    if rotation == 0:
        return image

    if rotation == 90:
        return cv2.rotate(
            image,
            cv2.ROTATE_90_CLOCKWISE,
        )

    if rotation == 180:
        return cv2.rotate(
            image,
            cv2.ROTATE_180,
        )

    if rotation == 270:
        return cv2.rotate(
            image,
            cv2.ROTATE_90_COUNTERCLOCKWISE,
        )

    raise ValueError(
        f"Unsupported rotation: {rotation}"
    )


print("=" * 70)
print(" ReFrag AI — Dataset Placement Diagnostic")
print("=" * 70)


# ------------------------------------------------------------
# Load jumbled image
# ------------------------------------------------------------

canvas = cv2.imread(
    str(JUMBLED)
)

if canvas is None:
    raise FileNotFoundError(
        f"Could not load:\n{JUMBLED}"
    )


# ------------------------------------------------------------
# Load ground truth
# ------------------------------------------------------------

with open(
    TRUTH,
    "r",
    encoding="utf-8",
) as file:

    truth = json.load(file)


results = []


# ------------------------------------------------------------
# Validate every fragment
# ------------------------------------------------------------

for item in truth["fragments"]:

    fragment_id = item["fragment_id"]

    x = item["scrambled_x"]
    y = item["scrambled_y"]

    width = item["width"]
    height = item["height"]

    rotation = item["rotation"]

    fragment_path = (
        FRAGMENTS
        / f"{fragment_id}.png"
    )

    clean = cv2.imread(
        str(fragment_path)
    )

    if clean is None:

        print(
            f"{fragment_id} | MISSING"
        )

        continue

    # --------------------------------------------------------
    # Rotate clean fragment exactly as generator did
    # --------------------------------------------------------

    expected = rotate_fragment(
        clean,
        rotation,
    )

    # --------------------------------------------------------
    # Extract actual fragment from jumbled image
    # --------------------------------------------------------

    actual = canvas[
        y:y + height,
        x:x + width
    ]

    # --------------------------------------------------------
    # Compare
    # --------------------------------------------------------

    score = mse(
        expected,
        actual,
    )

    results.append(score)

    status = (
        "PASS"
        if score < 2.0
        else "CHECK"
    )

    print(
        f"{fragment_id} | "
        f"rotation={rotation:3d}° | "
        f"position=({x:3d},{y:3d}) | "
        f"MSE={score:8.2f} | "
        f"{status}"
    )


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print("\n" + "=" * 70)

if results:

    passed = sum(
        score < 2.0
        for score in results
    )

    print(
        f"Fragments checked : {len(results)}"
    )

    print(
        f"Placement matches  : "
        f"{passed}/{len(results)}"
    )

    print(
        f"Average MSE        : "
        f"{np.mean(results):.4f}"
    )

    print(
        f"Maximum MSE        : "
        f"{np.max(results):.4f}"
    )

print("=" * 70)