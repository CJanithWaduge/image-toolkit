from __future__ import annotations

import os
import sys
from enum import Enum
from pathlib import Path


class UpscaleModel(str, Enum):
    REMACRI = "remacri-4x"
    ULTRASHARP = "ultrasharp-4x"
    HIGH_FIDELITY = "high-fidelity-4x"
    ULTRAMIX_BALANCED = "ultramix-balanced-4x"
    DIGITAL_ART = "digital-art-4x"
    UPSCAYL_STANDARD = "upscayl-standard-4x"
    UPSCAYL_LITE = "upscayl-lite-4x"


MODEL_LIST = [m.value for m in UpscaleModel]
DEFAULT_MODEL = UpscaleModel.REMACRI.value


def _get_project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT: Path = _get_project_root()
RESOURCES_DIR: Path = PROJECT_ROOT / "resources"

UPSCAYL_EXE: str = str(RESOURCES_DIR / "bin" / "upscayl-bin.exe")
UPSCAYL_MODELS: str = str(RESOURCES_DIR / "models")
