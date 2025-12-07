"""Motor de síntesis basado en Piper."""

from __future__ import annotations
import inspect
import json
import re
import shutil
import threading
import uuid
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import soundfile as sf
from piper.voice import PiperVoice

from model_sync import sync_models_if_needed


BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"
CONFIG_BACKUP_DIR = MODELS_DIR / ".config_backups"


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


class ConfigError(RuntimeError):
    pass


def _load_catalog() -> List[VoiceInfo]:
    """Carga el catálogo de voces desde disco o lo reconstruye si falta."""

    def _build_catalog_from_dirs() -> List[VoiceInfo]:
        voices: List[VoiceInfo] = []
        if not MODELS_DIR.exists():
            return voices

        for voice_dir in sorted(MODELS_DIR.iterdir()):
            if not voice_dir.is_dir():
                continue

            metadata = {}
            for candidate in (
                voice_dir / "metadata.json",
                voice_dir / "model.json",
                voice_dir / "voice.json",
            ):
                if candidate.exists():
                    try:
                        metadata = json.loads(candidate.read_text(encoding="utf-8"))
                        break
                    except (OSError, json.JSONDecodeError):
                        metadata = {}

            onnx_files = sorted(voice_dir.glob("*.onnx"))
            config_files = sorted(voice_dir.glob("*.onnx.json")) + sorted(voice_dir.glob("*.json"))
            if not onnx_files:
                continue

            model_path = onnx_files[0]
            matching_config = [cfg for cfg in config_files if cfg.stem.startswith(model_path.stem)]
            config_path = (
                matching_config[0]
                if matching_config
                else config_files[0]
                if config_files
                else model_path.with_suffix(model_path.suffix + ".json")
            )

            voices.append(
                VoiceInfo(
                    id=str(metadata.get("id") or metadata.get("name") or voice_dir.name),
                    name=str(metadata.get("name") or voice_dir.name.replace("_", " ").title()),
                    gender=str(metadata.get("gender") or "other"),
                    accent=str(metadata.get("accent") or metadata.get("language") or "General"),
                    quality=str(metadata.get("quality") or "Standard"),
                    description=str(
                        metadata.get(
                            "description",
                            "Modelo reconstruido automáticamente desde la carpeta local de modelos.",
                        )
                    ),
                    model=model_path,
                    config=config_path,
                )
            )

        return voices

    catalog_path = MODELS_DIR / "catalog.json"
    try:
        raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raw = {}

    voices: List[VoiceInfo] = []
    for entry in raw.get("voices", []):
        model_path = MODELS_DIR / entry.get("model", "")
        config_path = MODELS_DIR / entry.get("config", "")
        if not model_path.exists():
            continue

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

    if voices:
        return voices

    rebuilt = _build_catalog_from_dirs()
    if rebuilt:
        try:
            catalog_payload = {
                "voices": [
                    voice.as_public_dict()
                    | {
                        "model": str(voice.model.relative_to(MODELS_DIR)),
                        "config": str(voice.config.relative_to(MODELS_DIR)),
                    }
                    for voice in rebuilt
                ]
            }
            catalog_path.write_text(
                json.dumps(catalog_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            # No bloquear la carga si no se puede persistir el catálogo reconstruido.
            pass

    return rebuilt


class TTSEngine:
    """Motor reutilizable que mantiene modelos en memoria."""

    def __init__(self) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.voices: Dict[str, VoiceInfo] = {voice.id: voice for voice in _load_catalog()}
        self._voice_cache: Dict[str, PiperVoice] = {}
        self._lock = threading.Lock()
        self._sync_inflight = False
        self._ensure_config_backups()

    def missing_voices(self) -> List[Dict[str, str]]:
        """Devuelve las voces del catálogo que no tienen sus archivos en disco."""

        catalog_path = MODELS_DIR / "catalog.json"
        try:
            raw = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog_entries = raw.get("voices", []) if isinstance(raw, dict) else []
        except (OSError, json.JSONDecodeError):
            catalog_entries = []

        missing: List[Dict[str, str]] = []
        for entry in catalog_entries:
            if not isinstance(entry, dict):
                continue

            model_path = MODELS_DIR / str(entry.get("model", ""))
            config_path = MODELS_DIR / str(entry.get("config", ""))
            issues = []

            if not model_path.exists() or not model_path.is_file():
                issues.append(f"Falta el modelo {model_path.name or model_path}")

            if not config_path.exists() or not config_path.is_file():
                issues.append(f"Falta el archivo de configuración {config_path.name or config_path}")

            if issues:
                missing.append(
                    {
                        "id": str(entry.get("id") or entry.get("name") or model_path.stem),
                        "model": str(entry.get("model", "")),
                        "config": str(entry.get("config", "")),
                        "issues": issues,
                    }
                )

        return missing

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

    def _refresh_catalog(self) -> None:
        """Recarga el catálogo de voces desde disco tras una resincro."""

        self._voice_cache = {}
        self.voices = {voice.id: voice for voice in _load_catalog()}
        self._ensure_config_backups()

    def _backup_path_for(self, config_path: Path) -> Path:
        try:
            relative = config_path.relative_to(MODELS_DIR)
        except ValueError:
            relative = Path(config_path.name)

        return CONFIG_BACKUP_DIR / relative

    def _ensure_config_backups(self) -> None:
        """Garantiza que exista una copia de los archivos de configuración."""

        CONFIG_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        for voice in self.voices.values():
            try:
                backup_path = self._backup_path_for(voice.config)
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                if voice.config.exists() and not backup_path.exists():
                    shutil.copy2(voice.config, backup_path)
            except OSError:
                # Si no se puede crear el respaldo no bloquear el arranque.
                continue

    def _read_config(self, voice: VoiceInfo, *, original: bool = False) -> str:
        target = self._backup_path_for(voice.config) if original else voice.config
        try:
            return target.read_text(encoding="utf-8")
        except OSError as exc:
            raise ConfigError("No se pudo leer el archivo de configuración") from exc

    def get_config(self, voice_id: str) -> Dict[str, str]:
        voice = self._get_voice(voice_id)
        self._ensure_config_backups()
        return {
            "config": self._read_config(voice, original=False),
            "original": self._read_config(voice, original=True),
            "path": str(voice.config),
        }

    def update_config(self, voice_id: str, raw_content: str) -> Dict[str, str]:
        voice = self._get_voice(voice_id)
        self._ensure_config_backups()

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            raise ConfigError("El archivo de configuración no es un JSON válido") from exc

        try:
            formatted = json.dumps(parsed, ensure_ascii=False, indent=2)
            voice.config.write_text(formatted + "\n", encoding="utf-8")
        except OSError as exc:
            raise ConfigError("No se pudo guardar el archivo de configuración") from exc

        self._voice_cache.pop(voice.id, None)
        return {"config": formatted}

    def restore_config(self, voice_id: str) -> Dict[str, str]:
        voice = self._get_voice(voice_id)
        backup_path = self._backup_path_for(voice.config)

        if not backup_path.exists():
            raise ConfigError("No existe un respaldo para esta configuración")

        try:
            voice.config.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
        except OSError as exc:
            raise ConfigError("No se pudo restaurar el archivo de configuración") from exc

        self._voice_cache.pop(voice.id, None)
        return {"config": self._read_config(voice)}

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
            # Si la carga falla, intentar una resincro rápida de modelos una sola vez.
            if self._sync_inflight:
                raise SynthesisError(
                    "El modelo o su configuración parecen estar dañados incluso tras reintentar."
                ) from exc

            self._sync_inflight = True
            try:
                synced, message = sync_models_if_needed()
                if synced:
                    self._refresh_catalog()
                    # Reintentar con la información refrescada del catálogo.
                    voice = self._get_voice(voice.id)
                    loaded = PiperVoice.load(str(voice.model), config_path=str(voice.config))
                else:
                    raise SynthesisError(
                        "No se pudieron re-sincronizar los modelos automáticamente: " + message
                    ) from exc
            finally:
                self._sync_inflight = False
        self._voice_cache[voice.id] = loaded
        return loaded

    def synthesize(self, text: str, voice_id: str, speed: float = 1.0) -> Tuple[str, Path]:
        if not text.strip():
            raise SynthesisError("El texto está vacío")

        voice = self._get_voice(voice_id)
        length_scale = max(0.25, min(4.0, 1.0 / max(speed, 0.1)))
        filename = f"tts_{uuid.uuid4().hex}.wav"
        output_path = OUTPUT_DIR / filename

        segments = self._split_text_by_pause_tags(text)

        if len(segments) == 1 and segments[0][0] == "text":
            with self._lock:
                model = self._load_or_get_model(voice)
                self._synthesize_to_file(model, text, output_path, length_scale)
            return filename, output_path

        with self._lock:
            model = self._load_or_get_model(voice)
            self._synthesize_with_pauses(model, voice, segments, output_path, length_scale)

        return filename, output_path

    def _synthesize_to_file(
        self, model: PiperVoice, text: str, output_path: Path, length_scale: float
    ) -> None:
        """Genera el audio manejando versiones nuevas y antiguas de Piper."""

        sig = inspect.signature(model.synthesize)
        params = list(sig.parameters.values())

        try:
            # Versiones recientes exigen ``wav_file`` como argumento posicional
            # y esperan un manejador abierto, no una ruta en cadena.
            if len(params) >= 2 and params[1].name == "wav_file":
                with wave.open(str(output_path), "wb") as wav_file:
                    model.synthesize(text, wav_file, length_scale=length_scale)
                return

            # Versiones antiguas devuelven los bytes o el tuple (audio, sample_rate).
            audio_output = model.synthesize(text, length_scale=length_scale)
        except TypeError as exc:
            # Si la introspección falló, intenta la ruta inversa.
            try:
                model.synthesize(text, str(output_path), length_scale=length_scale)
                return
            except TypeError as inner_exc:  # pragma: no cover - dependiente de versión
                raise SynthesisError(
                    "La firma de PiperVoice.synthesize no es compatible: se esperaba un path o un manejador WAV."
                ) from inner_exc
        
        if isinstance(audio_output, tuple):
            audio_data, sample_rate = audio_output
            sf.write(output_path, audio_data, int(sample_rate))
        elif isinstance(audio_output, (bytes, bytearray)):
            output_path.write_bytes(audio_output)
        else:
            raise SynthesisError("La librería Piper devolvió un formato de audio inesperado")

    def _synthesize_with_pauses(
        self,
        model: PiperVoice,
        voice: VoiceInfo,
        segments: List[Tuple[str, int | str]],
        output_path: Path,
        length_scale: float,
    ) -> None:
        sample_rate = self._get_sample_rate(voice)
        num_channels = self._get_num_channels(voice)
        temp_files: List[Path] = []
        audio_chunks: List[np.ndarray] = []

        try:
            for kind, content in segments:
                if kind == "pause":
                    pause_ms = int(content)
                    silence = self._build_silence(sample_rate, num_channels, pause_ms)
                    if silence is not None:
                        audio_chunks.append(silence)
                    continue

                part_path = OUTPUT_DIR / f"part_{uuid.uuid4().hex}.wav"
                text_chunk = str(content)
                self._synthesize_to_file(model, text_chunk, part_path, length_scale)
                temp_files.append(part_path)

                audio_data, part_sample_rate = sf.read(part_path, dtype="float32")

                if part_sample_rate <= 0:
                    raise SynthesisError("La parte sintetizada tiene una tasa de muestreo inválida")

                if sample_rate is None:
                    sample_rate = int(part_sample_rate)
                elif int(part_sample_rate) != int(sample_rate):
                    raise SynthesisError(
                        "Las partes sintetizadas tienen diferentes tasas de muestreo; no se pueden concatenar"
                    )

                if audio_data.ndim > 1:
                    num_channels = audio_data.shape[1]
                else:
                    num_channels = 1

                audio_chunks.append(audio_data)

            if not audio_chunks:
                raise SynthesisError("El texto no contiene fragmentos sintetizables")

            if sample_rate is None:
                raise SynthesisError("No se pudo determinar la tasa de muestreo para el audio de salida")

            merged = np.concatenate(audio_chunks, axis=0)
            sf.write(output_path, merged, int(sample_rate))
        finally:
            for part in temp_files:
                try:
                    part.unlink()
                except OSError:
                    pass

    @staticmethod
    def _split_text_by_pause_tags(text: str) -> List[Tuple[str, int | str]]:
        pattern = re.compile(r"<p\s*=\s*(\d+)\s*>", flags=re.IGNORECASE)
        segments: List[Tuple[str, int | str]] = []
        last_index = 0

        for match in pattern.finditer(text):
            start, end = match.span()
            before = text[last_index:start].strip()
            if before:
                segments.append(("text", before))

            duration_ms = int(match.group(1))
            if duration_ms > 0:
                segments.append(("pause", duration_ms))

            last_index = end

        tail = text[last_index:].strip()
        if tail:
            segments.append(("text", tail))

        return segments or [("text", text.strip())]

    @staticmethod
    def _get_sample_rate(voice: VoiceInfo) -> int | None:
        try:
            data = json.loads(voice.config.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

        audio_cfg = data.get("audio", {}) if isinstance(data, dict) else {}
        for key in ("sample_rate", "sampleRate"):
            value = audio_cfg.get(key) if isinstance(audio_cfg, dict) else None
            if isinstance(value, (int, float)) and value > 0:
                return int(value)

        for key in ("sample_rate", "sampleRate"):
            value = data.get(key) if isinstance(data, dict) else None
            if isinstance(value, (int, float)) and value > 0:
                return int(value)

        return None

    @staticmethod
    def _get_num_channels(voice: VoiceInfo) -> int:
        try:
            data: Any = json.loads(voice.config.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return 1

        audio_cfg = data.get("audio", {}) if isinstance(data, dict) else {}
        if isinstance(audio_cfg, dict):
            channels = audio_cfg.get("num_channels") or audio_cfg.get("channels")
            if isinstance(channels, int) and channels > 0:
                return channels

        return 1

    @staticmethod
    def _build_silence(sample_rate: int | None, num_channels: int, pause_ms: int) -> np.ndarray | None:
        if sample_rate is None or pause_ms <= 0:
            return None

        frames = int(round(sample_rate * (pause_ms / 1000.0)))
        if frames <= 0:
            return None

        shape = (frames, max(1, num_channels)) if num_channels > 1 else (frames,)
        return np.zeros(shape, dtype="float32")


__all__ = [
    "TTSEngine",
    "VoiceNotFoundError",
    "SynthesisError",
    "VoiceInfo",
    "OUTPUT_DIR",
    "ConfigError",
    "CONFIG_BACKUP_DIR",
]
