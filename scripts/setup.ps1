# LectureLens Setup Script for Windows
# Creates virtual environment, installs dependencies, and runs environment proof

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "     LectureLens Environment Setup       " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Check Python installation
try {
    $pythonVer = python --version 2>&1
    Write-Host "Detected Python: $pythonVer" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    Exit 1
}

# Check Python architecture
$archCheck = python -c "import sysconfig; print(sysconfig.get_platform())"
Write-Host "Python Target Platform: $archCheck" -ForegroundColor Yellow

if ($archCheck -notlike "*arm64*" -and $archCheck -notlike "*aarch64*") {
    Write-Host "[NOTE] Non-ARM64 Python detected ($archCheck). App will run in CPU fallback mode." -ForegroundColor Yellow
}

# 2. Create Virtual Environment
$venvPath = "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment in .\$venvPath..." -ForegroundColor Cyan
    python -m venv $venvPath
} else {
    Write-Host "Virtual environment .\$venvPath already exists." -ForegroundColor Green
}

# 3. Activate Virtual Environment and Upgrade Pip
$activateScript = ".\$venvPath\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & $activateScript
}

Write-Host "Installing project requirements..." -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Run Environment Proof
Write-Host "Running environment proof verification..." -ForegroundColor Cyan
python scripts/env_proof.py

Write-Host "`nSetup complete! Run app with: scripts/run.ps1" -ForegroundColor Green
