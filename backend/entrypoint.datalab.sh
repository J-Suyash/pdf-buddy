#!/bin/bash
set -e

# Start Xvfb in the background
echo "Starting Xvfb on display $DISPLAY..."
Xvfb :99 -screen 0 1920x1080x24 &
XVFB_PID=$!

# Wait a moment for Xvfb to start
sleep 2

# Run the passed command
exec "$@"
