FROM python:3.11-slim

WORKDIR /app

# Dependencias mínimas para PyMuPDF y Matplotlib
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python3 -m nltk.downloader punkt stopwords

COPY . .

RUN mkdir -p uploads static

CMD gunicorn --bind 0.0.0.0:$PORT app_riesgo:app
