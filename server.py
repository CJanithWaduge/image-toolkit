import logging
import os
import tempfile
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from backend.converter import ConversionMode, Converter
from backend.models import ImageJob
from backend.pipeline import ProcessingPipeline
from backend.settings import Settings
from backend.upscaler import Upscaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

# Backend instances
settings = Settings()
converter = Converter()
upscaler = Upscaler()
pipeline = ProcessingPipeline(converter, upscaler)


# ---------------------------------------------------------------------------
# Static page
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Converter API
# ---------------------------------------------------------------------------

@app.route("/api/converter/process", methods=["POST"])
def api_converter_process():
    file = request.files.get("image")
    if not file:
        return jsonify({"success": False, "error": "No file provided"}), 400

    direction = request.form.get("direction", "png2jpeg")
    enable_upscale = request.form.get("upscale", "false").lower() == "true"
    model = request.form.get("model", "remacri-4x")
    scale = int(request.form.get("scale", "2"))

    mode = ConversionMode.PNG_TO_JPEG if direction == "png2jpeg" else ConversionMode.JPEG_TO_PNG
    suffix = Path(file.filename).suffix
    output_dir = tempfile.mkdtemp()
    output_name = f"{Path(file.filename).stem}_{uuid.uuid4().hex[:8]}"
    input_path = os.path.join(output_dir, f"input{suffix}")

    try:
        file.save(input_path)
        job = ImageJob(
            source_path=input_path,
            output_dir=output_dir,
            output_name=output_name,
            mode=mode.value,
            upscale_enabled=enable_upscale,
            upscale_model=model,
            upscale_scale=scale,
        )
        result = pipeline.process(job)
        return jsonify({
            "success": result.success,
            "filename": file.filename,
            "output_name": Path(result.output_path).name if result.output_path else output_name,
            "error": result.error or "",
        })
    except Exception as e:
        logger.exception("Conversion failed")
        return jsonify({"success": False, "filename": file.filename, "error": str(e)})


# ---------------------------------------------------------------------------
# Metadata Generator API
# ---------------------------------------------------------------------------

@app.route("/api/metadata/generate", methods=["POST"])
def api_metadata_generate():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        file.save(tmp.name)
        image_path = tmp.name

    try:
        from backend.rag_engine import RAGEngine

        engine = RAGEngine()
        results = engine.generate_from_files([image_path])
        r = results[0] if results else None
        if r is None:
            return jsonify({"filename": file.filename, "title": "", "tags": [], "description": ""})

        return jsonify({
            "filename": file.filename,
            "title": r.title,
            "tags": r.tags,
            "description": r.description,
        })
    except Exception as e:
        logger.exception("Metadata generation failed")
        return jsonify({"filename": file.filename, "title": "Error", "tags": [], "description": str(e)})
    finally:
        try:
            os.unlink(image_path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    import sys
    port = int(os.environ.get("PORT", "8000"))
    logger.info("Starting server on http://127.0.0.1:%d", port)
    app.run(host="127.0.0.1", port=port, debug=True)
