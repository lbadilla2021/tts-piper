#!/bin/bash
# Script para bloquear acceso a archivos de GPU/DRM
# Esto previene que ONNX Runtime intente detectar GPU

echo "Bloqueando acceso a archivos de GPU/DRM..."

# Crear directorios dummy si no existen
mkdir -p /sys/class/drm/card0/device 2>/dev/null || true
mkdir -p /sys/class/drm/renderD128/device 2>/dev/null || true

# Crear archivos dummy para prevenir errores
touch /sys/class/drm/card0/device/vendor 2>/dev/null || true
touch /sys/class/drm/card0/device/device 2>/dev/null || true
touch /sys/class/drm/renderD128/device/vendor 2>/dev/null || true

# Escribir valores dummy (IDs de vendor/device ficticios)
echo "0x0000" > /sys/class/drm/card0/device/vendor 2>/dev/null || true
echo "0x0000" > /sys/class/drm/card0/device/device 2>/dev/null || true

echo "✓ Archivos de GPU bloqueados"
