#!/usr/bin/env python3
"""
Script para descargar modelos de voz en español de Piper TTS
VERSIÓN EXTENDIDA - Incluye todas las voces disponibles
"""
import os
import requests
from pathlib import Path

# Directorio de modelos
MODELS_DIR = Path("/app/models")
MODELS_DIR.mkdir(exist_ok=True)

# ============================================================================
# TODAS LAS VOCES DISPONIBLES EN ESPAÑOL
# ============================================================================
# Puedes comentar las que NO quieras descargar con un '#' al inicio
# ============================================================================

MODELS = {
    # ========== ESPAÑA (Castellano) ==========
    
    "es_ES-davefx-medium": {
        "url_model": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx",
        "url_config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json",
        "name": "David (España)",
        "description": "Voz masculina natural y clara",
        "gender": "male",
        "quality": "medium",
        "size_mb": 60,
        "accent": "España"
    },
    
    "es_ES-mls_10246-low": {
        "url_model": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_10246/low/es_ES-mls_10246-low.onnx",
        "url_config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_10246/low/es_ES-mls_10246-low.onnx.json",
        "name": "María (España)",
        "description": "Voz femenina clara y profesional",
        "gender": "female",
        "quality": "low",
        "size_mb": 25,
        "accent": "España"
    },
    
    "es_ES-mls_9972-low": {
        "url_model": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_9972/low/es_ES-mls_9972-low.onnx",
        "url_config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_9972/low/es_ES-mls_9972-low.onnx.json",
        "name": "Carlos (España)",
        "description": "Voz masculina profesional",
        "gender": "male",
        "quality": "low",
        "size_mb": 25,
        "accent": "España"
    },
    
    "es_ES-sharvard-medium": {
        "url_model": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx",
        "url_config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json",
        "name": "Sandra (España)",
        "description": "Voz femenina equilibrada",
        "gender": "female",
        "quality": "medium",
        "size_mb": 60,
        "accent": "España"
    },
    
    # ========== MÉXICO (Latinoamérica) ==========
    
    "es_MX-claude-high": {
        "url_model": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/claude/high/es_MX-claude-high.onnx",
        "url_config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/claude/high/es_MX-claude-high.onnx.json",
        "name": "Claudia (México)",
        "description": "Voz femenina premium de máxima calidad",
        "gender": "female",
        "quality": "high",
        "size_mb": 90,
        "accent": "México"
    },
    
    # ========== ARGENTINA (Rioplatense) ==========
    
    "es_AR-glow_tts-medium": {
        "url_model": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_AR/glow_tts/medium/es_AR-glow_tts-medium.onnx",
        "url_config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_AR/glow_tts/medium/es_AR-glow_tts-medium.onnx.json",
        "name": "Gonzalo (Argentina)",
        "description": "Voz masculina con acento argentino",
        "gender": "male",
        "quality": "medium",
        "size_mb": 60,
        "accent": "Argentina"
    },

    # ========== CASTELLANO NEUTRO ADICIONAL ==========

    "es_ES-carlfm-medium": {
        "url_model": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/carlfm/medium/es_ES-carlfm-medium.onnx",
        "url_config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/carlfm/medium/es_ES-carlfm-medium.onnx.json",
        "name": "Carlos FM (España)",
        "description": "Voz masculina equilibrada para uso general",
        "gender": "male",
        "quality": "medium",
        "size_mb": 70,
        "accent": "España"
    },

    "es_ES-mls_1840-low": {
        "url_model": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_1840/low/es_ES-mls_1840-low.onnx",
        "url_config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_1840/low/es_ES-mls_1840-low.onnx.json",
        "name": "Lucía (España)",
        "description": "Voz femenina cálida basada en MLS",
        "gender": "female",
        "quality": "low",
        "size_mb": 25,
        "accent": "España"
    },

    "es_ES-mls_11646-low": {
        "url_model": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_11646/low/es_ES-mls_11646-low.onnx",
        "url_config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_11646/low/es_ES-mls_11646-low.onnx.json",
        "name": "Pablo (España)",
        "description": "Voz masculina neutra basada en MLS",
        "gender": "male",
        "quality": "low",
        "size_mb": 25,
        "accent": "España"
    },
    
    # ========== COLOMBIA ==========
    
    # Nota: Actualmente no hay modelos específicos de Colombia en la base
    # Los modelos de México son los más similares fonéticamente
    
    # ========== VOCES ADICIONALES DE CALIDAD BAJA (MÁS RÁPIDAS) ==========
    
    "es_ES-mls_518-low": {
        "url_model": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_518/low/es_ES-mls_518-low.onnx",
        "url_config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_518/low/es_ES-mls_518-low.onnx.json",
        "name": "Laura (España)",
        "description": "Voz femenina rápida para pruebas",
        "gender": "female",
        "quality": "low",
        "size_mb": 20,
        "accent": "España"
    },
}

