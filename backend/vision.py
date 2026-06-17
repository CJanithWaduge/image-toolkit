from __future__ import annotations

import logging
import os
import threading
from collections import Counter
from typing import ClassVar, Optional

import torch
from PIL import Image

logger = logging.getLogger(__name__)

VISION_MODEL_ID: str = os.environ.get(
    "VISION_MODEL_ID", "microsoft/Florence-2-base"
)

_SAMPLE_SIZE = 64
_TASK_PROMPT = "<CAPTION>"
_MAX_IMAGE_DIM = 1024  # longest edge in pixels


class LocalVisionEngine:
    """Wrapper around Florence-2 for image captioning."""

    _processor: ClassVar[Optional[object]] = None
    _model: ClassVar[Optional[object]] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def is_available(cls) -> bool:
        if cls._model is not None:
            return True
        try:
            from transformers import AutoModelForCausalLM, AutoProcessor
            return True
        except ImportError:
            return False

    @classmethod
    def _ensure_loaded(cls) -> tuple:
        if cls._model is not None:
            return cls._processor, cls._model
        with cls._lock:
            if cls._model is not None:
                return cls._processor, cls._model
            from transformers import AutoModelForCausalLM, AutoProcessor
            logger.info("Loading Florence-2 model: %s", VISION_MODEL_ID)
            cls._processor = AutoProcessor.from_pretrained(
                VISION_MODEL_ID, trust_remote_code=True
            )
            cls._model = AutoModelForCausalLM.from_pretrained(
                VISION_MODEL_ID, trust_remote_code=True, torch_dtype=torch.float32
            )
            logger.info("Florence-2 model loaded.")
        return cls._processor, cls._model

    # ------------------------------------------------------------------
    # Color analysis
    # ------------------------------------------------------------------

    @staticmethod
    def _classify_rgb(r: int, g: int, b: int) -> str:
        if r > 200 and g > 200 and b > 200:
            return "white"
        if r < 50 and g < 50 and b < 50:
            return "black"
        if r > 150 and g < 100 and b < 100:
            return "red"
        if r > 200 and g > 150 and b < 100:
            return "orange"
        if r > 200 and g > 200 and b < 100:
            return "yellow"
        if g > 150 and r < 100 and b < 100:
            return "green"
        if b > 200 and r < 100 and g < 150:
            return "blue"
        if r > 150 and b > 150 and g < 100:
            return "purple"
        if r > 200 and g > 150 and b > 150:
            return "pink"
        if r > 150 and g > 150 and b > 150:
            return "gray"
        return f"rgb({r},{g},{b})"

    @classmethod
    def _get_colors(cls, image_path: str, num_colors: int = 3) -> list[str]:
        image = Image.open(image_path).convert("RGB").resize((_SAMPLE_SIZE, _SAMPLE_SIZE))
        pixels = [image.getpixel((x, y)) for y in range(_SAMPLE_SIZE) for x in range(_SAMPLE_SIZE)]
        dominant = Counter(pixels).most_common(num_colors)
        return [cls._classify_rgb(r, g, b) for (r, g, b), _ in dominant]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def describe(cls, image_path: str, _prompt: str = "") -> str:
        """Return a natural-language description of *image_path*.

        Args:
            image_path: Path to a readable image file.
            _prompt: Unused -- reserved for future use.

        Returns:
            A short caption, e.g. ``"a baby boy playing soccer"``.
        """
        processor, model = cls._ensure_loaded()
        image = Image.open(image_path).convert("RGB")

        # Downscale if longer edge exceeds _MAX_IMAGE_DIM to prevent OOM
        w, h = image.size
        if max(w, h) > _MAX_IMAGE_DIM:
            scale = _MAX_IMAGE_DIM / max(w, h)
            new_size = (int(w * scale), int(h * scale))
            image = image.resize(new_size, Image.LANCZOS)
            logger.debug("Resized %s from %dx%d to %dx%d", image_path, w, h, *new_size)

        inputs = processor(text=_TASK_PROMPT, images=image, return_tensors="pt")
        out = model.generate(
            **inputs,
            max_new_tokens=50,
            do_sample=False,
        )
        caption = processor.batch_decode(out, skip_special_tokens=True)[0]
        caption = caption.replace(_TASK_PROMPT, "").strip()

        colors = cls._get_colors(image_path)
        color_list = ", ".join(colors)
        return f"{caption}. Dominant colors: {color_list}."
