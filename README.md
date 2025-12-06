# TTS Piper Frontend

Frontend liviano para consumir el backend de síntesis del proyecto [`tts-piper-2`](https://github.com/lbadilla2021/tts-piper-2). Este repositorio ahora también sincroniza la carpeta `models` del backend para exponer las voces de manera local al frontend.

## Requisitos

- Python 3.11+
- `tts-piper-2` corriendo y accesible mediante HTTP (para la síntesis)
- Docker opcional para un despliegue contenedor
- Acceso a internet para clonar la carpeta `models` (el servicio seguirá funcionando con los modelos de respaldo si no hay conectividad)

## Configuración

La aplicación obtiene la URL base del backend mediante la variable de entorno `API_BASE_URL` (por ejemplo `http://localhost:8000`). Si no se establece, se usará `http://localhost:8000` por defecto.

## Uso local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export API_BASE_URL=http://localhost:8000
flask run --host=0.0.0.0 --port=5000
```

Abre [http://localhost:5000](http://localhost:5000) en tu navegador y el frontend consumirá el backend configurado.

## Modelos locales

- El endpoint `/api/voices` intenta clonar la carpeta `models` del repositorio [`tts-piper-2`](https://github.com/lbadilla2021/tt-piper-2) usando `git` (se puede sobreescribir con la variable `MODEL_REPO_URL`).
- Si la sincronización falla (por ejemplo por falta de internet) se usa el catálogo local `models/catalog.json` para mantener la interfaz operativa.
- El estado de sincronización se muestra en la etiqueta “Modelos locales” dentro del formulario principal.

## Docker

```bash
docker-compose up --build -d
```

El contenedor expone el puerto `5000` y pasa `API_BASE_URL` al frontend.

## Estructura

```
.
├── app.py            # Servidor Flask mínimo
├── templates/        # Plantilla principal
├── static/           # Assets (JS/CSS)
├── Dockerfile        # Imagen de sólo frontend
└── docker-compose.yml
```

## Salud

El endpoint `/health` devuelve `{ "status": "ok" }` para revisiones de estado o healthchecks.
