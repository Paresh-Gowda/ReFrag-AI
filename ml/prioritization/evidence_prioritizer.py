import os
import json
import argparse
import pandas as pd


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

RECONSTRUCTION_FILE = os.path.join(
    BASE_DIR,
    "reconstructed",
    "reconstruction_results.csv"
)

INTEGRITY_FILE = os.path.join(
    BASE_DIR,
    "integrity",
    "integrity_results.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "prioritization"
)

OUTPUT_CSV = os.path.join(
    OUTPUT_DIR,
    "evidence_prioritized.csv"
)

OUTPUT_JSON = os.path.join(
    OUTPUT_DIR,
    "evidence_prioritized.json"
)


# =========================================================
# CONFIGURATION
# =========================================================

INTEGRITY_WEIGHTS = {
    "valid": 1.00,
    "partial": 0.60,
    "corrupted": 0.20,
    "unknown": 0.00,
}

PRIORITY_THRESHOLDS = {
    "high": 85,
    "medium": 60,
}


# =========================================================
# HELPERS
# =========================================================

def normalize_filename(value):
    """
    Convert any file path into a clean filename.

    Handles both:
        C:\\folder\\file.bin
    and:
        /folder/file.bin
    """

    value = str(value).strip()

    # Normalize Windows separators
    value = value.replace("\\", "/")

    return value.split("/")[-1]


def find_column(df, candidates):
    """
    Find a dataframe column using several possible names.
    """

    column_map = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:

        candidate = candidate.lower()

        if candidate in column_map:
            return column_map[candidate]

    return None


def get_status_score(status):
    """
    Convert integrity status into a 0-1 score.
    """

    status = str(status).strip().lower()

    return INTEGRITY_WEIGHTS.get(
        status,
        INTEGRITY_WEIGHTS["unknown"]
    )


def get_priority(score):
    """
    Convert numerical priority score into a category.
    """

    if score >= PRIORITY_THRESHOLDS["high"]:
        return "HIGH"

    if score >= PRIORITY_THRESHOLDS["medium"]:
        return "MEDIUM"

    return "LOW"


def generate_reason(row):
    """
    Generate an explainable reason for the priority.
    """

    status = str(
        row["integrity_status"]
    ).strip().upper()

    confidence = float(
        row["reconstruction_confidence"]
    )

    fragments = int(
        row["fragment_count"]
    )

    reasons = []

    # Integrity
    if status == "VALID":

        reasons.append(
            "integrity validation passed"
        )

    elif status == "PARTIAL":

        reasons.append(
            "partial integrity validation"
        )

    elif status == "CORRUPTED":

        reasons.append(
            "integrity validation failed"
        )

    else:

        reasons.append(
            "integrity status unavailable"
        )

    # Reconstruction confidence
    if confidence >= 0.90:

        reasons.append(
            "very high reconstruction confidence"
        )

    elif confidence >= 0.75:

        reasons.append(
            "high reconstruction confidence"
        )

    elif confidence >= 0.50:

        reasons.append(
            "moderate reconstruction confidence"
        )

    else:

        reasons.append(
            "low reconstruction confidence"
        )

    # Fragment support
    if fragments >= 20:

        reasons.append(
            "large reconstructed fragment chain"
        )

    elif fragments >= 10:

        reasons.append(
            "substantial reconstructed fragment chain"
        )

    else:

        reasons.append(
            "small reconstructed fragment chain"
        )

    return "; ".join(reasons)


# =========================================================
# LOAD DATA
# =========================================================

def load_data():

    if not os.path.exists(
        RECONSTRUCTION_FILE
    ):

        raise FileNotFoundError(
            "Reconstruction results not found:\n"
            f"{RECONSTRUCTION_FILE}"
        )

    if not os.path.exists(
        INTEGRITY_FILE
    ):

        raise FileNotFoundError(
            "Integrity results not found:\n"
            f"{INTEGRITY_FILE}"
        )

    reconstruction_df = pd.read_csv(
        RECONSTRUCTION_FILE
    )

    integrity_df = pd.read_csv(
        INTEGRITY_FILE
    )

    print(
        f"Loaded reconstruction results : "
        f"{len(reconstruction_df)}"
    )

    print(
        f"Loaded integrity results      : "
        f"{len(integrity_df)}"
    )

    return reconstruction_df, integrity_df


# =========================================================
# PREPARE DATA
# =========================================================

