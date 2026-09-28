# PowerShell Setup Script for LectureLens
$ErrorActionPreference = "Stop"

Write-Host "=== LectureLens Setup ===" -ForegroundColor Cyan

# Check Python environment
$PythonVersion = python -c "import platform; print(platform.python_version())"
$PythonArch = python -c "import platform; print(platform.machine())"

Write-Host "Detected Python Version: $PythonVersion ($PythonArch)" -ForegroundColor Green

# Create Virtual Environment if not exists
if (-not (Test-Path -Path ".venv")) {
    Write-Host "Creating venv under .venv..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate Venv
$VenvActivate = ".\.venv\Scripts\Activate.ps1"
if (Test-Path -Path $VenvActivate) {
    & $VenvActivate
}

# Upgrade pip & install requirements
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run Environment Check
Write-Host "Running environment check..." -ForegroundColor Yellow
python scripts/check_env.py

Write-Host "`nSetup completed successfully! Run 'scripts/run.ps1' to start the application." -ForegroundColor Green
