from dataclasses import dataclass, field
from typing import Any


@dataclass
class Fragment:
    id: str
    x: int
    y: int
    width: int
    height: int
    area: int

    image_path: str | None = None

    centroid_x: float = 0.0
    centroid_y: float = 0.0

    rotation: int = 0

    features: dict[str, Any] = field(default_factory=dict)


@dataclass
class Relationship:
    fragment_a: str
    fragment_b: str

    direction: str

    color_similarity: float = 0.0
    texture_similarity: float = 0.0
    edge_similarity: float = 0.0
    boundary_similarity: float = 0.0
    geometric_similarity: float = 0.0

    confidence: float = 0.0


@dataclass
class ReconstructionResult:
    success: bool

    image_path: str | None = None

    confidence: float = 0.0

    fragments_used: int = 0
    fragments_total: int = 0

    relationships_analyzed: int = 0
    strong_relationships: int = 0

    placements: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DamageResult:
    status: str

    damage_score: float = 0.0

    damaged_area_percent: float = 0.0

    damage_regions: int = 0

    mask_path: str | None = None

    reason: str = ""


@dataclass
class RecoverySession:
    session_id: str

    filename: str

    file_type: str

    file_size: int

    fragments: list[Fragment] = field(default_factory=list)

    relationships: list[Relationship] = field(default_factory=list)

    reconstruction: ReconstructionResult | None = None

    damage: DamageResult | None = None

    restoration: dict[str, Any] = field(default_factory=dict)

    evidence: dict[str, Any] = field(default_factory=dict)

    analytics: dict[str, Any] = field(default_factory=dict)