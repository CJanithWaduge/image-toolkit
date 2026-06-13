import os
import sys


def _get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = _get_base_path()

UPSCAYL_EXE = os.path.join(BASE_DIR, "resources", "bin", "upscayl-bin.exe")
UPSCAYL_MODELS = os.path.join(BASE_DIR, "resources", "models")

AVAILABLE_MODELS = [
    "remacri-4x",
    "ultrasharp-4x",
    "high-fidelity-4x",
    "ultramix-balanced-4x",
    "digital-art-4x",
    "upscayl-standard-4x",
    "upscayl-lite-4x",
]
