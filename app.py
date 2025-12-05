#!/usr/bin/env python3
"""
Aplicación de Texto a Voz (TTS) usando Piper
Completamente offline y dockerizable
"""
# FORZAR USO DE CPU - DEBE IR ANTES DE TODOS LOS IMPORTS
import os

# Variables de entorno consistentes para que Piper/ONNX no intenten usar GPU
CPU_ENV_VARS = {
    'CUDA_VISIBLE_DEVICES': '',
    'ONNXRUNTIME_PROVIDERS': 'CPUExecutionProvider',
    'ORT_LOGGING_LEVEL': '3',
    'ORT_DISABLE_ALL_OPTIMIZATION': '0',
    'PIPER_USE_CUDA': '0',
    'ORT_DEVICE_TYPE': 'CPU',
}

# Aplicar las variables en el proceso principal
os.environ.update(CPU_ENV_VARS)

from flask import Flask, render_template, request, jsonify, send_file
import json
from pathlib import Path
import wave
import io
import subprocess
import tempfile
from datetime import datetime
import hashlib
import warnings
import logging

# Suprimir warnings de ONNX Runtime sobre GPU
warnings.filterwarnings('ignore', category=UserWarning, module='onnxruntime')

# Configurar logging para no mostrar warnings de ONNX
logging.getLogger('onnxruntime').setLevel(logging.ERROR)
# ... resto del código igual

app = Flask(__name__)

# Configuración
MODELS_DIR = Path("/app/models")
UPLOADS_DIR = Path("/app/uploads")
OUTPUTS_DIR = Path("/app/outputs")

# Crear directorios si no existen
UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# Información de modelos disponibles
AVAILABLE_MODELS = {
    # España (Castellano)
    "es_ES-davefx-medium": {
        "name": "David (España)",
        "gender": "male",
        "accent": "España",
        "quality": "Alta",
        "description": "Voz masculina natural y clara"
    },
    "es_ES-mls_10246-low": {
        "name": "María (España)",
        "gender": "female",
        "accent": "España",
        "quality": "Media",
        "description": "Voz femenina profesional"
    },
    "es_ES-mls_9972-low": {
        "name": "Carlos (España)",
        "gender": "male",
        "accent": "España",
        "quality": "Media",
        "description": "Voz masculina profesional"
    },
    "es_ES-sharvard-medium": {
        "name": "Sandra (España)",
        "gender": "female",
        "accent": "España",
        "quality": "Alta",
        "description": "Voz femenina equilibrada"
    },
    "es_ES-mls_518-low": {
        "name": "Laura (España)",
        "gender": "female",
        "accent": "España",
        "quality": "Rápida",
        "description": "Voz femenina rápida para pruebas"
    },
    
    # México (Latinoamérica)
    "es_MX-claude-high": {
        "name": "Claudia (México)",
        "gender": "female",
        "accent": "México",
        "quality": "Premium",
        "description": "Voz femenina de máxima calidad"
    },
    
    # Argentina (Rioplatense)
    "es_AR-glow_tts-medium": {
        "name": "Gonzalo (Argentina)",
        "gender": "male",
        "accent": "Argentina",
        "quality": "Alta",
        "description": "Voz masculina con acento argentino"
    }
}

def get_available_voices():
    """Obtiene las voces disponibles agrupadas por género"""
    voices = {
        "male": [],
        "female": []
    }
    
    for model_id, info in AVAILABLE_MODELS.items():
        model_path = MODELS_DIR / f"{model_id}.onnx"
        if model_path.exists():
            voices[info["gender"]].append({
                "id": model_id,
                "name": info["name"],
                "accent": info["accent"],
                "quality": info["quality"],
                "description": info["description"]
            })
    
    return voices


def sanitize_model_config(config_path: Path):
    """Normaliza el archivo de configuración del modelo para evitar errores.

    Algunas distribuciones antiguas incluyen `PhonemeType.ESPEAK` en vez de
    `espeak`, lo que rompe con versiones recientes de piper-tts. Aquí
    reescribimos el archivo de configuración para dejar un valor compatible y
    forzamos el proveedor de ejecución a CPU por si el JSON trae CUDA.
    """

    if not config_path.exists():
        return

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        updated = False

        # Arreglar valor inválido de phoneme_type
        phoneme_type = config.get('phoneme_type')
        if isinstance(phoneme_type, str) and phoneme_type.upper().startswith('PHONEMETYPE.'):
            config['phoneme_type'] = phoneme_type.split('.', 1)[-1].lower()
            updated = True

        # Forzar proveedor CPU para evitar intentos de usar GPU/CUDA
        inference = config.get('inference', {}) or {}
        providers = inference.get('providers')
        if providers is None or any('CUDA' in provider for provider in providers):
            inference['providers'] = ['CPUExecutionProvider']
            config['inference'] = inference
            updated = True

        if updated:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

    except Exception:
        # No interrumpir el flujo si hay problemas leyendo/escribiendo
        pass

