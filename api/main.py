# api/main.py

from pathlib import Path
from typing import Any, Dict, List, Optional

import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from ml.live_recovery import analyze_bytes
from ml.image_recovery.visual_recovery_pipeline import run_visual_recovery


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="ReFrag AI API",
    description=(
        "AI-Assisted Intelligent Data Recovery "
        "and Digital Evidence Reconstruction"
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ML_DIR = BASE_DIR / "ml"

IMAGE_RECOVERY_DIR = (
    ML_DIR / "image_recovery"
)

IMAGE_REFERENCE_DIR = (
    IMAGE_RECOVERY_DIR
    / "reference_database"
    / "clean"
)

VISUAL_OUTPUT_DIR = (
    IMAGE_RECOVERY_DIR
    / "test"
    / "output"
    / "api_recovery"
)

UPLOAD_DIR = (
    IMAGE_RECOVERY_DIR
    / "test"
    / "uploads"
)


VISUAL_OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LIVE SESSION
# ============================================================

LIVE_SCAN: Dict[str, Any] = {
    "active": False,
    "mode": None,
    "file": None,
    "file_info": None,
    "analysis": None,
}

VISUAL_RESULT: Optional[Dict[str, Any]] = None


# ============================================================
# CONSTANT OUTPUT URLS
# ============================================================

VISUAL_OUTPUTS = {
    "reference_image":
        "/api/image-recovery/output/reference.jpg",

    "damage_mask":
        "/api/image-recovery/output/damage_mask.png",

    "evidence_map":
        "/api/image-recovery/output/evidence_map.png",

    "restored_image":
        "/api/image-recovery/output/restored_image.png",
}


# ============================================================
# HELPERS
# ============================================================

def safe_number(
    value: Any,
    default: float = 0
) -> float:

    try:
        return float(value)
    except (
        TypeError,
        ValueError
    ):
        return default


def safe_int(
    value: Any,
    default: int = 0
) -> int:

    try:
        return int(value)
    except (
        TypeError,
        ValueError
    ):
        return default


def empty_statistics():

    return {
        "total_fragments": 0,
        "reconstruction_candidates": 0,
        "valid_evidence": 0,
        "partial_evidence": 0,
        "corrupted_evidence": 0,
        "high_priority": 0,
        "medium_priority": 0,
        "low_priority": 0,
        "recovery_rate": 0,
    }


def current_analysis():

    return LIVE_SCAN.get(
        "analysis"
    )


def current_fragments():

    analysis = current_analysis()

    if not analysis:
        return []

    fragments = analysis.get(
        "fragments",
        []
    )

    if not isinstance(
        fragments,
        list
    ):
        return []

    return fragments


def current_relationships():

    analysis = current_analysis()

    if not analysis:
        return []

    relationships = analysis.get(
        "relationships",
        []
    )

    if not isinstance(
        relationships,
        list
    ):
        return []

    return relationships


def get_integrity(
    analysis
):

    result = {
        "valid": 0,
        "partial": 0,
        "corrupted": 0,
    }

    if not analysis:
        return result

    status = str(
        analysis.get(
            "integrity",
            "unknown"
        )
    ).lower()

    if status in result:
        result[status] = 1

    return result


def get_priority(
    analysis
):

    result = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }

    if not analysis:
        return result

    priority = str(
        analysis.get(
            "priority",
            "LOW"
        )
    ).upper()

    if priority in result:
        result[priority] = 1

    return result


def build_statistics(
    analysis
):

    stats = empty_statistics()

    if not analysis:
        return stats

    fragments = current_fragments()

    integrity = get_integrity(
        analysis
    )

    priority = get_priority(
        analysis
    )

    total_fragments = safe_int(
        analysis.get(
            "fragment_count",
            len(fragments)
        )
    )

    reconstructed_count = safe_int(
        analysis.get(
            "reconstruction_fragment_count",
            0
        )
    )

    recovery_confidence = safe_number(
        analysis.get(
            "reconstruction_confidence",
            0
        )
    )

    stats[
        "total_fragments"
    ] = total_fragments

    stats[
        "reconstruction_candidates"
    ] = (
        1
        if reconstructed_count > 0
        else 0
    )

    stats[
        "valid_evidence"
    ] = integrity["valid"]

    stats[
        "partial_evidence"
    ] = integrity["partial"]

    stats[
        "corrupted_evidence"
    ] = integrity["corrupted"]

    stats[
        "high_priority"
    ] = priority["HIGH"]

    stats[
        "medium_priority"
    ] = priority["MEDIUM"]

    stats[
        "low_priority"
    ] = priority["LOW"]

    stats[
        "recovery_rate"
    ] = round(
        recovery_confidence,
        2
    )

    return stats


