@echo off
echo Starting FeelMate Production Chatbot...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import fastapi, transformers, torch" >nul 2>&1
if errorlevel 1 (
    echo Dependencies not found. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies. Please check requirements.txt
        pause
        exit /b 1
    )
)

echo.
echo Starting production server on http://localhost:8001
echo Press Ctrl+C to stop the server
echo.

REM Start the production server
python start_production.py

pause
