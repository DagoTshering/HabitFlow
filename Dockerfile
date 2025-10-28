## Multi-stage Dockerfile for HabitFlow (Flask)

# ===== Builder stage: install dependencies into a clean venv =====
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for psycopg2 and compilation
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment in /opt/venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Only copy requirements to maximize Docker layer caching
COPY requirements.txt ./

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# ===== Runtime stage: minimal image with app and venv =====
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_ENV=production \
    PORT=5000

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd -m appuser

# Copy application code
COPY . /app

# Expose port and set default command (gunicorn)
EXPOSE 5000

# Use gunicorn via Procfile if present, else fallback
CMD ["gunicorn", "-w", "3", "-b", ":5000", "run:app"]


