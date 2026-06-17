from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int, str], None]

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


@dataclass
class MetadataResult:
    title: str = ""
    tags: list[str] = field(default_factory=list)
    description: str = ""
    raw: str = ""


def _extract_json(raw: str) -> Optional[dict]:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except (json.JSONDecodeError, TypeError):
        return None


class RAGEngine:
    _SKILL_PATH = (
        Path(__file__).resolve().parent.parent
        / "resources" / "skills" / "zedge-seo-metadata" / "SKILL.md"
    )

    def __init__(self) -> None:
        self.vector_store: Optional[object] = None
        self._loaded_path: Optional[str] = None
        self._skill_loaded = False

    def _ensure_skill_loaded(self) -> None:
        if self._skill_loaded:
            return
        skill_path = self._SKILL_PATH
        if not skill_path.is_file():
            logger.warning("Skill file not found: %s", skill_path)
            self._skill_loaded = True
            return
        logger.info("Loading Zedge SEO skill: %s", skill_path)
        self.load_document(str(skill_path))
        self._skill_loaded = True

    # ------------------------------------------------------------------
    # Document loading
    # ------------------------------------------------------------------

    def load_document(self, file_path: str) -> None:
        from langchain_community.document_loaders import TextLoader
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = FAISS.from_documents(chunks, embeddings)
        self._loaded_path = file_path

    # ------------------------------------------------------------------
    # Prompt parsing
    # ------------------------------------------------------------------

    @staticmethod
    def parse_prompts(file_path: str) -> list[str]:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        pattern = r"(?:^|\n)\s*(\d+)[.)]\s*(.*?)(?=\n\s*\d+[.)]\s*|\Z)"
        matches = re.findall(pattern, text, re.DOTALL)

        if not matches:
            return [text.strip()]

        return [m[1].strip() for m in matches]

    # ------------------------------------------------------------------
    # Image resolution
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_image(idx: int, image_folder: str) -> Optional[str]:
        folder = Path(image_folder)
        if not folder.is_dir():
            return None
        for ext in _IMAGE_EXTENSIONS:
            candidate = folder / f"{idx}{ext}"
            if candidate.is_file():
                return str(candidate)
        return None

    # ------------------------------------------------------------------
    # Single prompt -> metadata
    # ------------------------------------------------------------------

    def generate_for_prompt(
        self,
        prompt_text: str,
        image_path: Optional[str] = None,
    ) -> MetadataResult:
        self._ensure_skill_loaded()

        image_description = ""
        if image_path:
            from backend.vision import LocalVisionEngine
            image_description = LocalVisionEngine.describe(image_path)

        context = ""
        if self.vector_store is not None:
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            docs = retriever.invoke(f"Analyze this image generation prompt: {prompt_text}")
            context = "\n\n".join(d.page_content for d in docs)

        from backend.local_llm import LocalLLMEngine
        return LocalLLMEngine.generate(
            prompt_text=prompt_text,
            image_description=image_description,
            context=context,
        )

    # ------------------------------------------------------------------
    # Image-only generation (no .txt prompt file needed)
    # ------------------------------------------------------------------

    def generate_from_files(
        self,
        image_paths: list[str],
        on_progress: Optional[ProgressCallback] = None,
    ) -> list[MetadataResult]:
        if not image_paths:
            raise ValueError("No image paths provided")

        self._ensure_skill_loaded()
        log = on_progress or (lambda i, t, m: None)
        log(0, len(image_paths), f"Processing {len(image_paths)} image(s)")

        results: list[MetadataResult] = []
        for i, img_path in enumerate(image_paths):
            path = Path(img_path)
            log(i + 1, len(image_paths), f"Analyzing: {path.name}")

            from backend.vision import LocalVisionEngine
            image_description = LocalVisionEngine.describe(str(path))

            context = ""
            if self.vector_store is not None:
                retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
                docs = retriever.invoke(f"Zedge SEO metadata for: {path.stem}. {image_description}")
                context = "\n\n".join(d.page_content for d in docs)

            from backend.local_llm import LocalLLMEngine
            result = LocalLLMEngine.generate(
                prompt_text="",
                image_description=image_description,
                context=context,
            )
            results.append(result)

        return results

    def generate_from_images(
        self,
        image_folder: str,
        on_progress: Optional[ProgressCallback] = None,
    ) -> list[MetadataResult]:
        folder = Path(image_folder)
        if not folder.is_dir():
            raise NotADirectoryError(f"Image folder not found: {image_folder}")

        image_files: list[Path] = []
        for ext in _IMAGE_EXTENSIONS:
            image_files.extend(folder.glob(f"*{ext}"))
        image_files.sort(key=lambda p: p.stem)

        if not image_files:
            raise FileNotFoundError(f"No supported images found in: {image_folder}")

        log = on_progress or (lambda i, t, m: None)
        log(0, len(image_files), f"Found {len(image_files)} images")

        results: list[MetadataResult] = []
        for i, img_path in enumerate(image_files):
            log(i + 1, len(image_files), f"Analyzing: {img_path.name}")

            from backend.vision import LocalVisionEngine
            image_description = LocalVisionEngine.describe(str(img_path))

            from backend.local_llm import LocalLLMEngine
            result = LocalLLMEngine.generate(
                prompt_text="",
                image_description=image_description,
            )
            results.append(result)

        return results

    def _parse(self, raw: str) -> MetadataResult:
        data = _extract_json(raw)
        if data:
            return MetadataResult(
                title=str(data.get("title", "")),
                tags=list(data.get("tags", [])),
                description=str(data.get("description", "")),
                raw=raw,
            )
        return MetadataResult(title="Parse error", tags=[], description=raw[:200], raw=raw)

    # ------------------------------------------------------------------
    # Bulk processing (with .txt file)
    # ------------------------------------------------------------------

    def generate_bulk(
        self,
        file_path: str,
        image_folder: Optional[str] = None,
        on_progress: Optional[ProgressCallback] = None,
    ) -> list[MetadataResult]:
        self.load_document(file_path)
        prompts = self.parse_prompts(file_path)

        log = on_progress or (lambda i, t, m: None)
        log(0, len(prompts), f"Found {len(prompts)} prompts")

        results: list[MetadataResult] = []
        for i, prompt_text in enumerate(prompts):
            log(i + 1, len(prompts), f"Processing {i + 1}/{len(prompts)}")
            image_path = self._resolve_image(i + 1, image_folder) if image_folder else None
            results.append(self.generate_for_prompt(prompt_text, image_path=image_path))

        return results

    # ------------------------------------------------------------------
    # Output formatting
    # ------------------------------------------------------------------

    @staticmethod
    def format_download(results: list[MetadataResult]) -> str:
        lines: list[str] = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}.")
            lines.append(f"title: {r.title}")
            lines.append(f"Tags: {', '.join(r.tags)}")
            lines.append(f"Description: {r.description}")
            lines.append("")
        return "\n".join(lines)
