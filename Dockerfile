FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ffmpeg espeak-ng libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY model_sync.py ./
COPY tts_engine.py ./
COPY templates templates/
COPY static static/
COPY models models/

ENV FLASK_APP=app.py
ENV API_BASE_URL=

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