def normalize_fragment(
    fragment,
    index
):

    result = dict(fragment)

    result.setdefault(
        "fragment_id",
        f"FRAG_{index + 1:06d}"
    )

    result.setdefault(
        "index",
        index
    )

    result.setdefault(
        "confidence",
        result.get(
            "classification_confidence",
            0
        )
    )

    return result


def normalize_relationship(
    relationship,
    index
):

    result = dict(
        relationship
    )

    result.setdefault(
        "relationship_id",
        f"REL_{index + 1:06d}"
    )

    result.setdefault(
        "confidence",
        result.get(
            "probability",
            0
        )
    )

    return result


# ============================================================
# VISUAL HELPERS
# ============================================================

def extract_visual_metrics(
    result
):

    reference_match = (
        result.get(
            "reference_match",
            {}
        )
        if isinstance(result, dict)
        else {}
    )

    damage_analysis = (
        result.get(
            "damage_analysis",
            {}
        )
        if isinstance(result, dict)
        else {}
    )

    similarity = safe_number(
        reference_match.get(
            "similarity_percent",
            reference_match.get(
                "similarity",
                0
            )
        )
    )

    recovered = safe_number(
        damage_analysis.get(
            "recovered_percent",
            damage_analysis.get(
                "recovered_percentage",
                0
            )
        )
    )

    damaged = safe_number(
        damage_analysis.get(
            "damaged_percent",
            damage_analysis.get(
                "damaged_percentage",
                0
            )
        )
    )

    regions = safe_int(
        damage_analysis.get(
            "damage_regions",
            damage_analysis.get(
                "regions",
                0
            )
        )
    )

    reference_name = (
        reference_match.get(
            "reference_filename"
        )
        or reference_match.get(
            "filename"
        )
        or reference_match.get(
            "reference_name"
        )
    )

    return {
        "similarity": similarity,
        "recovered_percentage": recovered,
        "damaged_percentage": damaged,
        "damage_regions": regions,
        "reference_name": reference_name,
    }


def visual_integrity(
    damaged_percentage
):

    if damaged_percentage < 10:
        return "valid"

    if damaged_percentage < 50:
        return "partial"

    return "corrupted"


def visual_priority(
    similarity
):

    if similarity >= 85:
        return "HIGH"

    if similarity >= 60:
        return "MEDIUM"

    return "LOW"


