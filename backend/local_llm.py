from __future__ import annotations

import json
import logging
import os
import re
import threading
from pathlib import Path
from typing import ClassVar, Optional

from .rag_engine import MetadataResult

logger = logging.getLogger(__name__)

_DEFAULT_GGUF = str(
    Path(__file__).resolve().parent.parent
    / "resources" / "models" / "qwen2.5-1.5b-instruct-q4_k_m.gguf"
)

LLM_MODEL_ID: str = os.environ.get(
    "LLM_MODEL_ID", _DEFAULT_GGUF
)

_MAX_NEW_TOKENS = 300


def _extract_json(raw: str) -> Optional[dict]:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except (json.JSONDecodeError, TypeError):
        return None


def _is_gguf_path(path: str) -> bool:
    return path.lower().endswith(".gguf")


class LocalLLMEngine:
    """Wrapper around a local LLM, supporting both GGUF (llama.cpp) and HuggingFace models."""

    _model: ClassVar[Optional[object]] = None
    _tokenizer: ClassVar[Optional[object]] = None
    _use_gguf: ClassVar[Optional[bool]] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def is_available(cls) -> bool:
        if cls._model is not None:
            return True
        if _is_gguf_path(LLM_MODEL_ID):
            try:
                import llama_cpp  # noqa
                return True
            except ImportError:
                return False
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa
            return True
        except ImportError:
            return False

    @classmethod
    def _ensure_loaded(cls):
        if cls._model is not None:
            return
        with cls._lock:
            if cls._model is not None:
                return
            if _is_gguf_path(LLM_MODEL_ID):
                cls._load_gguf()
            else:
                cls._load_transformers()

    @classmethod
    def _load_gguf(cls) -> None:
        import llama_cpp

        gguf_path = Path(LLM_MODEL_ID)
        if not gguf_path.is_file():
            raise FileNotFoundError(f"GGUF model not found: {gguf_path}")

        logger.info("Loading GGUF model: %s", gguf_path)
        cls._model = llama_cpp.Llama(
            model_path=str(gguf_path),
            n_ctx=2048,
            n_threads=os.cpu_count() or 4,
            verbose=False,
        )
        cls._use_gguf = True
        logger.info("GGUF model loaded (q4_k_m).")

    @classmethod
    def _load_transformers(cls) -> None:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        logger.info("Loading local LLM via transformers: %s", LLM_MODEL_ID)
        cls._tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_ID)
        cls._model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL_ID,
            torch_dtype="auto",
            low_cpu_mem_usage=True,
        )
        cls._use_gguf = False
        logger.info("Transformers model loaded.")

    @classmethod
    def generate(
        cls,
        prompt_text: str,
        image_description: str = "",
        context: str = "",
    ) -> MetadataResult:
        cls._ensure_loaded()

        system_prompt = (
            "You are a Zedge SEO metadata expert. Your task is to generate optimized "
            "title, tags, and description for mobile wallpapers uploaded to Zedge.\n\n"
            "=== ZEDGE SEO RULES ===\n"
            "1. First tag is the most important keyword for ranking. Lead with the core subject.\n"
            "2. Cover these tag categories: subject, style, quality, colors, mood, use-case, "
            "device-context.\n"
            "3. Use compound keywords: 'cartoon-soccer' not 'cartoon soccer', "
            "'4k-wallpaper' not '4k wallpaper'.\n"
            "4. Include quality signals: hd, 4k, ultra-hd, high-quality, high-resolution.\n"
            "5. Include device/Zedge context: wallpaper, background, mobile-wallpaper, "
            "phone-background, screen.\n"
            "6. Include mood/feeling: vibrant, dark, minimal, colorful, serene, energetic, "
            "cinematic.\n"
            "7. Include style: anime, cartoon, 3d-render, vector-art, digital-art, "
            "photography, abstract, minimalist.\n"
            "8. Include color names the image actually contains (not invented).\n"
            "9. Avoid generic filler tags. Every tag must be a real search term people use.\n"
            "10. Never use trademarked or copyrighted character/ brand names unless "
            "obviously generic.\n"
            "11. Tags must be alphanumeric with hyphens or underscores only. "
            "No spaces, no special chars.\n"
            "12. Prefer specificity over generality: 'neon-samurai' > 'samurai' > 'warrior'.\n\n"
            "=== TITLE RULES ===\n"
            "- Max 70 chars. Lead with the main subject + key descriptor + quality.\n"
            "- Format: '[Subject] [Style/Quality] [Color/Mood] HD 4K Wallpaper'\n"
            "- Example: 'Neon Samurai Warrior Cyberpunk Anime HD 4K Wallpaper'\n\n"
            "=== DESCRIPTION RULES ===\n"
            "- Strictly under 200 characters.\n"
            "- Engaging, keyword-rich, natural sentence.\n"
            "- Include subject, style, mood, quality, use-case.\n"
            "- End with a call to action like 'Download for free!' or 'Perfect for your screen.'\n\n"
            "Consider copyright issues, commercial usage issues, and trademark policies. "
            "Do not use any words that violate those laws."
        )

        if prompt_text:
            user_lines = [f"Image generation prompt: {prompt_text}"]
            if image_description:
                user_lines.append(f"Visual analysis: {image_description}")
            if context:
                user_lines.append(f"Additional context:\n{context}")
        else:
            user_lines = [f"Visual analysis: {image_description or 'No description available.'}"]
            if context:
                user_lines.append(f"Additional context:\n{context}")

        user_content = "\n".join(user_lines) + (
            "\n\nGenerate optimized Zedge metadata with these constraints:\n"
            "1. Title: Maximum 70 characters. Catchy, include main keyword, state quality (HD, 4K).\n"
            "2. Tags: Exactly 10 tags. Commas between, no spaces after commas. "
            "Alphanumeric or - _ . only. No spaces inside tags; use compounding or hyphens.\n"
            "3. Description: STRICTLY under 200 characters. Engaging, keyword-rich summary.\n"
            "4. Output ONLY valid JSON. No markdown, no code fences, no extra text.\n"
            '{"title": "...", "tags": ["tag1","tag2",...], "description": "..."}'
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        if cls._use_gguf:
            raw = cls._generate_gguf(messages)
        else:
            raw = cls._generate_transformers(messages)

        data = _extract_json(raw)
        if data:
            return MetadataResult(
                title=str(data.get("title", "")),
                tags=list(data.get("tags", [])),
                description=str(data.get("description", "")),
                raw=raw,
            )
        return MetadataResult(title="Parse error", tags=[], description=raw[:200], raw=raw)

    @classmethod
    def _generate_gguf(cls, messages: list[dict]) -> str:
        response = cls._model.create_chat_completion(
            messages=messages,
            max_tokens=_MAX_NEW_TOKENS,
            temperature=0.3,
        )
        return response["choices"][0]["message"]["content"].strip()

    @classmethod
    def _generate_transformers(cls, messages: list[dict]) -> str:
        text = cls._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = cls._tokenizer(text, return_tensors="pt")
        input_len = inputs["input_ids"].shape[1]
        outputs = cls._model.generate(**inputs, max_new_tokens=_MAX_NEW_TOKENS)
        new_tokens = outputs[0][input_len:]
        return cls._tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
