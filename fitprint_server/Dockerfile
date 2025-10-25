# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for Pillow and other libs
RUN apt-get update \ 
    && apt-get install --no-install-recommends -y build-essential libjpeg62-turbo-dev zlib1g-dev \ 
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies separately for better caching
COPY fitprint_server/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \ 
    && pip install --no-cache-dir -r /tmp/requirements.txt

# Copy the application source
COPY fitprint_server /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