def download_file(url, destination):
    """Descarga un archivo desde una URL"""
    print(f"  Descargando {destination.name}...")
    try:
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"    Progreso: {percent:.1f}%", end='\r')
        
        print(f"  ✓ Descargado: {destination.name} ({downloaded / (1024*1024):.1f} MB)")
        return True
    except Exception as e:
        print(f"  ✗ Error descargando {destination.name}: {e}")
        return False

def main():
    print("=" * 70)
    print("  DESCARGA DE MODELOS DE VOZ - PIPER TTS")
    print("  Versión Extendida con Todas las Voces en Español")
    print("=" * 70)
    print()
    
    # Mostrar resumen de voces a descargar
    print("📊 RESUMEN DE VOCES A DESCARGAR:")
    print()
    
    by_accent = {}
    total_size = 0
    
    for model_id, info in MODELS.items():
        accent = info['accent']
        if accent not in by_accent:
            by_accent[accent] = {'male': [], 'female': []}
        by_accent[accent][info['gender']].append(info['name'])
        total_size += info['size_mb']
    
    for accent, voices in sorted(by_accent.items()):
        print(f"  🌍 {accent}:")
        if voices['male']:
            print(f"     Masculinas: {', '.join(voices['male'])}")
        if voices['female']:
            print(f"     Femeninas: {', '.join(voices['female'])}")
        print()
    
    print(f"  Total de voces: {len(MODELS)}")
    print(f"  Tamaño total aproximado: ~{total_size} MB")
    print()
    print("=" * 70)
    print()
    
    # Inicio automático (sin confirmación para Docker build)
    print("Iniciando descarga automática...")
    print()
    
    success_count = 0
    total_models = len(MODELS)
    
    for i, (model_id, model_info) in enumerate(MODELS.items(), 1):
        print(f"[{i}/{total_models}] {model_info['name']} ({model_info['accent']})")
        print(f"  Descripción: {model_info['description']}")
        print(f"  Calidad: {model_info['quality']} | Tamaño: ~{model_info['size_mb']} MB")
        
        model_path = MODELS_DIR / f"{model_id}.onnx"
        config_path = MODELS_DIR / f"{model_id}.onnx.json"
        
        # Descargar modelo
        if not model_path.exists():
            if download_file(model_info['url_model'], model_path):
                success_count += 0.5
        else:
            print(f"  ✓ Modelo ya existe: {model_path.name}")
            success_count += 0.5
        
        # Descargar configuración
        if not config_path.exists():
            if download_file(model_info['url_config'], config_path):
                success_count += 0.5
        else:
            print(f"  ✓ Config ya existe: {config_path.name}")
            success_count += 0.5
        
        print()
    
    print("=" * 70)
    print(f"✓ Proceso completado: {int(success_count)}/{total_models} modelos descargados")
    print("=" * 70)

if __name__ == "__main__":
    main()