#!/usr/bin/env bash
# Build script for Render deployment
# This script runs during the build phase

set -o errexit  # Exit on error
set -o nounset  # Exit on undefined variable
set -o pipefail # Exit on pipe failure

echo "========================================="
echo "Starting Render Build Process"
echo "========================================="

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

echo "========================================="
echo "Build completed successfully! ✅"
echo "========================================="
