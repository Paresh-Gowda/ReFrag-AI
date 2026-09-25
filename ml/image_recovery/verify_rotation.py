import json
from pathlib import Path

import numpy as np
from PIL import Image


BASE_DIR = Path(__file__).resolve().parent

ORIGINAL = (
    BASE_DIR /
    "test" /
    "input" /
    "original_dog.png"
)

GROUND_TRUTH = (
    BASE_DIR /
    "test" /
    "input" /
    "ground_truth.json"
)

FRAGMENTS_DIR = (
    BASE_DIR /
    "test" /
    "fragments"
)

GRID_ROWS = 8
GRID_COLS = 8
TILE = 96


def mse(a, b):

    a = a.astype(
        np.float32
    )

    b = b.astype(
        np.float32
    )

    return float(
        np.mean(
            (a - b) ** 2
        )
    )


def rotate(image, angle):

    if angle == 0:
        return image

    if angle == 90:
        # OpenCV: 90° CLOCKWISE
        return np.rot90(
            image,
            -1
        ).copy()

    if angle == 180:
        return np.rot90(
            image,
            2
        ).copy()

    if angle == 270:
        # OpenCV: 90° COUNTER-CLOCKWISE
        return np.rot90(
            image,
            1
        ).copy()

    raise ValueError(
        f"Unsupported rotation: {angle}"
    )

    if angle == 0:
        return image

    if angle == 90:
        return np.rot90(
            image,
            1
        ).copy()

    if angle == 180:
        return np.rot90(
            image,
            2
        ).copy()

    if angle == 270:
        return np.rot90(
            image,
            3
        ).copy()


# ------------------------------------------------------------
# Load original and normalize to 768x768
# ------------------------------------------------------------

original = Image.open(
    ORIGINAL
).convert(
    "RGB"
).resize(
    (
        GRID_COLS * TILE,
        GRID_ROWS * TILE
    )
)

original = np.asarray(
    original,
    dtype=np.uint8
)


# ------------------------------------------------------------
# Ground truth
# ------------------------------------------------------------

with open(
    GROUND_TRUTH,
    "r",
    encoding="utf-8"
) as f:

    truth = json.load(f)


print("=" * 65)
print(
    " ReFrag AI — Fragment Rotation Verification"
)
print("=" * 65)

print()

results = []

for item in truth["fragments"]:

    fragment_id = item[
        "fragment_id"
    ]

    row = int(
        item["original_row"]
    )

    col = int(
        item["original_col"]
    )

    stored_rotation = int(
        item["rotation"]
    )

    path = (
        FRAGMENTS_DIR /
        f"{fragment_id}.png"
    )

    fragment = Image.open(
        path
    ).convert(
        "RGB"
    ).resize(
        (
            TILE,
            TILE
        )
    )

    fragment = np.asarray(
        fragment,
        dtype=np.uint8
    )

    target = original[
        row * TILE:
        (row + 1) * TILE,

        col * TILE:
        (col + 1) * TILE
    ]

    scores = {}

    for rotation in (
        0,
        90,
        180,
        270
    ):

        candidate = rotate(
            fragment,
            rotation
        )

        scores[
            rotation
        ] = mse(
            candidate,
            target
        )

    best_rotation = min(
        scores,
        key=scores.get
    )

    expected_rotation = (
        360 -
        stored_rotation
    ) % 360

    results.append({
        "fragment": fragment_id,
        "stored_rotation":
            stored_rotation,
        "expected_inverse":
            expected_rotation,
        "best_rotation":
            best_rotation,
        "best_mse":
            scores[
                best_rotation
            ],
        "expected_mse":
            scores[
                expected_rotation
            ]
    })


# ------------------------------------------------------------
# Report
# ------------------------------------------------------------

correct = sum(
    1
    for x in results
    if x["best_rotation"]
    ==
    x["expected_inverse"]
)

accuracy = (
    100.0 *
    correct /
    len(results)
)

print(
    f"Fragments checked: "
    f"{len(results)}"
)

print(
    f"Rotation accuracy: "
    f"{accuracy:.2f}%"
)

print()

print(
    "Sample verification:"
)

for item in results[:15]:

    print(
        f"  {item['fragment']} "
        f"| stored="
        f"{item['stored_rotation']}° "
        f"| expected inverse="
        f"{item['expected_inverse']}° "
        f"| detected="
        f"{item['best_rotation']}° "
        f"| mse="
        f"{item['best_mse']:.2f}"
    )

print()

print("=" * 65)

if accuracy >= 95:

    print(
        "✓ ROTATION CONVENTION VERIFIED"
    )

else:

    print(
        "✗ ROTATION CONVENTION MISMATCH"
    )

print("=" * 65)