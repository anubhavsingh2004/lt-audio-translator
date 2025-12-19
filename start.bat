@echo off
REM Audio Translator - Quick Start Script for Windows
REM This script starts both backend and frontend

echo ================================================
echo L^&T Live Audio Translator
echo Full Offline Speech-to-Speech Translation
echo ================================================
echo.

REM Check if we're in the correct directory
if not exist "backend\" (
    echo ERROR: backend folder not found!
    echo Please run this script from the lt-audio-translator directory
    pause
    exit /b 1
)

if not exist "frontend\" (
    echo ERROR: frontend folder not found!
    echo Please run this script from the lt-audio-translator directory
    pause
    exit /b 1
)

REM Check if backend virtual environment exists
if not exist "backend\venv\" (
    echo.
    echo [!] Backend virtual environment not found
    echo [!] Please run setup first:
    echo.
    echo     cd backend
    echo     python -m venv venv
    echo     venv\Scripts\Activate.ps1
    echo     pip install -r requirements.txt
    echo     python download_models.py
    echo.
    pause
    exit /b 1
)

REM Check if frontend node_modules exists
if not exist "frontend\node_modules\" (
    echo.
    echo [!] Frontend dependencies not found
    echo [!] Please run setup first:
    echo.
    echo     cd frontend
    echo     npm install
    echo.
    pause
    exit /b 1
)

echo [1/2] Starting Backend Server...
echo.
start "L&T Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python main.py"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend...
echo.
start "L&T Frontend" cmd /k "cd frontend && npm start"

echo.
echo ================================================
echo Application is starting...
echo ================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Two new windows have been opened:
echo   1. Backend Server (Python)
echo   2. Frontend Dev Server (React)
echo.
echo To stop: Close both terminal windows
echo ================================================
echo.
pause
