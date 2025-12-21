# Builder stage
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Create a virtual environment at /opt/venv
RUN uv venv /opt/venv

# Install dependencies
# We copy README.md because pyproject.toml references it
COPY pyproject.toml uv.lock README.md ./
RUN VIRTUAL_ENV=/opt/venv uv pip install .

# Final stage
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the venv from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY . .

# Create storage directories
RUN mkdir -p /app/storage/pdfs /app/storage/datalab

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
