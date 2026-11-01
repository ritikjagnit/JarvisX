@echo off
TITLE JarvisX - 1-Click Client Environment Setup
echo ========================================================
echo         JarvisX - Client Environment Installer
echo ========================================================
echo.

:: 1. Check Python Availability
set PYTHON_CMD=python
python --version >nul 2>&1
if %errorlevel% equ 0 goto CREATE_VENV

set PYTHON_CMD=py
py --version >nul 2>&1
if %errorlevel% equ 0 goto CREATE_VENV

echo [ERROR] Python is not installed or not added to PATH!
echo.
echo Please download Python 3.10 or higher from https://www.python.org/downloads/
echo IMPORTANT: Make sure to check "Add Python.exe to PATH" during installation!
echo.
pause
exit /b 1

:CREATE_VENV
echo [1/3] Creating Python Virtual Environment (.venv) using %PYTHON_CMD%...
%PYTHON_CMD% -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo.
echo [2/3] Upgrading Pip package manager...
.\.venv\Scripts\python.exe -m pip install --upgrade pip --prefer-binary

echo.
echo [3/3] Installing all required dependencies from requirements.txt...
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --prefer-binary

echo.
echo ========================================================
echo   SETUP COMPLETE! You can now double-click 'run_jarvis.bat'
echo ========================================================
pause
