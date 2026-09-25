import json
import random

import cv2
import numpy as np

from config import (
    ORIGINAL_IMAGE,
    JUMBLED_IMAGE,
    GROUND_TRUTH,
    GRID_ROWS,
    GRID_COLS,
    TOTAL_FRAGMENTS,
    FRAGMENT_SIZE,
    CANVAS_SIZE,
    GAP_SIZE,
    BACKGROUND_VALUE,
    ROTATIONS,
)


# ============================================================
# ReFrag AI
# Visual Recovery Dataset Generator
# ============================================================

SEED = 42


# ============================================================
# LOAD ORIGINAL IMAGE
# ============================================================

def load_original():
    """Load the clean source image."""

    image = cv2.imread(str(ORIGINAL_IMAGE))

    if image is None:
        raise FileNotFoundError(
            f"\nOriginal image not found:\n{ORIGINAL_IMAGE}"
        )

    return image


# ============================================================
# PREPARE IMAGE
# ============================================================

def prepare_image(image):
    """
    Resize the original image so it can be divided into
    an exact GRID_ROWS x GRID_COLS grid.
    """

    target_size = GRID_ROWS * FRAGMENT_SIZE

    image = cv2.resize(
        image,
        (target_size, target_size),
        interpolation=cv2.INTER_AREA,
    )

    return image


# ============================================================
# CREATE FRAGMENTS
# ============================================================

def create_fragments(image):
    """
    Divide the clean image into equal-sized fragments.
    """

    fragments = []

    fragment_number = 1

    for row in range(GRID_ROWS):

        for col in range(GRID_COLS):

            x1 = col * FRAGMENT_SIZE
            y1 = row * FRAGMENT_SIZE

            x2 = x1 + FRAGMENT_SIZE
            y2 = y1 + FRAGMENT_SIZE

            tile = image[
                y1:y2,
                x1:x2
            ].copy()

            fragments.append(
                {
                    "id": f"F{fragment_number:03d}",
                    "original_row": row,
                    "original_col": col,
                    "original_index": (
                        row * GRID_COLS + col
                    ),
                    "image": tile,
                }
            )

            fragment_number += 1

    return fragments


# ============================================================
# ROTATE FRAGMENT
# ============================================================

def rotate_fragment(image, rotation):
    """
    Rotate a fragment by one of the supported angles.
    """

    if rotation == 0:
        return image.copy()

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


# ============================================================
# GENERATE POSITIONS
# ============================================================

def generate_positions():
    """
    Generate guaranteed non-overlapping positions.
    """

    cell_size = FRAGMENT_SIZE + GAP_SIZE

    required_width = (
        GRID_COLS * FRAGMENT_SIZE
        + (GRID_COLS - 1) * GAP_SIZE
    )

    required_height = (
        GRID_ROWS * FRAGMENT_SIZE
        + (GRID_ROWS - 1) * GAP_SIZE
    )

    if required_width > CANVAS_SIZE:
        raise ValueError(
            "\nCanvas is too small.\n"
            f"Required width : {required_width}\n"
            f"Canvas width   : {CANVAS_SIZE}\n"
        )

    if required_height > CANVAS_SIZE:
        raise ValueError(
            "\nCanvas is too small.\n"
            f"Required height: {required_height}\n"
            f"Canvas height  : {CANVAS_SIZE}\n"
        )

    positions = []

    for row in range(GRID_ROWS):

        for col in range(GRID_COLS):

            x = col * cell_size
            y = row * cell_size

            positions.append(
                (x, y)
            )

    # Shuffle physical locations.
    random.shuffle(positions)

    return positions


# ============================================================
# CREATE CANVAS
# ============================================================

def create_canvas():
    """
    Create the dark background used for segmentation.
    """

    return np.full(
        (
            CANVAS_SIZE,
            CANVAS_SIZE,
            3,
        ),
        BACKGROUND_VALUE,
        dtype=np.uint8,
    )


# ============================================================
# SAVE CLEAN FRAGMENTS
# ============================================================

def save_clean_fragments(fragments):
    """
    Save the original, unrotated fragments.

    These files are used only for evaluation/debugging.
    The actual recovery system must not depend on them.
    """

    fragment_dir = (
        JUMBLED_IMAGE.parent.parent
        / "fragments"
    )

    fragment_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Remove stale fragments.
    for old_file in fragment_dir.glob("F*.png"):
        old_file.unlink()

    for fragment in fragments:

        fragment_path = (
            fragment_dir
            / f"{fragment['id']}.png"
        )

        success = cv2.imwrite(
            str(fragment_path),
            fragment["image"],
        )

        if not success:
            raise RuntimeError(
                f"Failed to save fragment:\n"
                f"{fragment_path}"
            )

    return fragment_dir


# ============================================================
# GENERATE DATASET
# ============================================================

