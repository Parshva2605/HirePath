@echo off
REM HirePath Backend Startup Script for Windows

echo =====================================
echo     HirePath Backend Startup
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "agent" (
    echo ERROR: Please run this script from the hirepath_final directory
    pause
    exit /b 1
)

REM Check if venv exists
if not exist "agent\venv" (
    echo Creating Python virtual environment...
    cd agent
    python -m venv venv
    cd ..
)

REM Activate venv
echo Activating Python virtual environment...
call agent\venv\Scripts\activate.bat

REM Check dependencies
echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r agent\requirements.txt
)

REM Check Ollama connection
echo.
echo Checking Ollama connection...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo WARNING: Ollama is not running!
    echo Please start Ollama with: ollama serve
    echo Some features will be limited without Ollama.
    echo.
) else (
    echo ✓ Ollama is connected
    echo.
)

REM Start FastAPI server
echo =====================================
echo Starting FastAPI Backend on port 8000
echo =====================================
echo.
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/api/status
echo.
echo Press Ctrl+C to stop the server
echo.

cd agent
uvicorn main:app --reload --port 8000

pause
