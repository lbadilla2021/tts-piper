"""Herramientas para sincronizar y exponer modelos locales desde tts-piper-2.

El objetivo es clonar sólo la carpeta ``models`` del repositorio
https://github.com/lbadilla2021/tt-piper-2 y dejarla disponible de forma
local. Cuando no hay conectividad o no existe metadata, se usan valores de
respaldo para que el frontend siga funcionando.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
CACHE_DIR = BASE_DIR / ".cache"
REPO_CACHE = CACHE_DIR / "tts-piper-2"
DEFAULT_REPO = "https://github.com/lbadilla2021/tt-piper-2.git"


class ModelSyncError(RuntimeError):
    """Error genérico para problemas de sincronización de modelos."""


@dataclass
class Voice:
    """Representa una voz disponible para el frontend."""

    id: str
    name: str
    gender: str
    accent: str
    quality: str
    description: str

    def as_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "accent": self.accent,
            "quality": self.quality,
            "description": self.description,
        }


def _run(cmd: List[str]) -> None:
    """Ejecuta un comando y lanza ModelSyncError si falla."""

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise ModelSyncError("git no está instalado en la imagen del contenedor") from exc
    if result.returncode != 0:
        raise ModelSyncError(result.stderr.strip() or "No fue posible ejecutar git")


def _clone_models_repo(repo_url: str = DEFAULT_REPO) -> None:
    """Clona (o actualiza) sólo la carpeta ``models`` del repo remoto."""

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if (REPO_CACHE / ".git").exists():
        _run(["git", "-C", str(REPO_CACHE), "fetch", "--depth", "1", "origin", "main"])
        _run(["git", "-C", str(REPO_CACHE), "reset", "--hard", "origin/main"])
        return

    _run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--filter=blob:none",
            "--sparse",
            repo_url,
            str(REPO_CACHE),
        ]
    )
    _run(["git", "-C", str(REPO_CACHE), "sparse-checkout", "set", "models"])


def _copy_models_folder() -> Path:
    """Copia la carpeta ``models`` del repo cacheado a ``MODELS_DIR"""

    source = REPO_CACHE / "models"
    if not source.exists():
        raise ModelSyncError("No se encontró la carpeta models en el repositorio cacheado")

    if MODELS_DIR.exists():
        shutil.rmtree(MODELS_DIR)

    shutil.copytree(source, MODELS_DIR)
    return MODELS_DIR


def sync_models_if_needed(repo_url: str | None = None) -> Tuple[bool, str]:
    """Intenta clonar y copiar los modelos. Devuelve (éxito, mensaje)."""

    effective_repo = repo_url or os.environ.get("MODEL_REPO_URL", DEFAULT_REPO)
    try:
        _clone_models_repo(effective_repo)
        _copy_models_folder()
        return True, "Modelos sincronizados desde el repositorio remoto"
    except ModelSyncError as exc:  # pragma: no cover - dependiente de red
        return False, str(exc)


def _load_catalog_file(path: Path) -> List[Dict[str, str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    voices = data.get("voices") if isinstance(data, dict) else data
    if not isinstance(voices, list):
        return []

    cleaned = []
    for entry in voices:
        if not isinstance(entry, dict):
            continue
        cleaned.append(
            Voice(
                id=str(entry.get("id", entry.get("name", "voz")).strip() or "voz"),
                name=str(entry.get("name", entry.get("id", "Voz")).strip() or "Voz"),
                gender=str(entry.get("gender", "other")),
                accent=str(entry.get("accent", "General")),
                quality=str(entry.get("quality", "Standard")),
                description=str(entry.get("description", "Modelo sincronizado")),
            ).as_dict()
        )
    return cleaned


def _build_catalog_from_directories(root: Path) -> List[Dict[str, str]]:
    voices: List[Dict[str, str]] = []
    if not root.exists():
        return voices

    for item in sorted(root.iterdir()):
        if not item.is_dir():
            continue

        metadata_candidates = [
            item / "metadata.json",
            item / "model.json",
            item / "voice.json",
        ]
        metadata = {}
        for candidate in metadata_candidates:
            if candidate.exists():
                try:
                    metadata = json.loads(candidate.read_text(encoding="utf-8"))
                    break
                except (OSError, json.JSONDecodeError):
                    metadata = {}

        voices.append(
            Voice(
                id=metadata.get("id") or item.name,
                name=metadata.get("name") or item.name.replace("_", " ").title(),
                gender=str(metadata.get("gender", "other")),
                accent=str(metadata.get("accent", metadata.get("language", "General"))),
                quality=str(metadata.get("quality", "Standard")),
                description=str(
                    metadata.get(
                        "description",
                        "Modelo detectado automáticamente desde la carpeta local de modelos.",
                    )
                ),
            ).as_dict()
        )

    return voices


def _fallback_catalog() -> List[Dict[str, str]]:
    return [
        Voice(
            id="es-mx-junior",
            name="Junior (ES-MX)",
            gender="male",
            accent="Español Latino",
            quality="Premium",
            description="Voz masculina neutra lista para usarse sin conexión.",
        ).as_dict(),
        Voice(
            id="es-mx-luisa",
            name="Luisa (ES-MX)",
            gender="female",
            accent="Español Latino",
            quality="Premium",
            description="Voz femenina con pronunciación clara y natural.",
        ).as_dict(),
    ]


def load_voice_catalog() -> Dict[str, List[Dict[str, str]]]:
    """Carga la lista de voces agrupadas por género."""

    catalog_file = MODELS_DIR / "catalog.json"
    voices = _load_catalog_file(catalog_file)

    if not voices:
        voices = _build_catalog_from_directories(MODELS_DIR)
    if not voices:
        voices = _fallback_catalog()

    grouped: Dict[str, List[Dict[str, str]]] = {"male": [], "female": [], "other": []}
    for voice in voices:
        gender = voice.get("gender", "other").lower()
        if gender.startswith("m"):
            grouped["male"].append(voice)
        elif gender.startswith("f"):
            grouped["female"].append(voice)
        else:
            grouped["other"].append(voice)

    return grouped


__all__ = [
    "load_voice_catalog",
    "sync_models_if_needed",
    "ModelSyncError",
    "MODELS_DIR",
]
