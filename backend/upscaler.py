from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from .config import UPSCAYL_EXE, UPSCAYL_MODELS

logger = logging.getLogger(__name__)

_SUBPROCESS_TIMEOUT = int(os.environ.get("UPSCAYL_TIMEOUT", "300"))


class UpscalingError(RuntimeError):
    """Raised when the external upscayl binary fails."""


class Upscaler:
    """Thin wrapper around the external upscayl-bin.exe process."""

    def __init__(self, model: str = "remacri-4x", scale: int = 4) -> None:
        if scale < 1 or scale > 10:
            raise ValueError(f"scale must be 1-10, got {scale}")
        self.model = model
        self.scale = scale

    @staticmethod
    def is_available() -> bool:
        return Path(UPSCAYL_EXE).is_file()

    def upscale(self, input_path: str, output_path: str) -> None:
        cmd = [
            UPSCAYL_EXE,
            "-i", input_path,
            "-o", output_path,
            "-m", UPSCAYL_MODELS,
            "-n", self.model,
            "-s", str(self.scale),
        ]
        logger.info("Running upscayl: %s", " ".join(cmd))
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_SUBPROCESS_TIMEOUT,
        )
        if result.returncode != 0:
            raise UpscalingError(
                f"Upscayl error (exit {result.returncode}): {result.stderr.strip()}"
            )
