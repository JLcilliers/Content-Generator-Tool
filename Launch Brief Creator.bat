@echo off
REM Content Brief Creator - One-Click Launcher
REM This launches the Streamlit web app locally

echo.
echo ========================================
echo   Content Brief Creator
echo   Starting web application...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    echo This only needs to happen once.
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please create a .env file with your API keys.
    echo See .env.example for the template.
    echo.
    pause
    exit /b 1
)

REM Launch Streamlit
echo Opening in your browser...
echo.
echo Press Ctrl+C to stop the application
echo.
streamlit run app.py

pause