def generate_dataset():

    random.seed(SEED)
    np.random.seed(SEED)

    print("=" * 60)
    print(" ReFrag AI — Visual Recovery Dataset Generator")
    print("=" * 60)

    # --------------------------------------------------------
    # Load original
    # --------------------------------------------------------

    image = load_original()

    print(
        f"\nOriginal image:"
        f"\n  {ORIGINAL_IMAGE}"
    )

    print(
        f"\nOriginal dimensions:"
        f"\n  {image.shape[1]} x {image.shape[0]}"
    )

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    image = prepare_image(image)

    print(
        f"\nNormalized image:"
        f"\n  {image.shape[1]} x {image.shape[0]}"
    )

    # --------------------------------------------------------
    # Create fragments
    # --------------------------------------------------------

    fragments = create_fragments(image)

    print(
        f"\nFragments created:"
        f"\n  {len(fragments)}"
    )

    if len(fragments) != TOTAL_FRAGMENTS:

        raise RuntimeError(
            "\nUnexpected fragment count.\n"
            f"Expected: {TOTAL_FRAGMENTS}\n"
            f"Created : {len(fragments)}"
        )

    # --------------------------------------------------------
    # SAVE CLEAN FRAGMENTS
    # --------------------------------------------------------

    fragment_dir = save_clean_fragments(
        fragments
    )

    print(
        f"\nSaved clean fragments:"
        f"\n  {fragment_dir}"
    )

    # --------------------------------------------------------
    # Generate locations
    # --------------------------------------------------------

    positions = generate_positions()

    # --------------------------------------------------------
    # Create canvas
    # --------------------------------------------------------

    canvas = create_canvas()

    # --------------------------------------------------------
    # Shuffle fragments
    # --------------------------------------------------------

    shuffled_fragments = fragments.copy()

    random.shuffle(
        shuffled_fragments
    )

    ground_truth = []

    # --------------------------------------------------------
    # Place fragments
    # --------------------------------------------------------

    for position_index, fragment in enumerate(
        shuffled_fragments
    ):

        x, y = positions[position_index]

        rotation = random.choice(
            ROTATIONS
        )

        tile = rotate_fragment(
            fragment["image"],
            rotation,
        )

        height, width = tile.shape[:2]

        # Safety check.
        if (
            x + width > CANVAS_SIZE
            or
            y + height > CANVAS_SIZE
        ):
            raise RuntimeError(
                "Fragment would exceed canvas bounds."
            )

        # Place fragment.
        canvas[
            y:y + height,
            x:x + width
        ] = tile

        # Store ground truth.
        ground_truth.append(
            {
                "fragment_id": fragment["id"],

                "original_row": (
                    fragment["original_row"]
                ),

                "original_col": (
                    fragment["original_col"]
                ),

                "original_index": (
                    fragment["original_index"]
                ),

                "scrambled_index": (
                    position_index
                ),

                "scrambled_x": int(x),

                "scrambled_y": int(y),

                "width": int(width),

                "height": int(height),

                "rotation": int(rotation),
            }
        )

    # --------------------------------------------------------
    # Save jumbled image
    # --------------------------------------------------------

    JUMBLED_IMAGE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    success = cv2.imwrite(
        str(JUMBLED_IMAGE),
        canvas,
    )

    if not success:

        raise RuntimeError(
            f"Failed to save:\n{JUMBLED_IMAGE}"
        )

    # --------------------------------------------------------
    # Save ground truth
    # --------------------------------------------------------

    GROUND_TRUTH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ground_truth_data = {
        "dataset": "ReFrag AI Visual Recovery",

        "grid_rows": GRID_ROWS,

        "grid_cols": GRID_COLS,

        "total_fragments": TOTAL_FRAGMENTS,

        "fragment_size": FRAGMENT_SIZE,

        "gap_size": GAP_SIZE,

        "canvas_size": CANVAS_SIZE,

        "seed": SEED,

        "fragments": ground_truth,
    }

    with open(
        GROUND_TRUTH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            ground_truth_data,
            file,
            indent=2,
        )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print(
        "\nDataset configuration:"
    )

    print(
        f"  Grid          : "
        f"{GRID_ROWS} x {GRID_COLS}"
    )

    print(
        f"  Fragments     : "
        f"{TOTAL_FRAGMENTS}"
    )

    print(
        f"  Fragment size : "
        f"{FRAGMENT_SIZE} x {FRAGMENT_SIZE}"
    )

    print(
        f"  Gap           : "
        f"{GAP_SIZE}px"
    )

    print(
        f"  Canvas        : "
        f"{CANVAS_SIZE} x {CANVAS_SIZE}"
    )

    print(
        f"  Rotations     : "
        f"{ROTATIONS}"
    )

    print(
        "\nGenerated files:"
    )

    print(
        f"  Jumbled image:"
        f"\n  {JUMBLED_IMAGE}"
    )

    print(
        f"\n  Ground truth:"
        f"\n  {GROUND_TRUTH}"
    )

    print(
        f"\n  Clean fragments:"
        f"\n  {fragment_dir}"
    )

    print(
        "\n" + "=" * 60
    )

    print(
        " DATASET GENERATION COMPLETE"
    )

    print(
        f" {TOTAL_FRAGMENTS} fragments generated successfully."
    )

    print(
        "=" * 60
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    generate_dataset()