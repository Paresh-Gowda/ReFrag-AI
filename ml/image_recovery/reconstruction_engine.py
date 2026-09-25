import json
from pathlib import Path

import cv2
import numpy as np


BASE = Path(__file__).resolve().parent

FRAGMENTS_DIR = BASE / "test" / "fragments"
OUTPUT_DIR = BASE / "test" / "output"
ARTIFACT_DIR = BASE / "test" / "artifacts"


FRAGMENT_SIZE = 96
GRID_SIZE = 8


def rotate(image, angle):

    if angle == 0:
        return image

    if angle == 90:
        return cv2.rotate(
            image,
            cv2.ROTATE_90_CLOCKWISE,
        )

    if angle == 180:
        return cv2.rotate(
            image,
            cv2.ROTATE_180,
        )

    return cv2.rotate(
        image,
        cv2.ROTATE_90_COUNTERCLOCKWISE,
    )


def seam_cost(a, b, direction):

    band = 8

    if direction == "RIGHT":
        edge_a = a[:, -band:]
        edge_b = b[:, :band]

    else:
        edge_a = a[-band:, :]
        edge_b = b[:band, :]

    diff = np.abs(
        edge_a.astype(np.float32)
        - edge_b.astype(np.float32)
    )

    return float(np.mean(diff))


def load_fragments():

    fragments = {}

    for path in sorted(
        FRAGMENTS_DIR.glob("F*.png")
    ):

        image = cv2.imread(
            str(path)
        )

        if image is not None:
            fragments[path.stem] = image

    return fragments


def build_orientations(fragments):

    orientations = {}

    for fid, image in fragments.items():

        orientations[fid] = {}

        for angle in (
            0,
            90,
            180,
            270,
        ):

            orientations[fid][angle] = rotate(
                image,
                angle,
            )

    return orientations


def find_best_start(orientations):

    best = None
    best_score = float("inf")

    ids = list(orientations.keys())

    for fid in ids:

        for angle in orientations[fid]:

            image = orientations[fid][angle]

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY,
            )

            score = float(
                np.mean(gray)
            )

            if score < best_score:

                best_score = score

                best = (
                    fid,
                    angle,
                )

    return best


def choose_neighbor(
    current,
    used,
    orientations,
    direction,
):

    current_id, current_angle = current

    source = orientations[
        current_id
    ][current_angle]

    best = None
    best_cost = float("inf")

    for fid in orientations:

        if fid in used:
            continue

        for angle in orientations[fid]:

            candidate = orientations[
                fid
            ][angle]

            cost = seam_cost(
                source,
                candidate,
                direction,
            )

            if cost < best_cost:

                best_cost = cost

                best = (
                    fid,
                    angle,
                )

    return best


def reconstruct():

    print("=" * 70)
    print(" ReFrag AI — Fast Visual Reconstruction")
    print("=" * 70)

    fragments = load_fragments()

    print(
        f"Fragments loaded: "
        f"{len(fragments)}"
    )

    if len(fragments) != 64:

        raise RuntimeError(
            f"Expected 64 fragments, "
            f"found {len(fragments)}"
        )

    orientations = build_orientations(
        fragments
    )

    print(
        "Generated 4 orientations "
        "for every fragment."
    )

    # --------------------------------------------------------
    # Build simple grid
    # --------------------------------------------------------

    grid = [
        [None for _ in range(GRID_SIZE)]
        for _ in range(GRID_SIZE)
    ]

    used = set()

    start = find_best_start(
        orientations
    )

    grid[0][0] = start
    used.add(start[0])

    print(
        f"Starting fragment: "
        f"{start[0]} "
        f"({start[1]}°)"
    )

    # --------------------------------------------------------
    # Fill rows
    # --------------------------------------------------------

    for row in range(GRID_SIZE):

        for col in range(GRID_SIZE):

            if row == 0 and col == 0:
                continue

            if col > 0:

                previous = grid[row][col - 1]

                candidate = choose_neighbor(
                    previous,
                    used,
                    orientations,
                    "RIGHT",
                )

            else:

                previous = grid[row - 1][col]

                candidate = choose_neighbor(
                    previous,
                    used,
                    orientations,
                    "DOWN",
                )

            if candidate is None:
                raise RuntimeError(
                    "Could not place fragment."
                )

            grid[row][col] = candidate

            used.add(
                candidate[0]
            )

    # --------------------------------------------------------
    # Assemble image
    # --------------------------------------------------------

    canvas = np.zeros(
        (
            GRID_SIZE * FRAGMENT_SIZE,
            GRID_SIZE * FRAGMENT_SIZE,
            3,
        ),
        dtype=np.uint8,
    )

    for row in range(GRID_SIZE):

        for col in range(GRID_SIZE):

            fid, angle = grid[row][col]

            tile = orientations[
                fid
            ][angle]

            y = (
                row
                * FRAGMENT_SIZE
            )

            x = (
                col
                * FRAGMENT_SIZE
            )

            canvas[
                y:y + FRAGMENT_SIZE,
                x:x + FRAGMENT_SIZE
            ] = tile

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / "reconstructed_fast.png"
    )

    cv2.imwrite(
        str(output_path),
        canvas,
    )

    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    result = {

        "success": True,

        "fragment_count": len(
            fragments
        ),

        "grid": [
            [
                {
                    "fragment": item[0],
                    "rotation": item[1],
                }
                for item in row
            ]
            for row in grid
        ],

        "output": str(
            output_path
        ),
    }

    result_path = (
        ARTIFACT_DIR
        / "fast_reconstruction.json"
    )

    with open(
        result_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
        )

    print()
    print(
        f"Reconstructed: "
        f"{len(used)}/64"
    )

    print(
        f"Output: "
        f"{output_path}"
    )

    print(
        f"Metadata: "
        f"{result_path}"
    )

    print("=" * 70)


if __name__ == "__main__":
    reconstruct()