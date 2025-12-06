# TTS Piper Frontend

Frontend liviano con backend integrado basado en Piper TTS. Incluye el formulario web y un servidor Flask que carga los modelos `.onnx` de la carpeta `models` (los binarios pesados se copian manualmente) para generar audio directamente desde esta misma aplicación.

## Requisitos

- Python 3.11+
- Docker opcional para un despliegue contenedor
- Los modelos `.onnx` descargados manualmente (ver sección de modelos)

## Configuración

La aplicación obtiene la URL base del backend mediante la variable de entorno `API_BASE_URL`. Si no se establece, se usa el mismo origen del frontend (backend integrado).

## Uso local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5000
```

Abre [http://localhost:5000](http://localhost:5000) en tu navegador y el frontend consumirá el backend configurado.

## Modelos locales

El catálogo `models/catalog.json` ya incluye 8 voces (4 masculinas y 4 femeninas) para español:

- es_AR-daniela-high
- es_ES-ariadna-medium
- es_ES-carlfm-x_low
- es_ES-davefx-high
- es_ES-mls_9972-low
- es_ES-mls_10246-low
- es_ES-sharvard-medium
- es_MX-claude-high

Para que cada voz funcione, coloca en `models/` el archivo `.onnx` correspondiente junto a su `.onnx.json` (compartían el mismo nombre en el repositorio original). El endpoint `/api/voices` agrupa las voces por género y el endpoint `/api/synthesize` utiliza los modelos locales para generar el audio.

## Docker

```bash
docker-compose up --build -d
```

El contenedor expone el puerto `5000` y usa el backend integrado.

## Estructura

```
.
├── app.py            # Servidor Flask con endpoints /api
├── tts_engine.py     # Motor que carga y cachea los modelos Piper
├── templates/        # Plantilla principal
├── static/           # Assets (JS/CSS)
├── Dockerfile        # Imagen con frontend + backend integrado
└── docker-compose.yml
```

## Salud

El endpoint `/health` devuelve `{ "status": "ok" }` para revisiones de estado o healthchecks.
