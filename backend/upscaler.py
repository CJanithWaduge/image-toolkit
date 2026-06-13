import os
import subprocess

from .config import UPSCAYL_EXE, UPSCAYL_MODELS


class Upscaler:
    def __init__(self, model="remacri-4x", scale=4):
        self.model = model
        self.scale = scale

    @staticmethod
    def is_available():
        return os.path.isfile(UPSCAYL_EXE)

    def upscale(self, input_path, output_path):
        cmd = [
            UPSCAYL_EXE,
            "-i", input_path,
            "-o", output_path,
            "-m", UPSCAYL_MODELS,
            "-n", self.model,
            "-s", str(self.scale),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Upscayl error: {result.stderr.strip()}")
