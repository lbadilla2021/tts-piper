#!/usr/bin/env python3
"""
Aplicación Flask minimalista para servir el frontend de Piper TTS.

El backend de síntesis vive en el proyecto `tts-piper-2`; este servicio
solo entrega los assets estáticos y expone la URL base del backend para
que el JavaScript del cliente hable directamente con él.
"""
from __future__ import annotations

import os

from flask import Flask, jsonify, render_template

app = Flask(__name__)


def _get_api_base_url() -> str:
    """Obtiene la URL base del backend, asegurando que termine sin slash."""

    api_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    return api_url.rstrip("/")


@app.route("/")
def index():
    """Renderiza el frontend con la URL del backend inyectada en la plantilla."""

    return render_template("index.html", api_base_url=_get_api_base_url())


@app.route("/health")
def health():
    """Endpoint simple de salud para orquestadores o monitoreo."""

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
