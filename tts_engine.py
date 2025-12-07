"""Motor de síntesis basado en Piper."""

from __future__ import annotations
import json
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from piper.voice import PiperVoice
import soundfile as sf


BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"


@dataclass
class VoiceInfo:
    id: str
    name: str
    gender: str
    accent: str
    quality: str
    description: str
    model: Path
    config: Path

    def as_public_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "accent": self.accent,
            "quality": self.quality,
            "description": self.description,
        }


class VoiceNotFoundError(RuntimeError):
    pass


class SynthesisError(RuntimeError):
    pass


def _load_catalog() -> List[VoiceInfo]:
    catalog_path = MODELS_DIR / "catalog.json"
    try:
        raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raw = {}

    voices: List[VoiceInfo] = []
    for entry in raw.get("voices", []):
        model_path = MODELS_DIR / entry.get("model", "")
        config_path = MODELS_DIR / entry.get("config", "")
        voices.append(
            VoiceInfo(
                id=str(entry.get("id") or entry.get("name") or model_path.stem),
                name=str(entry.get("name") or model_path.stem),
                gender=str(entry.get("gender") or "other"),
                accent=str(entry.get("accent") or "General"),
                quality=str(entry.get("quality") or "Standard"),
                description=str(entry.get("description") or "Modelo disponible"),
                model=model_path,
                config=config_path if config_path.exists() else model_path.with_suffix(model_path.suffix + ".json"),
            )
        )

    return voices


class TTSEngine:
    """Motor reutilizable que mantiene modelos en memoria."""

    def __init__(self) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.voices: Dict[str, VoiceInfo] = {voice.id: voice for voice in _load_catalog()}
        self._voice_cache: Dict[str, PiperVoice] = {}
        self._lock = threading.Lock()

    def catalog_by_gender(self) -> Dict[str, List[Dict[str, str]]]:
        grouped: Dict[str, List[Dict[str, str]]] = {"male": [], "female": [], "other": []}
        for voice in self.voices.values():
            gender = voice.gender.lower()
            target = "male" if gender.startswith("m") else "female" if gender.startswith("f") else "other"
            grouped[target].append(voice.as_public_dict())
        return grouped

    def _get_voice(self, voice_id: str) -> VoiceInfo:
        try:
            return self.voices[voice_id]
        except KeyError as exc:  # pragma: no cover - validación de entrada
            raise VoiceNotFoundError(f"Voz '{voice_id}' no está configurada") from exc

    def _load_or_get_model(self, voice: VoiceInfo) -> PiperVoice:
        if voice.id in self._voice_cache:
            return self._voice_cache[voice.id]

        if not voice.model.exists():
            raise SynthesisError(f"No se encontró el modelo: {voice.model.name}")
        if not voice.config.exists():
            raise SynthesisError(f"No se encontró el archivo de configuración: {voice.config.name}")

        try:
            loaded = PiperVoice.load(str(voice.model), config_path=str(voice.config))
        except Exception as exc:  # pragma: no cover - depende del estado del modelo
            raise SynthesisError(
                "El modelo o su configuración parecen estar dañados. "
                "Intenta volver a sincronizar los modelos e intenta de nuevo."
            ) from exc
        self._voice_cache[voice.id] = loaded
        return loaded

    def synthesize(self, text: str, voice_id: str, speed: float = 1.0) -> Tuple[str, Path]:
        if not text.strip():
            raise SynthesisError("El texto está vacío")

        voice = self._get_voice(voice_id)
        length_scale = max(0.25, min(4.0, 1.0 / max(speed, 0.1)))

        with self._lock:
            model = self._load_or_get_model(voice)
            audio_output = model.synthesize(text, length_scale=length_scale)

        filename = f"tts_{uuid.uuid4().hex}.wav"
        output_path = OUTPUT_DIR / filename

        if isinstance(audio_output, tuple):
            audio_data, sample_rate = audio_output
            sf.write(output_path, audio_data, int(sample_rate))
        else:
            output_path.write_bytes(audio_output)

        return filename, output_path


__all__ = ["TTSEngine", "VoiceNotFoundError", "SynthesisError", "VoiceInfo", "OUTPUT_DIR"]
