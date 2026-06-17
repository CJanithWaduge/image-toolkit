import logging
import os
import tempfile
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

from backend.converter import ConversionMode, Converter
from backend.models import ImageJob
from backend.pipeline import ProcessingPipeline
from backend.settings import Settings
from backend.upscaler import Upscaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

app = Flask(__name__, template_folder=str(_TEMPLATE_DIR))
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
    user_output_dir = request.form.get("output_dir", "").strip()

    mode = ConversionMode.PNG_TO_JPEG if direction == "png2jpeg" else ConversionMode.JPEG_TO_PNG
    suffix = Path(file.filename).suffix
    if user_output_dir:
        output_dir = os.path.abspath(user_output_dir)
        os.makedirs(output_dir, exist_ok=True)
    else:
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
        )
        result = pipeline.process(job)
        output_path = Path(result.output_path) if result.output_path else None
        download_token = None
        if output_path and output_path.is_file():
            download_token = uuid.uuid4().hex
            _download_tokens[download_token] = str(output_path.resolve())
        return jsonify({
            "success": result.success,
            "filename": file.filename,
            "output_name": output_path.name if output_path else output_name,
            "output_path": str(output_path.resolve()) if output_path else "",
            "download_token": download_token,
            "error": result.error or "",
        })
    except Exception as e:
        logger.exception("Conversion failed")
        return jsonify({"success": False, "filename": file.filename, "error": str(e)})


# ---------------------------------------------------------------------------
# Upscaler API
# ---------------------------------------------------------------------------

@app.route("/api/upscaler/process", methods=["POST"])
def api_upscaler_process():
    file = request.files.get("image")
    if not file:
        return jsonify({"success": False, "error": "No file provided"}), 400

    model = request.form.get("model", "remacri-4x")
    scale = int(request.form.get("scale", "2"))
    user_output_dir = request.form.get("output_dir", "").strip()

    suffix = Path(file.filename).suffix
    if user_output_dir:
        output_dir = os.path.abspath(user_output_dir)
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = tempfile.mkdtemp()
    output_name = f"{Path(file.filename).stem}_{uuid.uuid4().hex[:8]}"
    input_path = os.path.join(output_dir, f"input{suffix}")
    output_path = os.path.join(output_dir, f"{output_name}{suffix}")

    try:
        file.save(input_path)
        upscaler.model = model
        upscaler.scale = scale
        upscaler.upscale(input_path, output_path)
        download_token = uuid.uuid4().hex
        _download_tokens[download_token] = output_path
        return jsonify({
            "success": True,
            "filename": file.filename,
            "output_name": Path(output_path).name,
            "output_path": output_path,
            "download_token": download_token,
            "error": "",
        })
    except Exception as e:
        logger.exception("Upscaling failed")
        return jsonify({"success": False, "filename": file.filename, "error": str(e)})


@app.route("/api/upscaler/download/<token>")
def api_upscaler_download(token: str):
    path = _download_tokens.pop(token, None)
    if not path or not os.path.isfile(path):
        return jsonify({"error": "File not found or expired"}), 404
    return send_file(path, as_attachment=True)


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
# Download API — serve processed files for client-side save
# ---------------------------------------------------------------------------

_download_tokens: dict[str, str] = {}

@app.route("/api/converter/download/<token>")
def api_converter_download(token: str):
    path = _download_tokens.pop(token, None)
    if not path or not os.path.isfile(path):
        return jsonify({"error": "File not found or expired"}), 404
    return send_file(path, as_attachment=True)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok"})