def build_visual_analysis(
    result,
    filename,
    extension,
    reference_path
):

    metrics = extract_visual_metrics(
        result
    )

    similarity = metrics[
        "similarity"
    ]

    recovered = metrics[
        "recovered_percentage"
    ]

    damaged = metrics[
        "damaged_percentage"
    ]

    regions = metrics[
        "damage_regions"
    ]

    reference_name = (
        metrics["reference_name"]
        or (
            reference_path.name
            if reference_path
            else None
        )
    )

    priority = visual_priority(
        similarity
    )

    integrity = visual_integrity(
        damaged
    )

    return {

        # -------------------------------
        # MODE
        # -------------------------------

        "mode": "visual",

        "visual_recovery": True,

        # -------------------------------
        # FILE
        # -------------------------------

        "file_type":
            extension
            .replace(".", "")
            .upper(),

        # -------------------------------
        # BYTE PIPELINE
        # -------------------------------

        "fragment_count": 0,

        "fragment_size": 0,

        "fragments": [],

        "relationships": [],

        "relationships_analyzed": 0,

        "strong_relationships": 0,

        "reconstruction_fragment_count": 0,

        "reconstruction_confidence":
            similarity,

        # -------------------------------
        # VISUAL RECOVERY
        # -------------------------------

        "similarity":
            similarity,

        "reference_similarity":
            similarity,

        "reference_name":
            reference_name,

        "matched_reference":
            reference_name,

        "recovered_percentage":
            recovered,

        "damaged_percentage":
            damaged,

        "damage_regions":
            regions,

        # -------------------------------
        # INTEGRITY
        # -------------------------------

        "integrity":
            integrity,

        "integrity_reason": (
            "Visual recovery completed "
            "using reference-assisted "
            "reconstruction. Integrity "
            "status represents the "
            "observed damage level and "
            "is not an authenticity "
            "determination."
        ),

        # -------------------------------
        # PRIORITY
        # -------------------------------

        "priority":
            priority,

        "priority_score":
            similarity,

        # -------------------------------
        # ANALYTICS
        # -------------------------------

        "entropy": 0,

        # -------------------------------
        # OUTPUTS
        # -------------------------------

        "outputs":
            VISUAL_OUTPUTS,

        # -------------------------------
        # ORIGINAL PIPELINE RESULT
        # -------------------------------

        "visual_result":
            result,
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name": "ReFrag AI",
        "status": "online",
        "version": "1.0.0",
        "system":
            "AI-Assisted Digital Evidence Recovery",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():

    return {
        "success": True,
        "status": "online",
        "service":
            "ReFrag AI API",

        "live_scan":
            LIVE_SCAN["active"],

        "mode":
            LIVE_SCAN.get(
                "mode"
            ),

        "visual_recovery":
            VISUAL_RESULT is not None,
    }


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/api/dashboard")
def dashboard():

    analysis = current_analysis()

    stats = build_statistics(
        analysis
    )

    integrity = get_integrity(
        analysis
    )

    priority = get_priority(
        analysis
    )

    if not analysis:

        return {
            "success": True,
            "active_scan": False,
            "mode": None,
            "file": None,

            "statistics":
                stats,

            "fragments": {
                "total": 0
            },

            "reconstruction": {
                "candidates": 0,
                "confidence": 0,
                "fragment_count": 0,
            },

            "integrity":
                integrity,

            "prioritization":
                priority,

            "analysis":
                None,
        }

    return {
        "success": True,

        "active_scan":
            LIVE_SCAN["active"],

        "mode":
            LIVE_SCAN.get(
                "mode"
            ),

        "file":
            LIVE_SCAN.get(
                "file"
            ),

        "file_info":
            LIVE_SCAN.get(
                "file_info"
            ),

        "total_fragments":
            stats[
                "total_fragments"
            ],

        "reconstruction_candidates":
            stats[
                "reconstruction_candidates"
            ],

        "valid_evidence":
            stats[
                "valid_evidence"
            ],

        "partial_evidence":
            stats[
                "partial_evidence"
            ],

        "corrupted_evidence":
            stats[
                "corrupted_evidence"
            ],

        "high_priority":
            stats[
                "high_priority"
            ],

        "medium_priority":
            stats[
                "medium_priority"
            ],

        "low_priority":
            stats[
                "low_priority"
            ],

        "recovery_rate":
            stats[
                "recovery_rate"
            ],

        "statistics":
            stats,

        "fragments": {
            "total":
                stats[
                    "total_fragments"
                ]
        },

        "reconstruction": {
            "candidates":
                stats[
                    "reconstruction_candidates"
                ],

            "confidence":
                safe_number(
                    analysis.get(
                        "reconstruction_confidence",
                        0
                    )
                ),

            "fragment_count":
                safe_int(
                    analysis.get(
                        "reconstruction_fragment_count",
                        0
                    )
                ),
        },

        "integrity":
            integrity,

        "prioritization":
            priority,

        "analysis":
            analysis,
    }


# ============================================================
# EVIDENCE
# ============================================================

@app.get("/api/evidence")
def evidence():

    analysis = current_analysis()

    if not analysis:

        return {
            "success": True,
            "active_scan": False,
            "mode": None,
            "file": None,
            "evidence": [],
            "total": 0,
        }

    evidence_item = {
        "id":
            "EVD-001",

        "mode":
            LIVE_SCAN.get(
                "mode"
            ),

        "visual_recovery":
            analysis.get(
                "visual_recovery",
                False
            ),

        "file":
            LIVE_SCAN.get(
                "file"
            ),

        "file_type":
            analysis.get(
                "file_type",
                "unknown"
            ),

        "fragment_count":
            analysis.get(
                "fragment_count",
                0
            ),

        "reconstruction_fragment_count":
            analysis.get(
                "reconstruction_fragment_count",
                0
            ),

        "reconstruction_confidence":
            analysis.get(
                "reconstruction_confidence",
                0
            ),

        "relationships_analyzed":
            analysis.get(
                "relationships_analyzed",
                0
            ),

        "strong_relationships":
            analysis.get(
                "strong_relationships",
                0
            ),

        "integrity":
            analysis.get(
                "integrity",
                "unknown"
            ),

        "integrity_reason":
            analysis.get(
                "integrity_reason",
                ""
            ),

        "priority":
            analysis.get(
                "priority",
                "LOW"
            ),

        "priority_score":
            analysis.get(
                "priority_score",
                0
            ),

        "reference":
            analysis.get(
                "reference_name"
            ),

        "similarity":
            analysis.get(
                "similarity",
                0
            ),

        "recovered_percentage":
            analysis.get(
                "recovered_percentage",
                0
            ),

        "damaged_percentage":
            analysis.get(
                "damaged_percentage",
                0
            ),

        "damage_regions":
            analysis.get(
                "damage_regions",
                0
            ),

        "outputs":
            analysis.get(
                "outputs",
                {}
            ),
    }

    return {
        "success": True,

        "active_scan":
            True,

        "mode":
            LIVE_SCAN.get(
                "mode"
            ),

        "file":
            LIVE_SCAN.get(
                "file"
            ),

        "evidence":
            [evidence_item],

        "total":
            1,

        "integrity":
            get_integrity(
                analysis
            ),

        "prioritization":
            get_priority(
                analysis
            ),
    }


# ============================================================
# TOP EVIDENCE
# ============================================================

@app.get("/api/evidence/top")
def top_evidence():

    analysis = current_analysis()

    if not analysis:

        return {
            "success": True,
            "active_scan": False,
            "evidence": [],
            "total": 0,
        }

    return {
        "success": True,

        "active_scan":
            True,

        "mode":
            LIVE_SCAN.get(
                "mode"
            ),

        "evidence": [
            {
                "rank": 1,

                "file":
                    LIVE_SCAN.get(
                        "file"
                    ),

                "file_type":
                    analysis.get(
                        "file_type",
                        "unknown"
                    ),

                "mode":
                    analysis.get(
                        "mode"
                    ),

                "priority":
                    analysis.get(
                        "priority",
                        "LOW"
                    ),

                "priority_score":
                    analysis.get(
                        "priority_score",
                        0
                    ),

                "integrity":
                    analysis.get(
                        "integrity",
                        "unknown"
                    ),

                "reconstruction_confidence":
                    analysis.get(
                        "reconstruction_confidence",
                        0
                    ),

                "fragment_count":
                    analysis.get(
                        "reconstruction_fragment_count",
                        0
                    ),

                "similarity":
                    analysis.get(
                        "similarity",
                        0
                    ),

                "reference":
                    analysis.get(
                        "reference_name"
                    ),

                "explanation": (
                    "Prioritized using "
                    "integrity, reconstruction "
                    "confidence and evidence "
                    "support."
                ),
            }
        ],

        "total": 1,
    }


# ============================================================
# FRAGMENTS
# ============================================================

@app.get("/api/fragments")
def fragments():

    analysis = current_analysis()

    if not analysis:

        return {
            "success": True,
            "active_scan": False,
            "mode": None,
            "file": None,
            "fragments": [],
            "relationships": [],
            "total": 0,
        }

    # --------------------------------------------------------
    # VISUAL MODE
    # --------------------------------------------------------

    if (
        LIVE_SCAN.get(
            "mode"
        )
        == "visual"
    ):

        return {
            "success": True,

            "active_scan":
                True,

            "mode":
                "visual",

            "visual_recovery":
                True,

            "file":
                LIVE_SCAN.get(
                    "file"
                ),

            "file_type":
                analysis.get(
                    "file_type",
                    "IMAGE"
                ),

            "fragment_size":
                0,

            "entropy":
                0,

            "fragments": [],

            "relationships": [],

            "total": 0,

            "relationships_analyzed":
                0,

            "strong_relationships":
                0,

            "reference":
                analysis.get(
                    "reference_name"
                ),

            "similarity":
                analysis.get(
                    "similarity",
                    0
                ),

            "recovered_percentage":
                analysis.get(
                    "recovered_percentage",
                    0
                ),

            "damaged_percentage":
                analysis.get(
                    "damaged_percentage",
                    0
                ),

            "damage_regions":
                analysis.get(
                    "damage_regions",
                    0
                ),

            "message": (
                "Visual recovery does not "
                "generate byte fragments. "
                "Image evidence is analyzed "
                "through visual similarity "
                "and reference matching."
            ),
        }

    # --------------------------------------------------------
    # FORENSIC / BYTE MODE
    # --------------------------------------------------------

    raw_fragments = (
        current_fragments()
    )

    raw_relationships = (
        current_relationships()
    )

    normalized_fragments = [
        normalize_fragment(
            fragment,
            index
        )
        for index, fragment
        in enumerate(
            raw_fragments
        )
    ]

    normalized_relationships = [
        normalize_relationship(
            relationship,
            index
        )
        for index, relationship
        in enumerate(
            raw_relationships
        )
    ]

    return {
        "success": True,

        "active_scan":
            True,

        "mode":
            "forensic",

        "visual_recovery":
            False,

        "file":
            LIVE_SCAN.get(
                "file"
            ),

        "file_type":
            analysis.get(
                "file_type",
                "unknown"
            ),

        "fragment_size":
            analysis.get(
                "fragment_size",
                4096
            ),

        "entropy":
            analysis.get(
                "entropy",
                0
            ),

        "fragments":
            normalized_fragments,

        "relationships":
            normalized_relationships,

        "total":
            len(
                normalized_fragments
            ),

        "relationships_analyzed":
            analysis.get(
                "relationships_analyzed",
                len(
                    normalized_relationships
                )
            ),

        "strong_relationships":
            analysis.get(
                "strong_relationships",
                0
            ),
    }


# ============================================================
# ANALYTICS
# ============================================================

@app.get("/api/analytics")
def analytics():

    analysis = current_analysis()

    if not analysis:

        return {
            "success": True,

            "active_scan":
                False,

            "mode":
                None,

            "file":
                None,

            "analytics": {
                "mode": None,
                "visual_recovery": False,

                "total_fragments": 0,

                "relationships_analyzed": 0,

                "strong_relationships": 0,

                "reconstruction_confidence": 0,

                "priority_score": 0,

                "entropy": 0,

                "similarity": 0,

                "recovered_percentage": 0,

                "damaged_percentage": 0,

                "damage_regions": 0,

                "reference": None,
            },

            "integrity": {
                "valid": 0,
                "partial": 0,
                "corrupted": 0,
            },

            "priority": {
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
            },
        }

    visual = (
        LIVE_SCAN.get(
            "mode"
        )
        == "visual"
    )

    analytics_data = {
        "mode":
            analysis.get(
                "mode",
                LIVE_SCAN.get(
                    "mode"
                )
            ),

        "visual_recovery":
            visual,

        "total_fragments":
            analysis.get(
                "fragment_count",
                0
            ),

        "relationships_analyzed":
            analysis.get(
                "relationships_analyzed",
                0
            ),

        "strong_relationships":
            analysis.get(
                "strong_relationships",
                0
            ),

        "reconstruction_confidence":
            analysis.get(
                "reconstruction_confidence",
                0
            ),

        "priority_score":
            analysis.get(
                "priority_score",
                0
            ),

        "entropy":
            analysis.get(
                "entropy",
                0
            ),

        "similarity":
            analysis.get(
                "similarity",
                0
            ),

        "recovered_percentage":
            analysis.get(
                "recovered_percentage",
                0
            ),

        "damaged_percentage":
            analysis.get(
                "damaged_percentage",
                0
            ),

        "damage_regions":
            analysis.get(
                "damage_regions",
                0
            ),

        "reference":
            analysis.get(
                "reference_name"
            ),
    }

    return {
        "success": True,

        "active_scan":
            True,

        "mode":
            LIVE_SCAN.get(
                "mode"
            ),

        "file":
            LIVE_SCAN.get(
                "file"
            ),

        "analytics":
            analytics_data,

        # Also expose the values at top level
        # for frontend compatibility.

        "total_fragments":
            analytics_data[
                "total_fragments"
            ],

        "relationships_analyzed":
            analytics_data[
                "relationships_analyzed"
            ],

        "strong_relationships":
            analytics_data[
                "strong_relationships"
            ],

        "reconstruction_confidence":
            analytics_data[
                "reconstruction_confidence"
            ],

        "priority_score":
            analytics_data[
                "priority_score"
            ],

        "entropy":
            analytics_data[
                "entropy"
            ],

        "visual_recovery":
            visual,

        "similarity":
            analytics_data[
                "similarity"
            ],

        "recovered_percentage":
            analytics_data[
                "recovered_percentage"
            ],

        "damaged_percentage":
            analytics_data[
                "damaged_percentage"
            ],

        "damage_regions":
            analytics_data[
                "damage_regions"
            ],

        "reference":
            analytics_data[
                "reference"
            ],

        "integrity":
            get_integrity(
                analysis
            ),

        "priority":
            get_priority(
                analysis
            ),

        "model_signals": {
            "fragment_classifier":
                not visual,

            "relationship_engine":
                not visual,

            "reconstruction_engine":
                not visual,

            "integrity_analyzer":
                True,

            "evidence_prioritizer":
                True,

            "visual_recovery":
                True,

            "reference_matching":
                True,
        },
    }


# ============================================================
# FORENSIC BYTE SCAN
# ============================================================

@app.post("/api/scan")
async def scan(
    file: UploadFile = File(...)
):

    global LIVE_SCAN
    global VISUAL_RESULT

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename supplied."
        )

    data = await file.read()

    if not data:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    try:

        analysis = analyze_bytes(
            data
        )

    except Exception as exc:

        print(
            f"[SCAN ERROR] "
            f"{file.filename}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Live recovery failed: "
                f"{exc}"
            )
        )

    # New forensic scan replaces
    # previous visual session.

    VISUAL_RESULT = None

    LIVE_SCAN = {
        "active": True,

        "mode":
            "forensic",

        "file":
            file.filename,

        "file_info": {
            "name":
                file.filename,

            "size":
                len(data),

            "content_type":
                file.content_type,
        },

        "analysis":
            analysis,
    }

    stats = build_statistics(
        analysis
    )

    return {
        "success": True,

        "message": (
            "File scanned successfully "
            "using the live ReFrag "
            "recovery engine."
        ),

        "file": {
            "name":
                file.filename,

            "size":
                len(data),

            "content_type":
                file.content_type,
        },

        "statistics":
            stats,

        "analysis":
            analysis,
    }