def prepare_data(
    reconstruction_df,
    integrity_df
):

    # -----------------------------------------------------
    # Find reconstruction filename column
    # -----------------------------------------------------

    recon_file_col = find_column(
        reconstruction_df,
        [
            "output_file",
            "file",
            "filename",
            "reconstructed_file",
        ]
    )

    if recon_file_col is None:

        raise ValueError(
            "Could not find reconstruction "
            "filename column.\n"
            f"Available columns: "
            f"{list(reconstruction_df.columns)}"
        )

    reconstruction_df = reconstruction_df.rename(
        columns={
            recon_file_col: "file"
        }
    )


    # -----------------------------------------------------
    # Find integrity filename column
    # -----------------------------------------------------

    integrity_file_col = find_column(
        integrity_df,
        [
            "file",
            "filename",
            "output_file",
            "reconstructed_file",
        ]
    )

    if integrity_file_col is None:

        raise ValueError(
            "Could not find integrity "
            "filename column.\n"
            f"Available columns: "
            f"{list(integrity_df.columns)}"
        )

    integrity_df = integrity_df.rename(
        columns={
            integrity_file_col: "file"
        }
    )


    # -----------------------------------------------------
    # Find reconstruction confidence
    # -----------------------------------------------------

    confidence_col = find_column(
        reconstruction_df,
        [
            "average_confidence",
            "avg_confidence",
            "confidence",
            "reconstruction_confidence",
        ]
    )

    if confidence_col is None:

        raise ValueError(
            "Could not find reconstruction "
            "confidence column.\n"
            f"Available columns: "
            f"{list(reconstruction_df.columns)}"
        )

    reconstruction_df = reconstruction_df.rename(
        columns={
            confidence_col:
            "reconstruction_confidence"
        }
    )


    # -----------------------------------------------------
    # Find fragment count
    # -----------------------------------------------------

    fragment_col = find_column(
        reconstruction_df,
        [
            "fragment_count",
            "fragments",
            "num_fragments",
            "number_of_fragments",
        ]
    )

    if fragment_col is None:

        raise ValueError(
            "Could not find fragment count column.\n"
            f"Available columns: "
            f"{list(reconstruction_df.columns)}"
        )

    reconstruction_df = reconstruction_df.rename(
        columns={
            fragment_col:
            "fragment_count"
        }
    )


    # -----------------------------------------------------
    # Find integrity status
    # -----------------------------------------------------

    status_col = find_column(
        integrity_df,
        [
            "status",
            "integrity_status",
            "validation_status",
        ]
    )

    if status_col is None:

        raise ValueError(
            "Could not find integrity status column.\n"
            f"Available columns: "
            f"{list(integrity_df.columns)}"
        )

    integrity_df = integrity_df.rename(
        columns={
            status_col:
            "integrity_status"
        }
    )


    # -----------------------------------------------------
    # NORMALIZE FILENAMES
    # -----------------------------------------------------

    reconstruction_df["file_key"] = (
        reconstruction_df["file"]
        .apply(normalize_filename)
    )

    integrity_df["file_key"] = (
        integrity_df["file"]
        .apply(normalize_filename)
    )


    # -----------------------------------------------------
    # DEBUG INFORMATION
    # -----------------------------------------------------

    print()
    print("Filename matching check:")
    print(
        f"Reconstruction unique files : "
        f"{reconstruction_df['file_key'].nunique()}"
    )

    print(
        f"Integrity unique files      : "
        f"{integrity_df['file_key'].nunique()}"
    )


    # -----------------------------------------------------
    # KEEP USEFUL INTEGRITY COLUMNS
    # -----------------------------------------------------

    integrity_columns = [
        "file_key",
        "integrity_status",
    ]

    optional_columns = [
        "file_type",
        "detected_type",
        "size",
        "reason",
        "validation_message",
    ]

    for column in optional_columns:

        if column in integrity_df.columns:

            integrity_columns.append(
                column
            )

    integrity_clean = integrity_df[
        integrity_columns
    ].copy()


    # -----------------------------------------------------
    # REMOVE DUPLICATE INTEGRITY RECORDS
    # -----------------------------------------------------

    integrity_clean = (
        integrity_clean
        .drop_duplicates(
            subset=["file_key"],
            keep="first"
        )
    )


    # -----------------------------------------------------
    # MERGE
    # -----------------------------------------------------

    merged = pd.merge(
        reconstruction_df,
        integrity_clean,
        on="file_key",
        how="left",
        suffixes=(
            "",
            "_integrity"
        )
    )


    # -----------------------------------------------------
    # CLEAN FINAL FILENAME
    # -----------------------------------------------------

    merged["file"] = (
        merged["file_key"]
        .astype(str)
    )


    # -----------------------------------------------------
    # HANDLE MISSING INTEGRITY
    # -----------------------------------------------------

    merged["integrity_status"] = (
        merged["integrity_status"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
        .str.lower()
    )


    # -----------------------------------------------------
    # NUMERIC CLEANUP
    # -----------------------------------------------------

    merged["reconstruction_confidence"] = (
        pd.to_numeric(
            merged["reconstruction_confidence"],
            errors="coerce"
        )
        .fillna(0.0)
        .clip(0, 1)
    )

    merged["fragment_count"] = (
        pd.to_numeric(
            merged["fragment_count"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )


    # -----------------------------------------------------
    # MERGE VALIDATION
    # -----------------------------------------------------

    matched = (
        merged["integrity_status"]
        != "unknown"
    ).sum()

    unmatched = (
        merged["integrity_status"]
        == "unknown"
    ).sum()

    print(
        f"Integrity matches           : "
        f"{matched}"
    )

    print(
        f"Integrity unmatched         : "
        f"{unmatched}"
    )

    if matched == 0:

        print()
        print(
            "WARNING: No integrity records "
            "matched reconstruction files."
        )

        print(
            "Check the filenames in:"
        )

        print(
            INTEGRITY_FILE
        )

    return merged


# =========================================================
# PRIORITIZATION ENGINE
# =========================================================

def prioritize(df):

    # -----------------------------------------------------
    # 1. INTEGRITY SCORE
    # -----------------------------------------------------

    integrity_score = (
        df["integrity_status"]
        .apply(get_status_score)
        * 100
    )


    # -----------------------------------------------------
    # 2. RECONSTRUCTION CONFIDENCE
    # -----------------------------------------------------

    reconstruction_score = (
        df["reconstruction_confidence"]
        .clip(0, 1)
        * 100
    )


    # -----------------------------------------------------
    # 3. FRAGMENT CHAIN SUPPORT
    # -----------------------------------------------------

    fragment_score = (
        df["fragment_count"]
        .clip(
            lower=0,
            upper=20
        )
        / 20
        * 100
    )


    # -----------------------------------------------------
    # FINAL SCORE
    # -----------------------------------------------------
    #
    # Integrity      = 60%
    # Reconstruction = 30%
    # Fragment count = 10%
    #

    priority_score = (
        integrity_score * 0.60
        + reconstruction_score * 0.30
        + fragment_score * 0.10
    )


    # -----------------------------------------------------
    # STORE COMPONENT SCORES
    # -----------------------------------------------------

    df["integrity_score"] = (
        integrity_score.round(2)
    )

    df["reconstruction_score"] = (
        reconstruction_score.round(2)
    )

    df["fragment_score"] = (
        fragment_score.round(2)
    )

    df["priority_score"] = (
        priority_score.round(2)
    )


    # -----------------------------------------------------
    # PRIORITY CATEGORY
    # -----------------------------------------------------

    df["priority"] = (
        df["priority_score"]
        .apply(get_priority)
    )


    # -----------------------------------------------------
    # EXPLANATION
    # -----------------------------------------------------

    df["explanation"] = (
        df.apply(
            generate_reason,
            axis=1
        )
    )


    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    df = (
        df.sort_values(
            by="priority_score",
            ascending=False
        )
        .reset_index(drop=True)
    )


    # -----------------------------------------------------
    # RANK
    # -----------------------------------------------------

    df.insert(
        0,
        "priority_rank",
        range(
            1,
            len(df) + 1
        )
    )


    return df


# =========================================================
# SAVE RESULTS
# =========================================================

def save_results(df):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


    # CSV
    df.to_csv(
        OUTPUT_CSV,
        index=False
    )


    # JSON
    records = df.to_dict(
        orient="records"
    )

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            default=str
        )


    print()
    print("Results saved:")
    print(
        f"CSV  : {OUTPUT_CSV}"
    )
    print(
        f"JSON : {OUTPUT_JSON}"
    )


# =========================================================
# SUMMARY
# =========================================================

def print_summary(
    df,
    top_n=10
):

    print()
    print("=" * 65)
    print(
        "REFRAG AI - EVIDENCE PRIORITIZATION"
    )
    print("=" * 65)

    print(
        f"Total evidence candidates : "
        f"{len(df)}"
    )


    high = (
        df["priority"] == "HIGH"
    ).sum()

    medium = (
        df["priority"] == "MEDIUM"
    ).sum()

    low = (
        df["priority"] == "LOW"
    ).sum()


    print(
        f"HIGH priority             : "
        f"{high}"
    )

    print(
        f"MEDIUM priority           : "
        f"{medium}"
    )

    print(
        f"LOW priority              : "
        f"{low}"
    )


    print()
    print(
        "Integrity distribution:"
    )

    print(
        df["integrity_status"]
        .value_counts()
        .to_string()
    )


    print()
    print(
        "Top evidence candidates:"
    )

    print("-" * 65)


    columns = [
        "priority_rank",
        "file",
        "integrity_status",
        "fragment_count",
        "reconstruction_confidence",
        "priority_score",
        "priority",
    ]


    available_columns = [
        column
        for column in columns
        if column in df.columns
    ]


    print(
        df[available_columns]
        .head(top_n)
        .to_string(
            index=False
        )
    )


    print()
    print(
        "Priority explanations:"
    )

    print("-" * 65)


    explanation_columns = [
        "priority_rank",
        "file",
        "priority",
        "explanation",
    ]


    print(
        df[explanation_columns]
        .head(top_n)
        .to_string(
            index=False
        )
    )


# =========================================================
# MAIN
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "ReFrag AI Evidence "
            "Prioritization Engine"
        )
    )


    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help=(
            "Number of top evidence "
            "candidates to display"
        )
    )


    args = parser.parse_args()


    # Load
    reconstruction_df, integrity_df = (
        load_data()
    )


    # Prepare + merge
    df = prepare_data(
        reconstruction_df,
        integrity_df
    )


    # Prioritize
    df = prioritize(
        df
    )


    # Save
    save_results(
        df
    )


    # Display
    print_summary(
        df,
        args.top
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()