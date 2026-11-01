@echo off
title JarvisX Launcher
echo ========================================================
echo       Launching JarvisX Desktop Application (.exe)       
echo ========================================================
cd /d "%~dp0dist\JarvisX"
if not exist "JarvisX.exe" (
    echo [ERROR] JarvisX.exe not found in dist\JarvisX.
    echo Please run build_exe.bat first.
    pause
    exit /b 1
)
start "" "JarvisX.exe"
exit
