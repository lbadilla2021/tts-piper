#!/usr/bin/env python3
"""
Aplicación Flask minimalista para servir el frontend de Piper TTS.

El backend de síntesis vive en el proyecto `tts-piper-2`; este servicio
solo entrega los assets estáticos y expone la URL base del backend para
que el JavaScript del cliente hable directamente con él.
"""
from __future__ import annotations

import os

from flask import Flask, jsonify, render_template, request

import requests

from model_sync import load_voice_catalog

app = Flask(__name__)


def _get_api_base_url() -> str:
    """Obtiene la URL base del backend, asegurando que termine sin slash."""

    api_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    return api_url.rstrip("/")


def _call_backend(paths, method="GET", **kwargs):
    """Realiza una llamada al backend probando múltiples rutas."""

    base_url = _get_api_base_url()
    errors = []

    for path in paths:
        url = f"{base_url}{path}"
        try:
            response = requests.request(method, url, timeout=15, **kwargs)
        except requests.RequestException as exc:  # pragma: no cover - dependiente de red
            errors.append(str(exc))
            continue

        if response.ok:
            return response, url

        errors.append(f"{url} -> {response.status_code}")

    return None, errors


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
    """Recupera el catálogo de voces desde el backend y ofrece un respaldo local."""

    backend_response, debug = _call_backend(["/api/voices", "/voices"])

    if backend_response is not None:
        data = backend_response.json()
        data.setdefault("synced", True)
        data.setdefault("message", "Modelos obtenidos desde el backend")
        return jsonify(data)

    catalog = load_voice_catalog()
    return jsonify(
        {
            "male": catalog.get("male", []),
            "female": catalog.get("female", []),
            "other": catalog.get("other", []),
            "synced": False,
            "message": "; ".join(debug) or "No se pudo contactar al backend",
        }
    )


@app.route("/api/synthesize", methods=["POST"])
def synthesize():
    """Proxy hacia el backend para generar audio."""

    payload = request.get_json(force=True, silent=True) or {}
    backend_response, debug = _call_backend(
        ["/api/synthesize", "/synthesize"], method="POST", json=payload
    )

    if backend_response is None:
        return (
            jsonify({"success": False, "error": "; ".join(debug) or "Backend no disponible"}),
            502,
        )

    return jsonify(backend_response.json())


@app.route("/api/upload-file", methods=["POST"])
def upload_file():
    """Proxy hacia el backend para extraer texto de archivos subidos."""

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No se recibió archivo"}), 400

    file = request.files["file"]
    files = {"file": (file.filename, file.stream, file.mimetype)}

    backend_response, debug = _call_backend(
        ["/api/upload-file", "/upload-file"], method="POST", files=files
    )

    if backend_response is None:
        return (
            jsonify({"success": False, "error": "; ".join(debug) or "Backend no disponible"}),
            502,
        )

    return jsonify(backend_response.json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
