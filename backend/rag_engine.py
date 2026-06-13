import json
import os
import re
from dataclasses import dataclass, field
from typing import Callable, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


ProgressCallback = Callable[[int, int, str], None]


@dataclass
class MetadataResult:
    title: str = ""
    tags: list[str] = field(default_factory=list)
    description: str = ""
    raw: str = ""


class RAGEngine:
    def __init__(self):
        self.api_key = os.environ.get("OPENCODE_API_KEY", "")
        self.api_url = "https://opencode.ai/zen/v1"
        self.model = "deepseek-v4-flash-free"
        self.vector_store: Optional[FAISS] = None
        self._loaded_path: Optional[str] = None

    def load_document(self, file_path: str) -> None:
        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = FAISS.from_documents(chunks, embeddings)
        self._loaded_path = file_path

    def parse_prompts(self, file_path: str) -> list[str]:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        pattern = r"(?:^|\n)\s*(\d+)[.)]\s*(.*?)(?=\n\s*\d+[.)]\s*|\Z)"
        matches = re.findall(pattern, text, re.DOTALL)

        if not matches:
            return [text.strip()]

        return [m[1].strip() for m in matches]

    def generate_for_prompt(self, prompt_text: str) -> MetadataResult:
        if not self.vector_store:
            raise RuntimeError("No document loaded. Call load_document() first.")

        llm = ChatOpenAI(
            base_url=self.api_url,
            api_key=self.api_key,
            model=self.model,
            temperature=0.3,
        )

        template = (
            "You are an AI that analyzes image-generation prompts.\n"
            "Given the context below, extract exactly:\n"
            "1. A short title (max 5 words)\n"
            "2. 10 relevant tags (comma-separated list)\n"
            "3. A brief description (max 200 characters)\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Respond ONLY in this exact JSON format:\n"
            '{{"title": "...", "tags": ["tag1", "tag2", ...], "description": "..."}}'
        )

        prompt = ChatPromptTemplate.from_template(template)
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        def format_docs(docs):
            return "\n\n".join(d.page_content for d in docs)

        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        result = chain.invoke(f"Analyze this image generation prompt: {prompt_text}")
        return self._parse(result, result)

    def generate_bulk(self, file_path: str, on_progress: Optional[ProgressCallback] = None) -> list[MetadataResult]:
        self.load_document(file_path)
        prompts = self.parse_prompts(file_path)

        log = on_progress or (lambda i, t, m: None)
        log(0, len(prompts), f"Found {len(prompts)} prompts")

        results: list[MetadataResult] = []
        for i, prompt_text in enumerate(prompts):
            log(i + 1, len(prompts), f"Processing {i + 1}/{len(prompts)}")
            result = self.generate_for_prompt(prompt_text)
            results.append(result)

        return results

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

    def _parse(self, raw: str, fallback_raw: str) -> MetadataResult:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return MetadataResult(
                    title=data.get("title", ""),
                    tags=data.get("tags", []),
                    description=data.get("description", ""),
                    raw=raw,
                )
            except (json.JSONDecodeError, TypeError):
                pass
        return MetadataResult(title="Parse error", tags=[], description=raw[:200], raw=fallback_raw)
