#!/usr/bin/env python3

"""
ReFrag AI - Reconstruction Engine

Uses the trained Fragment Relationship Model to discover
likely fragment chains and reconstruct candidate files.
"""

from pathlib import Path
import argparse

import joblib
import numpy as np
import pandas as pd


ML_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = ML_DIR / "saved" / "relationship_model.joblib"
PAIR_FEATURES_PATH = ML_DIR / "features" / "pair_features.csv"
FRAGMENTS_DIR = ML_DIR / "data" / "fragments"

DEFAULT_OUTPUT_DIR = ML_DIR / "reconstructed"

DEFAULT_THRESHOLD = 0.70


def load_model():
    print("Loading relationship model...")

    model = joblib.load(MODEL_PATH)

    print("Relationship model loaded.")

    return model


def load_pair_features():
    print("Loading pair features...")

    return pd.read_csv(PAIR_FEATURES_PATH)


def get_model_features(df):
    """
    Remove metadata columns and keep only numerical
    features used by the relationship model.
    """

    metadata_columns = [
        "fragment_a",
        "fragment_b",
        "source_a",
        "source_b",
        "index_a",
        "index_b",
        "label",
    ]

    feature_columns = [
        column
        for column in df.columns
        if column not in metadata_columns
    ]

    return df[feature_columns]


def calculate_relationships(model, pair_df):
    """
    Calculate relationship probability for every pair.
    """

    X = get_model_features(pair_df)

    probabilities = model.predict_proba(X)

    result = pair_df.copy()

    # Class 1 = Related
    result["relationship_probability"] = probabilities[:, 1]

    return result


def build_chains(pair_df, threshold):
    """
    Build candidate fragment chains using the strongest
    relationship predictions.
    """

    strong_pairs = pair_df[
        pair_df["relationship_probability"] >= threshold
    ].copy()

    strong_pairs = strong_pairs.sort_values(
        "relationship_probability",
        ascending=False,
    )

    next_fragment = {}
    previous_fragment = {}

    # Select strongest non-conflicting relationships.
    for _, row in strong_pairs.iterrows():

        fragment_a = row["fragment_a"]
        fragment_b = row["fragment_b"]

        if fragment_a == fragment_b:
            continue

        if fragment_a in next_fragment:
            continue

        if fragment_b in previous_fragment:
            continue

        next_fragment[fragment_a] = fragment_b
        previous_fragment[fragment_b] = fragment_a

    # Chain starting points have no previous fragment.
    starts = [
        fragment
        for fragment in next_fragment
        if fragment not in previous_fragment
    ]

    chains = []
    visited = set()

    for start in starts:

        chain = []
        current = start

        while current in next_fragment:

            if current in visited:
                break

            visited.add(current)
            chain.append(current)

            current = next_fragment[current]

        if current not in visited:
            chain.append(current)

        if len(chain) >= 2:
            chains.append(chain)

    return chains


def reconstruct_chain(chain, fragments_dir, output_path):
    """
    Concatenate all fragments in a chain.
    """

    with open(output_path, "wb") as output:

        for fragment_id in chain:

            fragment_path = fragments_dir / f"{fragment_id}.bin"

            if not fragment_path.exists():
                print(
                    f"Warning: fragment not found: {fragment_id}"
                )
                continue

            with open(fragment_path, "rb") as fragment:
                output.write(fragment.read())


def calculate_chain_confidence(chain, pair_df):
    """
    Calculate average relationship confidence
    across the chain.
    """

    probabilities = []

    for i in range(len(chain) - 1):

        fragment_a = chain[i]
        fragment_b = chain[i + 1]

        matches = pair_df[
            (pair_df["fragment_a"] == fragment_a)
            &
            (pair_df["fragment_b"] == fragment_b)
        ]

        if len(matches) == 0:
            continue

        probability = float(
            matches.iloc[0]["relationship_probability"]
        )

        probabilities.append(probability)

    if not probabilities:
        return 0.0

    return float(np.mean(probabilities))


def main():

    parser = argparse.ArgumentParser(
        description="ReFrag AI Reconstruction Engine"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="Minimum relationship probability",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for reconstructed files",
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("======================================")
    print("       ReFrag AI Reconstruction")
    print("======================================")
    print()

    print(f"Relationship threshold: {args.threshold:.2f}")
    print()

    # --------------------------------------------------
    # Load model
    # --------------------------------------------------

    model = load_model()

    # --------------------------------------------------
    # Load pair features
    # --------------------------------------------------

    pair_df = load_pair_features()

    print(
        f"Loaded {len(pair_df)} fragment relationships."
    )

    # --------------------------------------------------
    # Calculate relationship probabilities
    # --------------------------------------------------

    pair_df = calculate_relationships(
        model,
        pair_df,
    )

    print("Relationship probabilities calculated.")

    # --------------------------------------------------
    # Build fragment chains
    # --------------------------------------------------

    chains = build_chains(
        pair_df,
        args.threshold,
    )

    print()
    print(
        f"Candidate chains found: {len(chains)}"
    )

    # --------------------------------------------------
    # Reconstruct files
    # --------------------------------------------------

    reconstruction_results = []

    for index, chain in enumerate(chains, start=1):

        output_path = (
            output_dir /
            f"reconstructed_{index:03d}.bin"
        )

        reconstruct_chain(
            chain,
            FRAGMENTS_DIR,
            output_path,
        )

        confidence = calculate_chain_confidence(
            chain,
            pair_df,
        )

        result = {
            "reconstruction_id": index,
            "fragment_count": len(chain),
            "confidence": confidence,
            "output_file": str(output_path),
            "fragments": chain,
        }

        reconstruction_results.append(result)

        print()
        print(f"Reconstruction {index}")
        print("----------------------")
        print(f"Fragments : {len(chain)}")
        print(f"Confidence: {confidence:.2%}")
        print(f"Output    : {output_path}")

    # --------------------------------------------------
    # Save reconstruction results
    # --------------------------------------------------

    results = []

    for result in reconstruction_results:

        results.append(
            {
                "reconstruction_id":
                    result["reconstruction_id"],

                "fragment_count":
                    result["fragment_count"],

                "confidence":
                    result["confidence"],

                "output_file":
                    result["output_file"],
            }
        )

    results_df = pd.DataFrame(results)

    results_path = (
        output_dir /
        "reconstruction_results.csv"
    )

    results_df.to_csv(
        results_path,
        index=False,
    )

    print()
    print("--------------------------------------")
    print(
        f"Saved results: {results_path}"
    )
    print(
        f"Total reconstructions: "
        f"{len(reconstruction_results)}"
    )
    print("--------------------------------------")


if __name__ == "__main__":
    main()