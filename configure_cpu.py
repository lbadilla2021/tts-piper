#!/usr/bin/env python3
"""
Configuración de ONNX Runtime para forzar uso de CPU
Este script se ejecuta al inicio para configurar correctamente el entorno
"""
import os
import sys

def configure_onnx_cpu_only():
    """Configura ONNX Runtime para usar solo CPU"""
    
    # Variables de entorno críticas para ONNX Runtime
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    os.environ['ORT_DISABLE_ALL_OPTIMIZATION'] = '0'
    os.environ['ONNXRUNTIME_PROVIDERS'] = 'CPUExecutionProvider'
    
    # Intentar configurar programáticamente si onnxruntime está disponible
    try:
        import onnxruntime as ort
        
        # Obtener proveedores disponibles
        available_providers = ort.get_available_providers()
        print(f"Proveedores ONNX disponibles: {available_providers}")
        
        # Forzar solo CPUExecutionProvider
        if 'CPUExecutionProvider' in available_providers:
            print("✓ CPUExecutionProvider está disponible")
            print("✓ GPU/CUDA será ignorado")
        else:
            print("⚠ Advertencia: CPUExecutionProvider no está disponible")
            
    except ImportError:
        print("ℹ onnxruntime no instalado aún (se instalará con pip)")
    
    print("\n" + "="*60)
    print("Configuración de CPU forzada exitosamente")
    print("Variables de entorno configuradas:")
    print(f"  CUDA_VISIBLE_DEVICES = '{os.environ.get('CUDA_VISIBLE_DEVICES', '')}'")
    print(f"  ONNXRUNTIME_PROVIDERS = {os.environ.get('ONNXRUNTIME_PROVIDERS', '')}")
    print("="*60 + "\n")

if __name__ == "__main__":
    configure_onnx_cpu_only()