# ============================================================
# VISUAL IMAGE RECOVERY
# ============================================================

@app.post("/api/image-recovery")
async def image_recovery(
    file: UploadFile = File(...)
):

    global LIVE_SCAN
    global VISUAL_RESULT

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No image filename supplied."
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
    }

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported image format. "
                "Use JPG, JPEG, PNG, WEBP "
                "or BMP."
            )
        )

    data = await file.read()

    if not data:

        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty."
        )

    # --------------------------------------------------------
    # SAVE UPLOAD
    # --------------------------------------------------------

    safe_name = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    upload_path = (
        UPLOAD_DIR
        / safe_name
    )

    upload_path.write_bytes(
        data
    )

    print()
    print(
        "[VISUAL RECOVERY] "
        f"{file.filename}"
    )
    print()

    # --------------------------------------------------------
    # RUN VISUAL PIPELINE
    # --------------------------------------------------------

    try:

        result = run_visual_recovery(
            upload_path
        )

    except Exception as exc:

        print(
            "[VISUAL RECOVERY ERROR] "
            f"{exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Visual recovery failed: "
                f"{exc}"
            )
        )

    # --------------------------------------------------------
    # FIND REFERENCE
    # --------------------------------------------------------

    reference_path = None

    outputs = result.get(
        "outputs",
        {}
    )

    if not isinstance(
        outputs,
        dict
    ):
        outputs = {}

    possible_reference_values = [

        result.get(
            "reference_path"
        ),

        result.get(
            "reference_image"
        ),

        result.get(
            "reference"
        ),

        outputs.get(
            "reference_path"
        ),

        outputs.get(
            "reference_image"
        ),

        outputs.get(
            "reference"
        ),
    ]

    for value in (
        possible_reference_values
    ):

        if not value:
            continue

        candidate = Path(
            str(value)
        )

        if candidate.exists():

            reference_path = (
                candidate
            )

            break

    # --------------------------------------------------------
    # REFERENCE NAME FALLBACK
    # --------------------------------------------------------

    reference_name = (

        result.get(
            "reference_name"
        )

        or result.get(
            "matched_reference"
        )

        or result.get(
            "reference_filename"
        )

        or outputs.get(
            "reference_name"
        )

        or outputs.get(
            "matched_reference"
        )
    )

    if (
        reference_path is None
        and reference_name
    ):

        candidate = (
            IMAGE_REFERENCE_DIR
            / Path(
                str(
                    reference_name
                )
            ).name
        )

        if candidate.exists():

            reference_path = (
                candidate
            )

    # --------------------------------------------------------
    # STORE VISUAL RESULT
    # --------------------------------------------------------

    VISUAL_RESULT = dict(
        result
    )

    VISUAL_RESULT[
        "_reference_path"
    ] = (
        str(reference_path)
        if reference_path
        else None
    )

    VISUAL_RESULT[
        "_uploaded_path"
    ] = str(
        upload_path
    )

    # --------------------------------------------------------
    # BUILD VISUAL ANALYSIS
    # --------------------------------------------------------

    visual_analysis = (
        build_visual_analysis(
            result=result,
            filename=file.filename,
            extension=extension,
            reference_path=reference_path,
        )
    )

    # Ensure resolved reference name
    # is available even if pipeline
    # didn't provide it directly.

    if not visual_analysis.get(
        "reference_name"
    ):

        visual_analysis[
            "reference_name"
        ] = (
            reference_path.name
            if reference_path
            else reference_name
        )

        visual_analysis[
            "matched_reference"
        ] = (
            reference_path.name
            if reference_path
            else reference_name
        )

    # --------------------------------------------------------
    # THIS IS THE IMPORTANT FIX
    # --------------------------------------------------------
    #
    # Visual recovery now becomes
    # the active LIVE_SCAN session.
    #
    # Dashboard
    # Fragments
    # Evidence
    # Analytics
    #
    # all read this same object.
    # --------------------------------------------------------

    LIVE_SCAN = {
        "active": True,

        "mode":
            "visual",

        "file":
            file.filename,

        "file_info": {
            "name":
                file.filename,

            "size":
                len(data),

            "content_type":
                file.content_type,
        },

        "analysis":
            visual_analysis,
    }

    metrics = extract_visual_metrics(
        result
    )

    print(
        "VISUAL SESSION UPDATED"
    )

    print(
        f"Reference : "
        f"{visual_analysis.get('reference_name')}"
    )

    print(
        f"Similarity: "
        f"{metrics['similarity']:.2f}%"
    )

    print(
        f"Recovered : "
        f"{metrics['recovered_percentage']:.2f}%"
    )

    print(
        f"Damaged   : "
        f"{metrics['damaged_percentage']:.2f}%"
    )

    print(
        f"Regions   : "
        f"{metrics['damage_regions']}"
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "success": True,

        "message": (
            "Visual recovery completed "
            "successfully."
        ),

        "file": {
            "name":
                file.filename,

            "size":
                len(data),

            "content_type":
                file.content_type,
        },

        "mode":
            "visual",

        "result":
            result,

        "outputs":
            VISUAL_OUTPUTS,

        "reference": {
            "name": (
                reference_path.name
                if reference_path
                else reference_name
            ),

            "path": (
                str(reference_path)
                if reference_path
                else None
            ),
        },

        "analysis":
            visual_analysis,
    }


