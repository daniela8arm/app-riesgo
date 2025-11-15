FROM python:3.11-bullseye

WORKDIR /app

# Dependencias necesarias para PyMuPDF + Matplotlib + WordCloud
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libfreetype6 \
    libpng16-16 \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargar NLTK
RUN python3 -m nltk.downloader punkt stopwords

# Copiar proyecto
COPY . .

# Asegurar carpetas
RUN mkdir -p uploads static

# Ejecutar aplicación
CMD gunicorn --bind 0.0.0.0:$PORT app_riesgo:app
