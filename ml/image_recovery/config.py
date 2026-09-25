from pathlib import Path


# ============================================================
# ReFrag AI - Visual Recovery Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

TEST_DIR = BASE_DIR / "test"
INPUT_DIR = TEST_DIR / "input"
FRAGMENTS_DIR = TEST_DIR / "fragments"
OUTPUT_DIR = TEST_DIR / "output"
DEBUG_DIR = TEST_DIR / "debug"

ARTIFACTS_DIR = BASE_DIR / "artifacts"
MODELS_DIR = BASE_DIR / "models"


# ------------------------------------------------------------
# Dataset
# ------------------------------------------------------------

GRID_ROWS = 8
GRID_COLS = 8
TOTAL_FRAGMENTS = GRID_ROWS * GRID_COLS

CANVAS_SIZE = 900

FRAGMENT_SIZE = 96

GAP_SIZE = 18

BACKGROUND_VALUE = 18


# ------------------------------------------------------------
# Supported rotations
# ------------------------------------------------------------

ROTATIONS = [0, 90, 180, 270]


# ------------------------------------------------------------
# Relationship thresholds
# ------------------------------------------------------------

STRONG_RELATIONSHIP_THRESHOLD = 0.80
MEDIUM_RELATIONSHIP_THRESHOLD = 0.60


# ------------------------------------------------------------
# Reconstruction
# ------------------------------------------------------------

RECONSTRUCTION_CONFIDENCE_THRESHOLD = 0.55


# ------------------------------------------------------------
# Files
# ------------------------------------------------------------

ORIGINAL_IMAGE = INPUT_DIR / "original_dog.png"

JUMBLED_IMAGE = INPUT_DIR / "jumbled_dog.png"

GROUND_TRUTH = INPUT_DIR / "ground_truth.json"

RECONSTRUCTED_IMAGE = OUTPUT_DIR / "reconstructed.png"

DAMAGE_MASK = OUTPUT_DIR / "damage_mask.png"

RESTORED_IMAGE = OUTPUT_DIR / "restored.png"

SEGMENTATION_DEBUG = DEBUG_DIR / "segmentation_debug.png"