# ============================================================
# VISUAL OUTPUT FILES
# ============================================================

@app.get(
    "/api/image-recovery/output/{filename}"
)
def get_visual_output(
    filename: str
):

    # --------------------------------------------------------
    # REFERENCE
    # --------------------------------------------------------

    if filename == "reference.jpg":

        if not VISUAL_RESULT:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No visual recovery "
                    "has been performed yet."
                )
            )

        reference_path = (
            VISUAL_RESULT.get(
                "_reference_path"
            )
        )

        if not reference_path:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Reference image path "
                    "is unavailable."
                )
            )

        reference_path = Path(
            reference_path
        )

        if not reference_path.exists():

            raise HTTPException(
                status_code=404,
                detail=(
                    "Reference image "
                    "was not found."
                )
            )

        return FileResponse(
            reference_path,
            media_type="image/jpeg",
        )

    # --------------------------------------------------------
    # GENERATED OUTPUTS
    # --------------------------------------------------------

    allowed_outputs = {

        "damage_mask.png":
            VISUAL_OUTPUT_DIR
            / "damage_mask.png",

        "evidence_map.png":
            VISUAL_OUTPUT_DIR
            / "evidence_map.png",

        "restored_image.png":
            VISUAL_OUTPUT_DIR
            / "restored_image.png",
    }

    if filename not in allowed_outputs:

        raise HTTPException(
            status_code=404,
            detail="Output file not found."
        )

    path = allowed_outputs[
        filename
    ]

    if not path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                f"{filename} has not "
                "been generated yet."
            )
        )

    media_types = {
        ".png":
            "image/png",

        ".jpg":
            "image/jpeg",

        ".jpeg":
            "image/jpeg",

        ".webp":
            "image/webp",
    }

    return FileResponse(
        path,
        media_type=media_types.get(
            path.suffix.lower(),
            "application/octet-stream",
        ),
    )


