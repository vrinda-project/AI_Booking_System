#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies without version constraints
pip install --upgrade pip
pip install -r requirements-minimal.txt

# Run migrations
python -m alembic upgrade head