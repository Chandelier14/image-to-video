@echo off
setlocal enabledelayedexpansion

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please download and install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Pip is not installed. Attempting to install pip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo Failed to install pip. Please install pip manually.
        pause
        exit /b 1
    )
)

if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing required libraries...
pip install opencv-python-headless PyQt6 Pillow

if %errorlevel% neq 0 (
    echo Failed to install required libraries.
    pause
    exit /b 1
)

echo Running Image to Video Converter...
python main.py

deactivate

pause