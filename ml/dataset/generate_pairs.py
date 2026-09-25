import json
import random
from pathlib import Path

import pandas as pd


RANDOM_SEED = 42
NEGATIVE_RATIO = 1.0

BASE_DIR = Path(__file__).resolve().parents[1]
METADATA_PATH = BASE_DIR / "data" / "fragments_metadata.json"
OUTPUT_PATH = BASE_DIR / "data" / "pairs.csv"


def load_metadata():
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    random.seed(RANDOM_SEED)

    metadata = load_metadata()

    # Handle either a list or a dictionary containing fragment records
    if isinstance(metadata, dict):
        if "fragments" in metadata:
            records = metadata["fragments"]
        else:
            records = list(metadata.values())
    else:
        records = metadata

    df = pd.DataFrame(records)

    required_columns = {
        "fragment_id",
        "source_file",
        "fragment_index",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required metadata columns: {sorted(missing)}"
        )

    df = df.sort_values(
        ["source_file", "fragment_index"]
    ).reset_index(drop=True)

    positive_pairs = []

    # Consecutive fragments from the same source file
    for source_file, group in df.groupby("source_file"):
        group = group.sort_values("fragment_index")

        rows = group.to_dict("records")

        for i in range(len(rows) - 1):
            current = rows[i]
            next_fragment = rows[i + 1]

            if next_fragment["fragment_index"] == current["fragment_index"] + 1:
                positive_pairs.append(
                    {
                        "fragment_a": current["fragment_id"],
                        "fragment_b": next_fragment["fragment_id"],
                        "source_a": current["source_file"],
                        "source_b": next_fragment["source_file"],
                        "index_a": current["fragment_index"],
                        "index_b": next_fragment["fragment_index"],
                        "label": 1,
                    }
                )

    # Generate negative pairs from different source files
    all_records = df.to_dict("records")

    negative_target = int(len(positive_pairs) * NEGATIVE_RATIO)
    negative_pairs = []

    attempts = 0
    max_attempts = negative_target * 20 if negative_target else 100

    while len(negative_pairs) < negative_target and attempts < max_attempts:
        attempts += 1

        a, b = random.sample(all_records, 2)

        if a["source_file"] == b["source_file"]:
            continue

        negative_pairs.append(
            {
                "fragment_a": a["fragment_id"],
                "fragment_b": b["fragment_id"],
                "source_a": a["source_file"],
                "source_b": b["source_file"],
                "index_a": a["fragment_index"],
                "index_b": b["fragment_index"],
                "label": 0,
            }
        )

    pairs = positive_pairs + negative_pairs

    random.shuffle(pairs)

    output_df = pd.DataFrame(pairs)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Positive pairs: {len(positive_pairs)}")
    print(f"Negative pairs: {len(negative_pairs)}")
    print(f"Total pairs: {len(output_df)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()