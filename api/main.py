import os
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="ReFrag AI API",
    description="AI-assisted digital evidence recovery API",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    "ml",
    "reconstructed",
    "reconstruction_results.csv",
)

INTEGRITY_FILE = os.path.join(
    BASE_DIR,
    "ml",
    "integrity",
    "integrity_results.csv",
)

PRIORITIZATION_FILE = os.path.join(
    BASE_DIR,
    "ml",
    "prioritization",
    "evidence_prioritized.csv",
)

FRAGMENT_FILE = os.path.join(
    BASE_DIR,
    "ml",
    "features",
    "extracted_features.csv",
)


# =========================================================
# HELPERS
# =========================================================

def load_csv(path):

    if not os.path.exists(path):
        return pd.DataFrame()

    return pd.read_csv(path)


def dataframe_to_records(df):

    if df.empty:
        return []

    return df.where(
        pd.notnull(df),
        None
    ).to_dict(
        orient="records"
    )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "success": True,
        "name": "ReFrag AI",
        "message": "Digital evidence recovery API is running",
        "version": "1.0.0",
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/api/health")
def health():

    return {
        "success": True,
        "status": "online",
    }


# =========================================================
# DASHBOARD
# =========================================================

@app.get("/api/dashboard")
def dashboard():

    reconstruction = load_csv(
        RECONSTRUCTION_FILE
    )

    integrity = load_csv(
        INTEGRITY_FILE
    )

    prioritization = load_csv(
        PRIORITIZATION_FILE
    )

    fragments = load_csv(
        FRAGMENT_FILE
    )

    valid = 0
    partial = 0
    corrupted = 0

    if not integrity.empty:

        status_column = None

        for column in [
            "integrity_status",
            "status",
        ]:

            if column in integrity.columns:
                status_column = column
                break

        if status_column:

            statuses = (
                integrity[status_column]
                .astype(str)
                .str.lower()
            )

            valid = int(
                (statuses == "valid").sum()
            )

            partial = int(
                (statuses == "partial").sum()
            )

            corrupted = int(
                (statuses == "corrupted").sum()
            )

    high = 0
    medium = 0
    low = 0

    if not prioritization.empty:

        if "priority" in prioritization.columns:

            priorities = (
                prioritization["priority"]
                .astype(str)
                .str.upper()
            )

            high = int(
                (priorities == "HIGH").sum()
            )

            medium = int(
                (priorities == "MEDIUM").sum()
            )

            low = int(
                (priorities == "LOW").sum()
            )

    return {
        "success": True,

        "statistics": {
            "total_fragments": len(fragments),
            "reconstruction_candidates": len(
                reconstruction
            ),
            "valid_evidence": valid,
            "partial_evidence": partial,
            "corrupted_evidence": corrupted,
            "high_priority": high,
            "medium_priority": medium,
            "low_priority": low,
        },
    }


# =========================================================
# EVIDENCE
# =========================================================

@app.get("/api/evidence")
def evidence():

    df = load_csv(
        PRIORITIZATION_FILE
    )

    return {
        "success": True,
        "count": len(df),
        "evidence": dataframe_to_records(df),
    }


# =========================================================
# TOP EVIDENCE
# =========================================================

@app.get("/api/evidence/top")
def top_evidence():

    df = load_csv(
        PRIORITIZATION_FILE
    )

    if df.empty:
        return {
            "success": True,
            "evidence": [],
        }

    if "priority_score" in df.columns:

        df = df.sort_values(
            "priority_score",
            ascending=False,
        )

    df = df.head(10)

    return {
        "success": True,
        "evidence": dataframe_to_records(df),
    }


# =========================================================
# FRAGMENTS
# =========================================================

@app.get("/api/fragments")
def fragments():

    df = load_csv(
        FRAGMENT_FILE
    )

    return {
        "success": True,
        "count": len(df),
        "fragments": dataframe_to_records(
            df.head(500)
        ),
    }


# =========================================================
# ANALYTICS
# =========================================================

@app.get("/api/analytics")
def analytics():

    integrity = load_csv(
        INTEGRITY_FILE
    )

    prioritization = load_csv(
        PRIORITIZATION_FILE
    )

    result = {
        "success": True,
        "integrity": {},
        "priority": {},
    }

    if not integrity.empty:

        status_column = None

        for column in [
            "integrity_status",
            "status",
        ]:

            if column in integrity.columns:
                status_column = column
                break

        if status_column:

            result["integrity"] = (
                integrity[status_column]
                .astype(str)
                .str.lower()
                .value_counts()
                .to_dict()
            )

    if not prioritization.empty:

        if "priority" in prioritization.columns:

            result["priority"] = (
                prioritization["priority"]
                .astype(str)
                .str.upper()
                .value_counts()
                .to_dict()
            )

    return result


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )