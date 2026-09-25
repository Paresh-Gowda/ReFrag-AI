import cv2
import json
import numpy as np
from pathlib import Path


# =========================================================
# PATHS
# =========================================================

BASE = Path(__file__).resolve().parent / "reference_database"

CLEAN = BASE / "clean"

FEATURE_INDEX = BASE / "feature_index.json"


# =========================================================
# FEATURE EXTRACTION
# =========================================================

def color_histogram(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    hist = cv2.calcHist(
        [hsv],
        [0, 1],
        None,
        [32, 32],
        [0, 180, 0, 256],
    )

    cv2.normalize(hist, hist)

    return hist.flatten()


def visual_features(path):
    image = cv2.imread(str(path))

    if image is None:
        raise ValueError(f"Cannot read image: {path}")

    image = cv2.resize(image, (256, 256))

    hist = color_histogram(image)

    small = cv2.resize(image, (32, 32))
    small = cv2.cvtColor(small, cv2.COLOR_BGR2LAB)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(
        gray,
        80,
        160,
    )

    edge_small = cv2.resize(
        edges,
        (32, 32),
    ).astype(np.float32)

    edge_small /= 255.0

    return np.concatenate([
        hist.astype(np.float32),
        small.astype(np.float32).flatten() / 255.0,
        edge_small.flatten(),
    ])


# =========================================================
# SIMILARITY
# =========================================================

def cosine_similarity(a, b):
    denominator = (
        np.linalg.norm(a)
        *
        np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(a, b) / denominator
    )


# =========================================================
# BUILD DATABASE
# =========================================================

def build_database():

    database = []

    files = sorted(
        CLEAN.glob("*.jpg")
    )

    print(
        f"Reference images found: {len(files)}"
    )

    if not files:
        raise RuntimeError(
            f"No clean images found in: {CLEAN}"
        )

    for i, path in enumerate(
        files,
        1,
    ):

        features = visual_features(path)

        database.append({
            "id": path.stem.replace(
                "_clean",
                "",
            ),
            "filename": path.name,
            "features": features.tolist(),
        })

        print(
            f"[{i:03d}/{len(files)}] {path.name}"
        )

    with open(
        FEATURE_INDEX,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            database,
            f,
        )

    print()
    print("=" * 65)
    print("REFERENCE INDEX CREATED")
    print("=" * 65)
    print(f"Images : {len(database)}")
    print(f"Index  : {FEATURE_INDEX}")


# =========================================================
# SEARCH
# =========================================================

def search(query_path, top_k=5):

    query_path = Path(query_path)

    if not FEATURE_INDEX.exists():

        raise RuntimeError(
            "Feature index not found.\n"
            f"Expected: {FEATURE_INDEX}\n"
            "Run:\n"
            "python ml/image_recovery/"
            "reference_matcher.py build"
        )

    with open(
        FEATURE_INDEX,
        "r",
        encoding="utf-8",
    ) as f:

        database = json.load(f)

    query = visual_features(
        query_path
    )

    results = []

    for item in database:

        reference = np.array(
            item["features"],
            dtype=np.float32,
        )

        similarity = cosine_similarity(
            query,
            reference,
        )

        results.append({
            "id": item["id"],
            "filename": item["filename"],
            "similarity": similarity,
        })

    results.sort(
        key=lambda x: x["similarity"],
        reverse=True,
    )

    return results[:top_k]


# =========================================================
# CLI
# =========================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:

        print("Usage:")
        print(
            "python reference_matcher.py build"
        )
        print(
            "python reference_matcher.py search <image>"
        )

        raise SystemExit(1)

    command = sys.argv[1]

    if command == "build":

        build_database()

    elif command == "search":

        if len(sys.argv) < 3:

            print("Missing image path.")
            raise SystemExit(1)

        results = search(
            sys.argv[2]
        )

        print()
        print("=" * 65)
        print("TOP REFERENCE MATCHES")
        print("=" * 65)

        for rank, result in enumerate(
            results,
            1,
        ):

            print(
                f"#{rank}  "
                f"{result['filename']:<25} "
                f"{result['similarity'] * 100:6.2f}%"
            )

    else:

        print(
            f"Unknown command: {command}"
        )
