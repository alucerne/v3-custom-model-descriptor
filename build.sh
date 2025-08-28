#!/bin/bash
set -e

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Download spaCy model if not already installed
python -m spacy download en_core_web_sm || true

echo "Build completed successfully!"
