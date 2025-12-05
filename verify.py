#!/usr/bin/env python3
"""
Script de verificación del sistema TTS Professional
Verifica que todos los componentes estén correctamente instalados
"""
import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_mark(condition):
    return "✓" if condition else "✗"

def main():
    print_header("TTS Professional - Verificación del Sistema")
    
    # Verificar estructura de directorios
    print("\n1. Estructura de directorios:")
    required_dirs = [
        "templates",
        "static/css",
        "static/js",
        "models",
        "uploads",
        "outputs"
    ]
    
    all_dirs_ok = True
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        all_dirs_ok = all_dirs_ok and exists
        print(f"   {check_mark(exists)} {dir_path}")
    
    # Verificar archivos principales
    print("\n2. Archivos principales:")
    required_files = [
        "app.py",
        "download_models.py",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "templates/index.html",
        "static/css/styles.css",
        "static/js/app.js"
    ]
    
    all_files_ok = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        all_files_ok = all_files_ok and exists
        print(f"   {check_mark(exists)} {file_path}")
    
    # Verificar modelos de voz
    print("\n3. Modelos de voz:")
    models_dir = Path("models")
    if models_dir.exists():
        onnx_files = list(models_dir.glob("*.onnx"))
        json_files = list(models_dir.glob("*.json"))
        
        print(f"   {check_mark(len(onnx_files) > 0)} Modelos .onnx encontrados: {len(onnx_files)}")
        print(f"   {check_mark(len(json_files) > 0)} Archivos de config .json encontrados: {len(json_files)}")
        
        if len(onnx_files) > 0:
            print("\n   Modelos disponibles:")
            for model in sorted(onnx_files):
                size_mb = model.stat().st_size / (1024 * 1024)
                print(f"      • {model.name} ({size_mb:.1f} MB)")
    else:
        print(f"   {check_mark(False)} Directorio de modelos no encontrado")
    
    # Verificar dependencias Python
    print("\n4. Dependencias Python:")
    try:
        import flask
        print(f"   {check_mark(True)} Flask {flask.__version__}")
    except ImportError:
        print(f"   {check_mark(False)} Flask no instalado")
    
    try:
        import numpy
        print(f"   {check_mark(True)} NumPy {numpy.__version__}")
    except ImportError:
        print(f"   {check_mark(False)} NumPy no instalado")
    
    # Resumen
    print("\n" + "="*60)
    if all_dirs_ok and all_files_ok:
        print("  ✓ Sistema verificado correctamente")
        print("  Ejecuta './start.sh' para iniciar la aplicación")
    else:
        print("  ✗ Se encontraron problemas en la verificación")
        print("  Por favor, revisa los elementos marcados con ✗")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
