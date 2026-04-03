@echo off
echo ========================================
echo   GitHub Profile Analyzer
echo ========================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Virtual environment not detected.
    echo.
    echo Activating venv...
    if exist venv\Scripts\activate.bat (
        call venv\Scripts\activate.bat
    ) else (
        echo ERROR: venv not found!
        echo Please run: python -m venv venv
        echo Then: venv\Scripts\activate
        echo Then: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo.
echo Starting application...
echo.
python run.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start!
    echo.
    pause
)
