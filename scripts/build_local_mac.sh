#!/usr/bin/env bash
set -euo pipefail

# remove previous build artifacts
rm -rf build dist *.spec

# On macOS and Linux the add-data separator is ':'
# Build a macOS .app bundle (GUI) instead of a single-file executable
uv run pyinstaller --noconfirm --clean --windowed --name "Teabloom Garden" \
  --add-data "assets:assets" \
  --add-data "data:data" \
  main.py

echo "Built: dist/$(basename main.py .py)"
