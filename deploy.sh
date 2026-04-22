#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$HOME/pdf-buddy"
BACKEND_DIR="$REPO_DIR/backend"

echo "==> Pulling latest code..."
cd "$REPO_DIR"
git pull origin deploy/simplify

echo "==> Installing/updating Python dependencies..."
cd "$BACKEND_DIR"
uv sync --frozen

echo "==> Running database migrations..."
uv run alembic upgrade head

echo "==> Restarting services..."
sudo systemctl restart pdfbuddy-api
sudo systemctl restart pdfbuddy-celery
sudo systemctl restart pdfbuddy-celery-datalab

echo "==> Checking service status..."
sleep 2
sudo systemctl --no-pager status pdfbuddy-api pdfbuddy-celery pdfbuddy-celery-datalab

echo ""
echo "Deploy complete. Health check:"
curl -s http://localhost:8001/health | python3 -m json.tool 2>/dev/null || echo "API not responding yet (may need a few seconds)"
