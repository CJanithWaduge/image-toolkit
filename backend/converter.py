from __future__ import annotations

from enum import Enum
from typing import Sequence

from PIL import Image


class ConversionMode(str, Enum):
    """Supported image conversion directions."""

    PNG_TO_JPEG = "png_to_jpeg"
    JPEG_TO_PNG = "jpeg_to_png"


class Converter:
    """Bulk image format converter with configurable mode."""

    def __init__(self) -> None:
        self._init_mode(ConversionMode.PNG_TO_JPEG)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _init_mode(self, mode: ConversionMode) -> None:
        if mode == ConversionMode.PNG_TO_JPEG:
            self.source_ext: str = ".png"
            self.target_ext: str = ".jpeg"
            self.target_format: str = "JPEG"
            self.convert_to_rgb: bool = True
        else:
            self.source_ext = ".jpg"
            self.target_ext = ".png"
            self.target_format = "PNG"
            self.convert_to_rgb = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def configure(self, mode: str) -> None:
        self._init_mode(ConversionMode(mode))

    def convert(self, input_path: str, output_path: str) -> None:
        with Image.open(input_path) as img:
            if self.convert_to_rgb:
                img = img.convert("RGB")
            img.save(output_path, self.target_format)

    def source_filetypes(self) -> Sequence[tuple[str, str]]:
        if self.target_format == "JPEG":
            return [("PNG Files", "*.png")]
        return [("JPEG Files", "*.jpg *.jpeg")]

    def target_name(self) -> str:
        return "JPEG" if self.target_format == "JPEG" else "PNG"
