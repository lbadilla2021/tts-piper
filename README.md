# TTS Piper Frontend

Frontend liviano para consumir el backend de síntesis del proyecto [`tts-piper-2`](https://github.com/lbadilla2021/tts-piper-2). Este repositorio sólo sirve los assets estáticos y expone la URL del backend al JavaScript del cliente.

## Requisitos

- Python 3.11+
- `tts-piper-2` corriendo y accesible mediante HTTP
- Docker opcional para un despliegue contenedor

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
