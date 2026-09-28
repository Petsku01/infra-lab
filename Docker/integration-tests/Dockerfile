# syntax=docker/dockerfile:1
# Uses a more recent Ubuntu base image with a smaller footprint
FROM ubuntu:22.04

# Sets environment variables for non-interactive installs and improved Python behavior
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies in a single layer to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    jq \
    nano \
    git \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only necessary files to leverage Docker caching
COPY requirements.txt .
COPY process.py .

# Make the Bash script executable
# RUN chmod +x script.sh  (script.sh not needed)

# Install Python dependencies in a single layer
RUN pip3 install --no-cache-dir -r requirements.txt

# Use a non-root user for improved security
RUN useradd -m -s /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

# Command to run the Python script
CMD ["python3", "process.py"]
