@echo off
REM Workflow Management System - Startup Script

echo.
echo ========================================
echo   WORKFLOW MANAGEMENT SYSTEM
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing Flask...
    pip install -q Flask==2.3.0 Werkzeug==2.3.0
    if errorlevel 1 (
        echo ERROR: Failed to install Flask
        pause
        exit /b 1
    )
)

echo Starting Workflow Management System...
echo.
echo Web Server: http://localhost:5000
echo.
echo Features:
echo  - Design and execute workflows
echo  - Define complex approval rules
echo  - Track every step with audit trails
echo  - View complete execution history
echo.
echo Press CTRL+C to stop
echo.
echo ========================================
echo.

python workflow_app.py
