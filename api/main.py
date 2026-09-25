import os
import sys
import subprocess

import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ml.live_recovery import analyze_bytes

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
    """Safely load a CSV file."""

    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        return pd.read_csv(path)

    except Exception:
        return pd.DataFrame()


def dataframe_to_records(df):
    """Convert dataframe into JSON-safe records."""

    if df.empty:
        return []

    return (
        df.where(
            pd.notnull(df),
            None
        )
        .to_dict(
            orient="records"
        )
    )


def run_pipeline_step(name, command):
    """Run one ML pipeline step."""

    print(f"\n[SCAN] {name}")

    process = subprocess.run(
        command,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        return {
            "success": False,
            "name": name,
            "output": process.stdout[-3000:],
            "error": (
                process.stderr
                or process.stdout
                or "Unknown error"
            ),
        }

    return {
        "success": True,
        "name": name,
        "output": process.stdout[-3000:],
    }


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "success": True,
        "name": "ReFrag AI",
        "message": (
            "Digital evidence recovery API "
            "is running"
        ),
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

    # -----------------------------------------------------
    # Integrity statistics
    # -----------------------------------------------------

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
                .str.strip()
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

    # -----------------------------------------------------
    # Priority statistics
    # -----------------------------------------------------

    high = 0
    medium = 0
    low = 0

    if not prioritization.empty:

        if "priority" in prioritization.columns:

            priorities = (
                prioritization["priority"]
                .astype(str)
                .str.strip()
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

            "total_fragments": len(
                fragments
            ),

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
            "count": 0,
            "evidence": [],
        }

    if "priority_score" in df.columns:

        df["priority_score"] = pd.to_numeric(
            df["priority_score"],
            errors="coerce"
        )

        df = df.sort_values(
            by="priority_score",
            ascending=False,
        )

    df = df.head(10)

    return {
        "success": True,
        "count": len(df),
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

    # -----------------------------------------------------
    # Integrity analytics
    # -----------------------------------------------------

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
                .str.strip()
                .str.lower()
                .value_counts()
                .to_dict()
            )

    # -----------------------------------------------------
    # Priority analytics
    # -----------------------------------------------------

    if not prioritization.empty:

        if "priority" in prioritization.columns:

            result["priority"] = (
                prioritization["priority"]
                .astype(str)
                .str.strip()
                .str.upper()
                .value_counts()
                .to_dict()
            )

    return result


# =========================================================
# SCAN PIPELINE
# =========================================================

# =========================================================
# FILE SCAN
# =========================================================

def detect_file_type(data):

    if data.startswith(b"\xff\xd8\xff"):
        return "JPEG"

    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"

    if data.startswith(b"%PDF"):
        return "PDF"

    if data.startswith(b"PK"):
        return "ZIP"

    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "GIF"

    return "UNKNOWN"


def calculate_entropy(data):

    if not data:
        return 0.0

    import math

    counts = [0] * 256

    for byte in data:
        counts[byte] += 1

    entropy = 0.0

    for count in counts:

        if count == 0:
            continue

        probability = count / len(data)

        entropy -= (
            probability *
            math.log2(probability)
        )

    return round(entropy, 4)


def check_integrity(file_type, data):

    if not data:
        return "CORRUPTED"

    if file_type == "JPEG":

        if (
            data.startswith(b"\xff\xd8\xff")
            and data.endswith(b"\xff\xd9")
        ):
            return "VALID"

        return "PARTIAL"

    if file_type == "PNG":

        if (
            data.startswith(
                b"\x89PNG\r\n\x1a\n"
            )
            and data.endswith(
                b"IEND\xaeB`\x82"
            )
        ):
            return "VALID"

        return "PARTIAL"

    if file_type == "PDF":

        if (
            data.startswith(b"%PDF")
            and b"%%EOF" in data[-1024:]
        ):
            return "VALID"

        return "PARTIAL"

    if file_type == "ZIP":

        if (
            data.startswith(b"PK")
            and (
                b"PK\x05\x06" in data[-1024:]
                or b"PK\x01\x02" in data[-1024:]
            )
        ):
            return "VALID"

        return "PARTIAL"

    return "UNKNOWN"


@app.post("/api/scan")
async def run_scan(
    file: UploadFile = File(...)
):

    try:

        # -------------------------------------------------
        # Read uploaded evidence
        # -------------------------------------------------

        data = await file.read()

        if not data:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Uploaded file is empty."
                }
            )

        # -------------------------------------------------
        # File analysis
        # -------------------------------------------------

        file_type = detect_file_type(data)

        entropy = calculate_entropy(data)

        integrity = check_integrity(
            file_type,
            data
        )

        # -------------------------------------------------
        # Fragment analysis
        # -------------------------------------------------

        fragment_size = 4096

        fragments = []

        for offset in range(
            0,
            len(data),
            fragment_size
        ):

            chunk = data[
                offset:
                offset + fragment_size
            ]

            fragments.append({

                "fragment_id":
                    len(fragments) + 1,

                "offset":
                    offset,

                "size":
                    len(chunk),

                "entropy":
                    calculate_entropy(chunk),
            })

        # -------------------------------------------------
        # Recovery confidence
        # -------------------------------------------------

        if integrity == "VALID":

            confidence = 0.98

        elif integrity == "PARTIAL":

            confidence = 0.72

        elif integrity == "CORRUPTED":

            confidence = 0.35

        else:

            confidence = 0.20

        # -------------------------------------------------
        # Evidence priority
        # -------------------------------------------------

        if integrity == "VALID":

            priority = "HIGH"

        elif integrity == "PARTIAL":

            priority = "MEDIUM"

        else:

            priority = "LOW"

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return {

            "success": True,

            "message":
                "File processed successfully.",

            "file": {

                "name":
                    file.filename,

                "size":
                    len(data),

                "type":
                    file_type,
            },

            "analysis": {

                "fragment_count":
                    len(fragments),

                "fragment_size":
                    fragment_size,

                "entropy":
                    entropy,

                "integrity":
                    integrity,

                "reconstruction_confidence":
                    confidence,

                "priority":
                    priority,
            },

            "fragments":
                fragments[:100],
        }

    except Exception as error:

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "message":
                    "File processing failed.",

                "error":
                    str(error),
            }
        )