# ============================================================
# VISUAL RECOVERY RESULT
# ============================================================

@app.get(
    "/api/image-recovery/result"
)
def visual_recovery_result():

    if not VISUAL_RESULT:

        return {
            "success": True,
            "active": False,
            "result": None,
        }

    reference_path = (
        VISUAL_RESULT.get(
            "_reference_path"
        )
    )

    reference_name = (
        Path(
            reference_path
        ).name
        if reference_path
        else None
    )

    return {
        "success": True,

        "active":
            True,

        "result":
            VISUAL_RESULT,

        "reference": {
            "name":
                reference_name,

            "url":
                (
                    VISUAL_OUTPUTS[
                        "reference_image"
                    ]
                    if reference_path
                    else None
                ),
        },

        "outputs":
            VISUAL_OUTPUTS,

        "analysis":
            current_analysis(),
    }


# ============================================================
# CLEAR LIVE SESSION
# ============================================================

@app.delete("/api/scan")
def clear_scan():

    global LIVE_SCAN
    global VISUAL_RESULT

    LIVE_SCAN = {
        "active": False,
        "mode": None,
        "file": None,
        "file_info": None,
        "analysis": None,
    }

    VISUAL_RESULT = None

    return {
        "success": True,
        "message":
            "Live scan session cleared.",
    }


