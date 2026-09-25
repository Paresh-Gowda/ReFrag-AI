import cv2
import numpy as np

from config import (
    JUMBLED_IMAGE,
    FRAGMENTS_DIR,
    DEBUG_DIR,
    SEGMENTATION_DEBUG,
    GRID_ROWS,
    GRID_COLS,
    FRAGMENT_SIZE,
    GAP_SIZE,
    TOTAL_FRAGMENTS,
)


# ============================================================
# ReFrag AI
# Visual Fragment Segmentation
#
# Controlled Dataset Version
# ============================================================


def load_image():

    image = cv2.imread(
        str(JUMBLED_IMAGE)
    )

    if image is None:
        raise FileNotFoundError(
            f"Could not load image:\n{JUMBLED_IMAGE}"
        )

    return image


def detect_fragment_cells(image):

    """
    Our generated dataset places exactly one fragment
    inside every known grid cell.

    We therefore use the known physical layout to isolate
    each candidate region.

    This gives us reliable fragments for the next stages:
        feature extraction
        relationship analysis
        reconstruction
    """

    height, width = image.shape[:2]

    cell_size = FRAGMENT_SIZE + GAP_SIZE

    fragments = []

    fragment_number = 1

    for row in range(GRID_ROWS):

        for col in range(GRID_COLS):

            x = col * cell_size
            y = row * cell_size

            # Safety check.
            if (
                x + FRAGMENT_SIZE > width
                or
                y + FRAGMENT_SIZE > height
            ):
                continue

            crop = image[
                y:y + FRAGMENT_SIZE,
                x:x + FRAGMENT_SIZE
            ].copy()

            # Ignore completely empty regions.
            if crop.size == 0:
                continue

            gray = cv2.cvtColor(
                crop,
                cv2.COLOR_BGR2GRAY
            )

            # Determine whether this cell actually
            # contains meaningful image information.
            #
            # We don't use this to split the fragment.
            # It only validates that the cell is occupied.
            non_dark_pixels = np.count_nonzero(
                gray > 25
            )

            occupancy = (
                non_dark_pixels /
                gray.size
            )

            if occupancy < 0.02:
                continue

            fragments.append(
                {
                    "id": f"F{fragment_number:03d}",

                    "grid_row": row,

                    "grid_col": col,

                    "x": x,

                    "y": y,

                    "width": FRAGMENT_SIZE,

                    "height": FRAGMENT_SIZE,

                    "area": FRAGMENT_SIZE * FRAGMENT_SIZE,

                    "occupancy": float(
                        occupancy
                    ),

                    "image": crop,
                }
            )

            fragment_number += 1

    return fragments


def save_fragments(fragments):

    FRAGMENTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Remove previous fragments.
    for file in FRAGMENTS_DIR.glob("*.png"):
        file.unlink()

    results = []

    for fragment in fragments:

        output_path = (
            FRAGMENTS_DIR /
            f"{fragment['id']}.png"
        )

        cv2.imwrite(
            str(output_path),
            fragment["image"],
        )

        results.append(
            {
                "id": fragment["id"],

                "x": fragment["x"],

                "y": fragment["y"],

                "width": fragment["width"],

                "height": fragment["height"],

                "area": fragment["area"],

                "grid_row": fragment["grid_row"],

                "grid_col": fragment["grid_col"],

                "occupancy": fragment["occupancy"],

                "path": str(
                    output_path
                ),
            }
        )

    return results


def create_debug_image(
    image,
    fragments,
):

    debug = image.copy()

    for fragment in fragments:

        x = fragment["x"]
        y = fragment["y"]

        w = fragment["width"]
        h = fragment["height"]

        # Bounding box.
        cv2.rectangle(
            debug,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2,
        )

        # Fragment ID.
        cv2.putText(
            debug,
            fragment["id"],
            (x + 4, y + 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )

    DEBUG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cv2.imwrite(
        str(SEGMENTATION_DEBUG),
        debug,
    )


def segment():

    print("=" * 60)
    print(" ReFrag AI — Visual Fragment Segmentation")
    print("=" * 60)

    image = load_image()

    print(
        f"\nImage:"
        f"\n  {image.shape[1]} x {image.shape[0]}"
    )

    print(
        f"\nExpected grid:"
        f"\n  {GRID_ROWS} x {GRID_COLS}"
    )

    print(
        f"\nFragment size:"
        f"\n  {FRAGMENT_SIZE} x {FRAGMENT_SIZE}"
    )

    print(
        f"\nGap:"
        f"\n  {GAP_SIZE}px"
    )

    # --------------------------------------------------------
    # Segment
    # --------------------------------------------------------

    fragments = detect_fragment_cells(
        image
    )

    print(
        f"\nDetected fragments:"
        f" {len(fragments)}"
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    results = save_fragments(
        fragments
    )

    create_debug_image(
        image,
        fragments,
    )

    print(
        f"\nFragments directory:"
        f"\n  {FRAGMENTS_DIR}"
    )

    print(
        f"\nDebug image:"
        f"\n  {SEGMENTATION_DEBUG}"
    )

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    if results:

        widths = [
            item["width"]
            for item in results
        ]

        heights = [
            item["height"]
            for item in results
        ]

        print(
            "\nFragment dimensions:"
        )

        print(
            f"  Width  : "
            f"{min(widths)} - {max(widths)}"
        )

        print(
            f"  Height : "
            f"{min(heights)} - {max(heights)}"
        )

    print(
        "\n" + "=" * 60
    )

    if len(fragments) == TOTAL_FRAGMENTS:

        print(
            " SEGMENTATION SUCCESS"
        )

        print(
            f" Successfully isolated "
            f"{TOTAL_FRAGMENTS} fragments."
        )

    else:

        print(
            " SEGMENTATION FAILED"
        )

        print(
            f" Expected: {TOTAL_FRAGMENTS}"
        )

        print(
            f" Detected: {len(fragments)}"
        )

    print(
        "=" * 60
    )

    return results


if __name__ == "__main__":
    segment()