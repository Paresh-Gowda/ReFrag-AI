import cv2
import json
import numpy as np
from pathlib import Path


def analyze_damage(broken_path, reference_path, output_dir="test/output/evidence"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    broken = cv2.imread(str(broken_path))
    reference = cv2.imread(str(reference_path))

    if broken is None:
        raise ValueError(f"Cannot read broken image: {broken_path}")

    if reference is None:
        raise ValueError(f"Cannot read reference image: {reference_path}")

    # Put both images on the same canvas.
    reference = cv2.resize(
        reference,
        (broken.shape[1], broken.shape[0]),
        interpolation=cv2.INTER_AREA
    )

    # Pixel difference.
    diff = cv2.absdiff(broken, reference)

    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # Adaptive threshold.
    threshold = max(18, int(np.mean(gray_diff) + 2 * np.std(gray_diff)))

    mask = (gray_diff > threshold).astype(np.uint8) * 255

    # Remove tiny noise.
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Connected damage regions.
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        mask,
        connectivity=8
    )

    regions = []

    for label in range(1, num_labels):
        x, y, w, h, area = stats[label]

        # Ignore tiny regions.
        if area < 100:
            continue

        regions.append({
            "region_id": len(regions) + 1,
            "x": int(x),
            "y": int(y),
            "width": int(w),
            "height": int(h),
            "area_pixels": int(area),
            "area_percent": round(
                area / (mask.shape[0] * mask.shape[1]) * 100,
                3
            )
        })

    total_pixels = mask.shape[0] * mask.shape[1]
    damaged_pixels = int(np.count_nonzero(mask))
    preserved_pixels = total_pixels - damaged_pixels

    damage_percent = damaged_pixels / total_pixels * 100
    recovered_percent = preserved_pixels / total_pixels * 100

    # Evidence visualization.
    evidence_map = broken.copy()

    # Red = damaged.
    evidence_map[mask > 0] = [0, 0, 255]

    # Draw region boundaries.
    for region in regions:
        x = region["x"]
        y = region["y"]
        w = region["width"]
        h = region["height"]

        cv2.rectangle(
            evidence_map,
            (x, y),
            (x + w, y + h),
            (0, 255, 255),
            2
        )

        cv2.putText(
            evidence_map,
            f"R{region['region_id']}",
            (x, max(20, y - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

    # Reference-assisted restoration.
    restored = broken.copy()
    restored[mask > 0] = reference[mask > 0]

    # Save outputs.
    mask_path = output_dir / "damage_mask.png"
    evidence_path = output_dir / "evidence_map.png"
    restored_path = output_dir / "restored_image.png"
    report_path = output_dir / "evidence.json"

    cv2.imwrite(str(mask_path), mask)
    cv2.imwrite(str(evidence_path), evidence_map)
    cv2.imwrite(str(restored_path), restored)

    report = {
        "broken_image": str(broken_path),
        "reference_image": str(reference_path),

        "image_width": int(mask.shape[1]),
        "image_height": int(mask.shape[0]),

        "total_pixels": int(total_pixels),
        "preserved_pixels": int(preserved_pixels),
        "damaged_pixels": int(damaged_pixels),

        "recovered_percent": round(recovered_percent, 2),
        "damaged_percent": round(damage_percent, 2),

        "damage_regions": len(regions),
        "regions": regions,

        "evidence": {
            "preserved_content": "DIRECT_INPUT_EVIDENCE",
            "damaged_content": "DIFFERENCE_FROM_REFERENCE",
            "restored_content": "REFERENCE_ASSISTED"
        },

        "outputs": {
            "damage_mask": str(mask_path),
            "evidence_map": str(evidence_path),
            "restored_image": str(restored_path)
        }
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print(
            "Usage:\n"
            "python damage_analyzer.py <broken> <reference>"
        )
        raise SystemExit(1)

    report = analyze_damage(
        sys.argv[1],
        sys.argv[2]
    )

    print()
    print("=" * 60)
    print("REFRAG AI — DAMAGE & EVIDENCE ANALYSIS")
    print("=" * 60)

    print(f"Image size       : {report['image_width']} x {report['image_height']}")
    print(f"Total pixels     : {report['total_pixels']:,}")
    print(f"Preserved        : {report['preserved_pixels']:,}")
    print(f"Damaged          : {report['damaged_pixels']:,}")
    print(f"Recovered        : {report['recovered_percent']:.2f}%")
    print(f"Damaged          : {report['damaged_percent']:.2f}%")
    print(f"Damage regions   : {report['damage_regions']}")

    print()
    print("Evidence:")
    print("  Preserved  → DIRECT INPUT EVIDENCE")
    print("  Damaged    → REFERENCE DIFFERENCE")
    print("  Restored   → REFERENCE-ASSISTED")

    print()
    print(f"Report: {report['outputs']['restored_image']}")
