FROM python:3.10-slim

# Install system dependencies for Prophet and scientific stack
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    liblapack-dev \
    libblas-dev \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

ENV PYTHONPATH=/app

EXPOSE 8501 8000
