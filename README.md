# Image Toolkit

A Tkinter desktop application for bulk image processing with AI-powered metadata generation.

## Features

### Converter Tab
- Batch convert **PNG ↔ JPEG** using Pillow
- **AI 4x upscaling** via Upscayl CLI
- Multiple upscaling models (remacri, ultrasharp, high-fidelity, etc.)
- Settings persist across sessions

### Metadata Generator Tab
- Upload a `.txt` file with numbered image-generation prompts
- RAG pipeline powered by **LangChain** + **FAISS** vector store
- AI extracts: **title**, **10 tags**, and **≤200 character description** for each prompt
- Download results as a formatted `.txt` file

## Requirements

- **Python 3.8+**
- **Pillow** – image conversion
- **Upscayl** *(optional)* – AI upscaling, installed at `C:\Program Files\Upscayl`
- **OpenCode Zen API key** – metadata generation

## Quick Start

```powershell
# Install dependencies
pip install -r requirements.txt

# Set your API key

# Run
python main.py
```

## Build Executable

```powershell
.\build.ps1
```

Output: `dist/ImageConverter.exe`

## Project Structure

```
backend/              # Business logic (no tkinter)
├── config.py         # Paths and constants
├── converter.py      # Image conversion (Pillow)
├── upscaler.py       # Upscayl CLI wrapper
├── settings.py       # JSON settings persistence
├── models.py         # ImageJob & JobResult dataclasses
├── pipeline.py       # Processing orchestrator
└── rag_engine.py     # LangChain RAG pipeline

frontend/             # UI layer
├── app.py            # MainWindow (notebook)
├── converter_tab.py  # Converter UI
├── metadata_tab.py   # Metadata generator UI
└── styles.py         # Theme constants

main.py               # Entry point
resources/            # Upscayl binaries and models
```

## Tech Stack

- **UI:** Tkinter / ttk
- **Image processing:** Pillow
- **AI upscaling:** Upscayl (subprocess)
- **RAG pipeline:** LangChain, FAISS, HuggingFace Embeddings
- **LLM:** OpenCode Zen (DeepSeek V4 Flash Free)

## License

© 2026. All rights reserved.

This software is provided for **viewing purposes only**. No permission is granted to use, copy, modify, distribute, or sell this code or any derivative works without explicit written consent from the author.
