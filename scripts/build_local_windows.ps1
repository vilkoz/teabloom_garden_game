#!/usr/bin/env pwsh
# Exit on any error
$ErrorActionPreference = "Stop"

# Remove previous build artifacts
Write-Host "Cleaning previous build artifacts..."
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
Get-Item "*.spec" -ErrorAction SilentlyContinue | Remove-Item -Force

# On Windows the add-data separator is ';'
# Build a Windows executable (GUI)
Write-Host "Building Teabloom Garden..."
uv run pyinstaller --noconfirm --clean --windowed --name "Teabloom Garden" `
  --add-data "assets;assets" `
  --add-data "data;data" `
  main.py

$exeName = "Teabloom Garden.exe"
Write-Host "Built: dist/$exeName"
