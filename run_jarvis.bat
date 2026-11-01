@echo off
TITLE JarvisX - AI Assistant Launcher
echo ========================================================
echo                 JarvisX - Starting AI OS
echo ========================================================
echo.

IF EXIST .venv\Scripts\python.exe (
    echo [INFO] Launching JarvisX using local virtual environment...
    .\.venv\Scripts\python.exe main.py
) ELSE (
    echo [WARNING] .venv not found. Running with system Python...
    python main.py
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with error code %errorlevel%.
)

pause
