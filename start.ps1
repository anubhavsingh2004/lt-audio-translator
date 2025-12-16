# L&T Audio Translator - Quick Start Script for PowerShell
# Full Offline Speech-to-Speech Translation

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "L&T Live Audio Translator" -ForegroundColor Green
Write-Host "Full Offline Speech-to-Speech Translation" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the correct directory
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: backend folder not found!" -ForegroundColor Red
    Write-Host "Please run this script from the lt-audio-translator directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "frontend")) {
    Write-Host "ERROR: frontend folder not found!" -ForegroundColor Red
    Write-Host "Please run this script from the lt-audio-translator directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if backend virtual environment exists
if (-not (Test-Path "backend\venv")) {
    Write-Host ""
    Write-Host "[!] Backend virtual environment not found" -ForegroundColor Yellow
    Write-Host "[!] Please run setup first:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    cd backend" -ForegroundColor Cyan
    Write-Host "    python -m venv venv" -ForegroundColor Cyan
    Write-Host "    venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "    pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host "    python download_models.py" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if frontend node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host ""
    Write-Host "[!] Frontend dependencies not found" -ForegroundColor Yellow
    Write-Host "[!] Please run setup first:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    cd frontend" -ForegroundColor Cyan
    Write-Host "    npm install" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/2] Starting Backend Server..." -ForegroundColor Green
Write-Host ""

# Start backend in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\Activate.ps1; python main.py" -WindowStyle Normal

# Wait for backend to start
Start-Sleep -Seconds 3

Write-Host "[2/2] Starting Frontend..." -ForegroundColor Green
Write-Host ""

# Start frontend in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm start" -WindowStyle Normal

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Application is starting..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Two new PowerShell windows have been opened:" -ForegroundColor White
Write-Host "  1. Backend Server (Python)" -ForegroundColor Cyan
Write-Host "  2. Frontend Dev Server (React)" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop: Close both PowerShell windows" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to close this window"