# ============================================================
# CLEAR VISUAL RECOVERY
# ============================================================

@app.delete(
    "/api/image-recovery"
)
def clear_visual_recovery():

    global LIVE_SCAN
    global VISUAL_RESULT

    VISUAL_RESULT = None

    LIVE_SCAN = {
        "active": False,
        "mode": None,
        "file": None,
        "file_info": None,
        "analysis": None,
    }

    return {
        "success": True,

        "message":
            "Visual recovery session cleared.",
    }


# ============================================================
# REFERENCE DATABASE IMAGE
# ============================================================

@app.get(
    "/api/image-recovery/reference/{filename}"
)
def get_reference_image(
    filename: str
):

    safe_filename = Path(
        filename
    ).name

    path = (
        IMAGE_REFERENCE_DIR
        / safe_filename
    )

    if not path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Reference image "
                "not found."
            )
        )

    if path.suffix.lower() not in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid reference "
                "image."
            )
        )

    media_types = {
        ".jpg":
            "image/jpeg",

        ".jpeg":
            "image/jpeg",

        ".png":
            "image/png",

        ".webp":
            "image/webp",
    }

    return FileResponse(
        path,
        media_type=media_types[
            path.suffix.lower()
        ],
    )


# ============================================================
# REFERENCE DATABASE INFO
# ============================================================

