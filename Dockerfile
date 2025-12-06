FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear directorios para modelos y archivos
RUN mkdir -p /app/models /app/uploads /app/outputs

# Copiar aplicación
COPY app.py .
COPY templates templates/
COPY static static/
COPY download_models.py .
COPY configure_cpu.py .
COPY entrypoint.sh .
COPY block_gpu.sh .

# Hacer ejecutables los scripts
RUN chmod +x entrypoint.sh block_gpu.sh

# Configurar ONNX para usar solo CPU
RUN python configure_cpu.py

# Descargar modelos de voz al construir la imagen
RUN python download_models.py

# Exponer puerto
EXPOSE 5000

# Variables de entorno
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV CUDA_VISIBLE_DEVICES="-1"
ENV CUDA_DEVICE_ORDER=PCI_BUS_ID
ENV PIPER_USE_CUDA=0
ENV ORT_DISABLE_ALL_OPTIMIZATION=0
ENV ONNXRUNTIME_PROVIDERS=CPUExecutionProvider

# Comando para ejecutar
ENTRYPOINT ["./entrypoint.sh"]
