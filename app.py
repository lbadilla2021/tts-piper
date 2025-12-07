#!/usr/bin/env python3
"""
Aplicación Flask para servir el frontend y el backend de Piper TTS.

El servidor expone los endpoints `/api/voices`, `/api/synthesize` y
`/api/upload-file`, cargando los modelos locales definidos en
``models/catalog.json`` y generando los audios en ``outputs/``.
"""
from __future__ import annotations

import os
import pathlib

from flask import Flask, jsonify, render_template, request, send_from_directory, url_for

from tts_engine import OUTPUT_DIR, TTSEngine, SynthesisError, VoiceNotFoundError
from model_sync import sync_models_if_needed

app = Flask(__name__)
SYNCED, SYNC_MESSAGE = sync_models_if_needed()
tts_engine = TTSEngine()


def _get_api_base_url() -> str:
    """Obtiene la URL base del backend, asegurando que termine sin slash."""

    api_url = os.environ.get("API_BASE_URL", "")
    return api_url.rstrip("/")


@app.route("/")
def index():
    """Renderiza el frontend con la URL del backend inyectada en la plantilla."""

    return render_template("index.html", api_base_url=_get_api_base_url())


@app.route("/health")
def health():
    """Endpoint simple de salud para orquestadores o monitoreo."""

    return jsonify({"status": "ok"})


@app.route("/api/voices")
def voices():
    """Recupera el catálogo de voces expuesto por el motor local."""

    catalog = tts_engine.catalog_by_gender()
    return jsonify(
        {
            **catalog,
            "synced": SYNCED,
            "message": SYNC_MESSAGE,
            "missing_models": tts_engine.missing_voices(),
        }
    )


@app.route("/api/synthesize", methods=["POST"])
def synthesize():
    """Genera audio localmente usando los modelos descargados."""

    payload = request.get_json(force=True, silent=True) or {}
    text = str(payload.get("text") or "").strip()
    voice_id = str(payload.get("voice") or "").strip()
    speed = float(payload.get("speed") or 1.0)

    if not text:
        return jsonify({"success": False, "error": "El texto es obligatorio"}), 400
    if not voice_id:
        return jsonify({"success": False, "error": "Debes seleccionar una voz"}), 400

    try:
        filename, output_path = tts_engine.synthesize(text, voice_id, speed)
    except VoiceNotFoundError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404
    except SynthesisError as exc:  # pragma: no cover - dependiente de modelo
        return jsonify({"success": False, "error": str(exc)}), 500

    download_url = url_for("download_audio", filename=output_path.name, _external=False)
    return jsonify(
        {
            "success": True,
            "voice": voice_id,
            "filename": filename,
            "download_url": download_url,
        }
    )


@app.route("/api/upload-file", methods=["POST"])
def upload_file():
    """Extrae texto desde archivos de texto plano."""

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No se recibió archivo"}), 400

    file = request.files["file"]
    filename = pathlib.Path(file.filename or "texto.txt").name
    raw_bytes = file.read()

    try:
        content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            content = raw_bytes.decode("latin-1")
        except Exception:  # pragma: no cover - error de codificación
            return jsonify({"success": False, "error": "No se pudo leer el archivo"}), 400

    return jsonify({"success": True, "filename": filename, "text": content})


@app.route("/outputs/<path:filename>")
def download_audio(filename: str):
    """Entrega los audios generados."""

    return send_from_directory(OUTPUT_DIR, filename, as_attachment=False)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
