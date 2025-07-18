#!/bin/bash

# Exit on error
set -e

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python -m alembic upgrade head

# Start the application
echo "Starting the application..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}