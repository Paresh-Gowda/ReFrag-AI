import json
from pathlib import Path

import cv2
import numpy as np


BASE = Path(__file__).resolve().parent
FRAGMENT_DIR = BASE / "test" / "fragments"
TRUTH = BASE / "test" / "input" / "ground_truth.json"
OUTPUT = BASE / "test" / "artifacts" / "visual_compatibility.json"


ROTATIONS = [0, 90, 180, 270]


def rotate(img, angle):
    if angle == 0:
        return img
    if angle == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if angle == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)


def normalize(img):
    img = img.astype(np.float32) / 255.0
    return img


def seam_cost(a, b, direction, band=12):
    """
    Compare the actual touching boundaries of two oriented fragments.

    RIGHT:
        A right edge <-> B left edge

    DOWN:
        A bottom edge <-> B top edge
    """

    if direction == "RIGHT":
        a_edge = a[:, -band:]
        b_edge = b[:, :band]

    else:
        a_edge = a[-band:, :]
        b_edge = b[:band, :]

    # Pixel continuity
    color = np.mean(
        np.abs(
            normalize(a_edge)
            - normalize(b_edge)
        )
    )

    # Gradient continuity
    ag = cv2.cvtColor(a_edge, cv2.COLOR_BGR2GRAY)
    bg = cv2.cvtColor(b_edge, cv2.COLOR_BGR2GRAY)

    ag = cv2.Sobel(
        ag,
        cv2.CV_32F,
        1,
        1,
        ksize=3,
    )

    bg = cv2.Sobel(
        bg,
        cv2.CV_32F,
        1,
        1,
        ksize=3,
    )

    gradient = np.mean(
        np.abs(ag - bg)
    ) / 255.0

    # Structural edge continuity
    ae = cv2.Canny(
        cv2.cvtColor(
            a_edge,
            cv2.COLOR_BGR2GRAY,
        ),
        50,
        150,
    )

    be = cv2.Canny(
        cv2.cvtColor(
            b_edge,
            cv2.COLOR_BGR2GRAY,
        ),
        50,
        150,
    )

    edge = np.mean(
        np.abs(
            ae.astype(np.float32)
            - be.astype(np.float32)
        )
    ) / 255.0

    # Combined cost.
    return float(
        0.55 * color
        + 0.30 * gradient
        + 0.15 * edge
    )


def load_fragments():

    fragments = {}

    for path in sorted(
        FRAGMENT_DIR.glob("F*.png")
    ):

        image = cv2.imread(
            str(path)
        )

        if image is not None:
            fragments[
                path.stem
            ] = image

    return fragments


def build():

    print("=" * 70)
    print(" ReFrag AI — Visual Match Engine V4")
    print("=" * 70)

    fragments = load_fragments()

    print(
        f"Fragments loaded: "
        f"{len(fragments)}"
    )

    oriented = {}

    for fid, image in fragments.items():

        for angle in ROTATIONS:

            oriented[
                (fid, angle)
            ] = rotate(
                image,
                angle,
            )

    relationships = []

    ids = list(fragments.keys())

    total = (
        len(ids)
        * (len(ids) - 1)
        * 4
        * 2
    )

    processed = 0

    for a in ids:

        for b in ids:

            if a == b:
                continue

            for angle_a in ROTATIONS:

                img_a = oriented[
                    (a, angle_a)
                ]

                for angle_b in ROTATIONS:

                    img_b = oriented[
                        (b, angle_b)
                    ]

                    for direction in (
                        "RIGHT",
                        "DOWN",
                    ):

                        cost = seam_cost(
                            img_a,
                            img_b,
                            direction,
                        )

                        relationships.append(
                            {
                                "source": a,
                                "target": b,
                                "source_rotation": angle_a,
                                "target_rotation": angle_b,
                                "direction": direction,
                                "cost": float(cost),
                            }
                        )

            processed += 1

            if processed % 8 == 0:
                print(
                    f"Processed {processed}/"
                    f"{len(ids)} fragments"
                )

    relationships.sort(
        key=lambda x: x["cost"]
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            {
                "fragments": len(ids),
                "relationships": relationships,
            },
            f,
            indent=2,
        )

    print()
    print(
        f"Relationships: "
        f"{len(relationships)}"
    )

    print(
        f"Output: {OUTPUT}"
    )

    print("=" * 70)


if __name__ == "__main__":
    build()
