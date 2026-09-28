# syntax=docker/dockerfile:1
FROM python:3.12-slim

LABEL maintainer="pk" \
      description="Modular async web crawler" \
      version="2.0"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy modular components
COPY fetcher.py parser.py storage.py crawler.py validators.py observability.py main.py ./

ENV PYTHONUNBUFFERED=1

# Non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN mkdir -p /app/output && chown appuser:appuser /app/output
USER appuser

ENTRYPOINT ["python", "main.py"]

