# Standard python-slim-bookworm as the base
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Install uv using pip
RUN pip install --no-cache-dir uv

# Set the virtualenv location outside of /app so it's not hidden by volumes
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

# Install dependencies only
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

# Final stage
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy venv from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY . .

# Create storage directories
RUN mkdir -p /app/storage/pdfs /app/storage/datalab

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