@app.get(
    "/api/image-recovery/references"
)
def reference_database():

    images = []

    if IMAGE_REFERENCE_DIR.exists():

        for path in sorted(
            IMAGE_REFERENCE_DIR.iterdir()
        ):

            if (
                path.is_file()
                and path.suffix.lower()
                in {
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp",
                }
            ):

                images.append({
                    "name":
                        path.name,

                    "url": (
                        "/api/"
                        "image-recovery/"
                        f"reference/"
                        f"{path.name}"
                    ),
                })

    return {
        "success": True,

        "total":
            len(images),

        "images":
            images,
    }


# ============================================================
# SYSTEM SUMMARY
# ============================================================

@app.get("/api/system")
def system_summary():

    analysis = (
        current_analysis()
    )

    return {
        "success": True,

        "system": {
            "name":
                "ReFrag AI",

            "status":
                "online",

            "version":
                "1.0.0",
        },

        "engines": {
            "fragment_classifier":
                True,

            "relationship_engine":
                True,

            "reconstruction_engine":
                True,

            "integrity_analyzer":
                True,

            "evidence_prioritizer":
                True,

            "visual_recovery":
                True,

            "reference_matching":
                True,
        },

        "live_scan": {
            "active":
                LIVE_SCAN[
                    "active"
                ],

            "mode":
                LIVE_SCAN.get(
                    "mode"
                ),

            "file":
                LIVE_SCAN.get(
                    "file"
                ),
        },

        "visual_recovery": {
            "active":
                VISUAL_RESULT
                is not None,
        },

        "current_analysis":
            analysis,
    }


# ============================================================
# SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )