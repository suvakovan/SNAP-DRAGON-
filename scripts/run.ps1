# PowerShell Run Script for LectureLens
$ErrorActionPreference = "Stop"

Write-Host "=== Launching LectureLens Streamlit App ===" -ForegroundColor Cyan

# Activate Venv if present
if (Test-Path -Path ".\.venv\Scripts\Activate.ps1") {
    & .\.venv\Scripts\Activate.ps1
}

# Run Streamlit
streamlit run lecturelens/ui/app.py
