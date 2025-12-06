#!/bin/bash
# Entrypoint para TTS Professional
# Configura el entorno para forzar uso de CPU

echo "=================================="
echo "TTS Professional - Iniciando..."
echo "=================================="

# Bloquear archivos de GPU/DRM primero
./block_gpu.sh

# Forzar uso de CPU (deshabilitar CUDA/GPU)
export CUDA_VISIBLE_DEVICES="-1"
export CUDA_DEVICE_ORDER="PCI_BUS_ID"
export ORT_DISABLE_ALL_OPTIMIZATION="0"
export ONNXRUNTIME_PROVIDERS="CPUExecutionProvider"
export PIPER_USE_CUDA="0"

# Verificar que los modelos existen
if [ ! -d "/app/models" ] || [ -z "$(ls -A /app/models)" ]; then
    echo "⚠ Advertencia: No se encontraron modelos de voz"
    echo "Los modelos deberían haberse descargado durante el build"
fi

# Verificar configuración
echo ""
echo "Configuración de CPU:"
echo "  CUDA_VISIBLE_DEVICES = '$CUDA_VISIBLE_DEVICES'"
echo "  CUDA_DEVICE_ORDER = $CUDA_DEVICE_ORDER"
echo "  ONNXRUNTIME_PROVIDERS = $ONNXRUNTIME_PROVIDERS"
echo "  PIPER_USE_CUDA = $PIPER_USE_CUDA"
echo ""

# Ejecutar la aplicación Flask
echo "Iniciando aplicación Flask..."
exec python app.py
