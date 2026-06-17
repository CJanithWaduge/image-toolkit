# Image Toolkit

A fully local, CPU-only desktop app for generating Zedge-optimized wallpaper metadata using AI vision and language models. No API keys, no cloud calls — everything runs on your machine.

## Features

### Converter Tab
- Batch convert **PNG ↔ JPEG** via Pillow
- **AI 4x upscaling** via Upscayl CLI with multiple models (remacri, ultrasharp, high-fidelity, etc.)

### Metadata Generator Tab
- Select 1+ images, click Generate
- **Florence-2** (Microsoft) describes the image
- **Qwen2.5-1.5B** (GGUF, Q4_K_M) generates Zedge-optimized title, 10 tags, and description
- **RAG pipeline** feeds Zedge SEO rules as context (FAISS + sentence embeddings)
- Download results as `.txt`

## AI Models Required

The app downloads these automatically on first use via HuggingFace:

| Model | Size | Purpose | Auto-downloaded |
|-------|------|---------|-----------------|
| **microsoft/Florence-2-base** | ~0.8B params | Image captioning | Yes |
| **Qwen2.5-1.5B-Instruct GGUF Q4_K_M** | ~1.1 GB | SEO metadata generation | No — manual |
| **all-MiniLM-L6-v2** | ~80 MB | Text embeddings for RAG | Yes |

### Where to place the GGUF model

1. Download from HuggingFace:
   https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf

2. Place it at:
   ```
   resources/models/qwen2.5-1.5b-instruct-q4_k_m.gguf
   ```

### How to replace models

Set environment variables to override defaults:

```powershell
# Override vision model
$env:VISION_MODEL_ID="microsoft/Florence-2-base"

# Override LLM (GGUF path or HuggingFace model ID)
$env:LLM_MODEL_ID="path/to/custom-model.gguf"
$env:LLM_MODEL_ID="Qwen/Qwen2.5-1.5B-Instruct"
```

The vision model can be **any** HuggingFace `AutoModelForCausalLM` with a compatible processor. The LLM can be any `.gguf` file or any HuggingFace causal LM.

### Upscaling (optional)

Install Upscayl from https://www.upscayl.org. The app expects it at `C:\Program Files\Upscayl` by default. Upscayl models are in `resources/models/` (download from Upscayl's release page).

## Requirements

- **Python 3.10+**
- **~8 GB RAM** (both Florence-2 and Qwen2.5 run simultaneously during generation)
- **Windows** (Upscayl integration is Windows-specific; core generation works cross-platform)

## Quick Start

```powershell
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place the GGUF model (see above)

# 4. Run
python main.py
```

First launch will download Florence-2 and the embedding model (~1 GB total). Subsequent launches are instant.

## Project Structure

```
backend/               # Business logic (no tkinter)
├── config.py          # Paths and constants
├── converter.py       # Image conversion (Pillow)
├── local_llm.py       # Qwen2.5 GGUF / transformers inference
├── rag_engine.py      # LangChain RAG pipeline + Zedge SEO skill
├── vision.py          # Florence-2 image captioning
├── upscaler.py        # Upscayl CLI wrapper
├── settings.py        # JSON settings persistence
├── models.py          # ImageJob & JobResult dataclasses
└── pipeline.py        # Processing orchestrator

frontend/              # Tkinter UI layer
├── app.py             # MainWindow (notebook)
├── converter_tab.py   # Converter UI
├── metadata_tab.py    # Metadata generator UI
└── styles.py          # Theme constants

resources/
├── models/            # GGUF + Upscayl model files (gitignored)
├── bins/              # Upscayl binaries (gitignored)
└── skills/            # Zedge SEO skill (loaded into vector store)

main.py                # Entry point
```

## Tests

```powershell
pytest tests/ -v
```

39 tests covering converter, upscaler, pipeline, settings, vision, and RAG engine.

## License

© 2026. All rights reserved.
