#!/usr/bin/env bash
set -e

# Start BoonMindX Capital Shield API server for local load testing
# From repo root

cd "$(dirname "$0")/.."

# Set PYTHONPATH to repo root to ensure app module can be imported
export PYTHONPATH="${PWD}:${PYTHONPATH}"

echo "Starting BoonMindX Capital Shield API server..."
echo "Server will be available at http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

# Sanity check: verify app module can be imported
echo "Verifying app import..."
python3 -c "from app.main import app; print('✅ App import OK')" || {
    echo "❌ ERROR: Cannot import app module. Check PYTHONPATH and module structure."
    exit 1
}
echo ""

# Start API with uvicorn on 0.0.0.0:8000
# Using python3 -m uvicorn for more robust module resolution
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


