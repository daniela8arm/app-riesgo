FROM python:3.11-slim

WORKDIR /app

# Dependencias necesarias para PyMuPDF, Matplotlib y WordCloud
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargar recursos de NLTK
RUN python3 -m nltk.downloader punkt stopwords

# Copiar el proyecto
COPY . .

# Crear carpetas necesarias
RUN mkdir -p uploads static

# Comando para arrancar Flask con Gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT app_riesgo:app