def text_to_speech(text, model_id, output_path, speed=1.0):
    """Convierte texto a voz usando Piper"""
    model_path = MODELS_DIR / f"{model_id}.onnx"
    config_path = MODELS_DIR / f"{model_id}.onnx.json"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Modelo no encontrado: {model_id}")

    # Ajustar configuración del modelo para que sea compatible con CPU
    sanitize_model_config(config_path)
    
    # Crear archivo temporal para el texto
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(text)
        text_file = f.name
    
    try:
        # Ejecutar Piper TTS (forzar uso de CPU, no GPU)
        # Establecer variables de entorno para deshabilitar CUDA
        env = os.environ.copy()
        env.update(CPU_ENV_VARS)
        
        cmd = [
            'piper',
            '--model', str(model_path),
            '--output_file', str(output_path),
            '--length_scale', str(1.0/speed) if speed != 1.0 else '1.0'
        ]
        
        # Pasar texto por stdin y suprimir warnings de stderr
        with open(text_file, 'r', encoding='utf-8') as f:
            with open(os.devnull, 'w') as devnull:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stdout=subprocess.PIPE,
                    stderr=devnull,  # Suprimir stderr (warnings de GPU)
                    text=True,
                    timeout=900,
                    env=env  # Pasar variables de entorno modificadas
                )
        
        # Solo verificar returncode, no stderr (ya que lo suprimimos)
        if result.returncode != 0:
            # Si falla, ejecutar de nuevo CON stderr para ver el error real
            with open(text_file, 'r', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    capture_output=True,
                    text=True,
                    timeout=900,
                    env=env
                )
            raise Exception(f"Error en Piper: {result.stderr}")
        
        return True
    
    finally:
        # Limpiar archivo temporal
        if os.path.exists(text_file):
            os.unlink(text_file)

@app.route('/')
def index():
    """Página principal"""
    voices = get_available_voices()
    return render_template('index.html', voices=voices)

@app.route('/api/voices')
def api_voices():
    """API para obtener voces disponibles"""
    voices = get_available_voices()
    return jsonify(voices)

@app.route('/api/synthesize', methods=['POST'])
def api_synthesize():
    """API para sintetizar texto a voz"""
    try:
        data = request.json
        text = data.get('text', '').strip()
        model_id = data.get('voice', 'es_ES-davefx-medium')
        speed = float(data.get('speed', 1.0))
        
        if not text:
            return jsonify({'error': 'No se proporcionó texto'}), 400
        
        # Validar longitud del texto
        if len(text) > 50000:
            return jsonify({'error': 'El texto es demasiado largo (máximo 50,000 caracteres)'}), 400
        
        # Validar modelo
        if model_id not in AVAILABLE_MODELS:
            return jsonify({'error': 'Modelo de voz no válido'}), 400
        
        # Generar nombre de archivo único
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_{timestamp}_{text_hash}.wav"
        output_path = OUTPUTS_DIR / filename
        
        # Generar audio
        text_to_speech(text, model_id, output_path, speed)
        
        # Verificar que se creó el archivo
        if not output_path.exists():
            return jsonify({'error': 'Error al generar el audio'}), 500
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download/{filename}',
            'voice': AVAILABLE_MODELS[model_id]['name']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-file', methods=['POST'])
def api_upload_file():
    """API para procesar archivos de texto subidos"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se proporcionó archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        
        # Validar extensión
        allowed_extensions = {'.txt', '.md', '.text'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Tipo de archivo no soportado. Use .txt o .md'}), 400
        
        # Leer contenido
        try:
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            try:
                content = file.read().decode('latin-1')
            except:
                return jsonify({'error': 'No se pudo decodificar el archivo. Use codificación UTF-8'}), 400
        
        if len(content) > 50000:
            return jsonify({'error': 'El archivo es demasiado grande (máximo 50,000 caracteres)'}), 400
        
        return jsonify({
            'success': True,
            'text': content,
            'filename': file.filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Descarga un archivo de audio generado"""
    file_path = OUTPUTS_DIR / filename
    
    if not file_path.exists():
        return "Archivo no encontrado", 404
    
    return send_file(
        file_path,
        mimetype='audio/wav',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/stats')
def api_stats():
    """Estadísticas del sistema"""
    voices = get_available_voices()
    total_voices = len(voices['male']) + len(voices['female'])
    
    # Contar archivos generados
    audio_files = list(OUTPUTS_DIR.glob("*.wav"))
    
    return jsonify({
        'total_voices': total_voices,
        'male_voices': len(voices['male']),
        'female_voices': len(voices['female']),
        'generated_files': len(audio_files),
        'models_available': list(AVAILABLE_MODELS.keys())
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("="*60)
    print("Aplicación TTS iniciando...")
    print("="*60)
    print(f"Modelos disponibles: {len(AVAILABLE_MODELS)}")
    voices = get_available_voices()
    print(f"Voces masculinas: {len(voices['male'])}")
    print(f"Voces femeninas: {len(voices['female'])}")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)