#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --user --upgrade pip
python3 -m pip install --user pyinstaller

# remove previous build artifacts
rm -rf build dist *.spec

# On macOS and Linux the add-data separator is ':'
pyinstaller --noconfirm --clean --onefile \
  --add-data "assets:assets" \
  --add-data "data:data" \
  main.py

echo "Built: dist/$(basename main.py .py)"
