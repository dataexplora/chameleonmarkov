FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for music21 (lxml), and for fonts if needed later
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev libxslt1-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8885

# Gunicorn entrypoint
CMD ["gunicorn", "--bind", "0.0.0.0:8885", "chameleon_server:app", "--workers", "2", "--threads", "4", "--timeout", "180"]


