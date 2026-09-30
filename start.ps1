$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       FitBuddy - Starting Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed or 'py' is not in PATH." -ForegroundColor Red
    Write-Host "Install Python 3.11+ from https://www.python.org/downloads/"
    exit 1
}

if (-not (Test-Path ".\venv")) {
    Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Yellow
    py -m venv venv
}

Write-Host "[2/4] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host "[3/4] Installing required packages..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

if (-not (Test-Path ".\.env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Green
}

Write-Host "[4/4] Starting FitBuddy..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Website:   http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API Docs:  http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press CTRL+C to stop the server." -ForegroundColor Cyan
Write-Host ""

python -m uvicorn app.main:app --reload
