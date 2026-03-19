@echo off
REM Expense Approval Workflow - Startup Script
REM This script starts the Flask web application

echo.
echo ========================================
echo   EXPENSE APPROVAL WORKFLOW SYSTEM
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
    echo Installing dependencies...
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting Flask Application...
echo.
echo Web Server Starting on: http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo.
echo ========================================
echo.

python workflow_app.py
