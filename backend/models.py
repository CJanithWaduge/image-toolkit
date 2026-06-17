from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class ImageJob:
    """A single image conversion/upscaling job."""

    source_path: str
    output_dir: str
    output_name: str
    mode: str = "png_to_jpeg"
    upscale_enabled: bool = False
    upscale_model: str = "remacri-4x"
    upscale_scale: int = 4


@dataclass(slots=True)
class JobResult:
    """Outcome of a single processing job."""

    success: bool
    output_path: Optional[str] = None
    error: Optional[str] = None
