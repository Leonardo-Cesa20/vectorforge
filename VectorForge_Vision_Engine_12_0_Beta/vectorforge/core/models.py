from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import numpy as np

@dataclass
class Settings:
    art_type: str = "logo"
    profile: str = "engraving"
    width_mm: float = 100.0
    min_area: int = 10
    denoise: int = 1
    close_gaps: int = 1
    simplify: float = 0.08
    auto_crop: bool = True
    invert: bool = False
    preserve_holes: bool = True
    preserve_original_paths: bool = True
    geometry_strength: float = 0.0
    max_nodes_per_path: int = 420
    candidate_mode: str = "auto"
    remove_border_noise: bool = True
    fill_small_holes: bool = False
    edge_protection: float = 0.65

@dataclass
class VisionCandidate:
    name: str
    binary: np.ndarray
    score: float
    coverage: float
    components: int
    holes: int
    border_noise: float
    compactness: float

@dataclass
class VectorShape:
    kind: str
    layer: str
    points: np.ndarray | None = None
    closed: bool = True
    center: Tuple[float, float] | None = None
    radius: float | None = None
    confidence: float = 1.0
    hole: bool = False
    source_index: int = -1

@dataclass
class Document:
    image_size: Tuple[int, int]
    original_bgr: np.ndarray
    normalized_bgr: np.ndarray
    binary: np.ndarray
    preview_bgr: np.ndarray
    candidates: List[VisionCandidate] = field(default_factory=list)
    shapes: List[VectorShape] = field(default_factory=list)
    diagnostics: Dict = field(default_factory=dict)
