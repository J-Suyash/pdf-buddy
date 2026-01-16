# Stage 1: Builder
FROM python:3.11-slim-bookworm AS builder

WORKDIR /pkg

# Install uv
RUN pip install --no-cache-dir uv

# Tell uv to use this specific location for the venv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV UV_COMPILE_BYTECODE=1

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into /opt/venv
RUN uv sync --frozen --no-dev --no-install-project

# Stage 2: Runner
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install runtime system dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv

# Copy the venv from builder
COPY --from=builder /opt/venv /opt/venv

# Set up environment variables
# UV_PROJECT_ENVIRONMENT tells 'uv run' where to look for the environment
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY . .

# Create storage directories
RUN mkdir -p /app/storage/pdfs /app/storage/datalab

# Expose port
EXPOSE 8000

# Default command using uv run
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
