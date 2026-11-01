@echo off
TITLE JarvisX - Windows Executable (.exe) Compiler
echo ========================================================
echo       JarvisX - Compiling Standalone Windows .exe
echo ========================================================
echo.

IF EXIST .venv\Scripts\python.exe (
    echo [INFO] Running build_exe.py using local virtual environment...
    .\.venv\Scripts\python.exe build_exe.py %*
) ELSE (
    echo [INFO] Running build_exe.py with system Python...
    python build_exe.py %*
)

echo.
pause
