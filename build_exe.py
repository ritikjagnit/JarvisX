"""
JarvisX Automated Windows Executable (.exe) Compiler using PyInstaller.

Usage:
  python build_exe.py           # Compiles into dist/JarvisX/ (Fastest startup)
  python build_exe.py --onefile # Compiles into single standalone dist/JarvisX.exe
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build():
    project_root = Path(__file__).resolve().parent
    is_onefile = "--onefile" in sys.argv

    print("========================================================")
    print("      JarvisX Windows Executable (.exe) Compiler        ")
    print("========================================================")
    print(f"Target Mode: {'Single File Standalone (.exe)' if is_onefile else 'Directory Package (dist/JarvisX/)'}")
    print(f"Working Directory: {project_root}")

    # Verify PyInstaller is installed
    try:
        import PyInstaller
        print(f"[OK] Found PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("[ERROR] PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Clean old build artifacts
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)

    # PyInstaller arguments
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=JarvisX",
        "--noconfirm",
        "--clean",
        "--console",  # Keep console for diagnostic output and camera status logs
        f"--onedir" if not is_onefile else "--onefile",
        # Asset directories
        "--add-data=jarvis_data/sfx;jarvis_data/sfx",
        "--add-data=ui;ui",
        "--add-data=web_remote;web_remote",
        # Collect models & data
        "--collect-all=face_recognition_models",
        # Hidden imports
        "--hidden-import=face_recognition",
        "--hidden-import=cv2",
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=pyautogui",
        "--hidden-import=pyttsx3",
        "--hidden-import=comtypes",
        "--hidden-import=comtypes.stream",
        "--hidden-import=numpy",
        "--hidden-import=engineio.async_drivers.threading",
        # Main entry script
        str(project_root / "main.py")
    ]

    print("\n[BUILD] Running PyInstaller compilation pipeline...")
    print(f"Command: {' '.join(cmd[:6])} ... [assets & hidden imports] ... main.py\n")

    res = subprocess.run(cmd, cwd=project_root)
    if res.returncode == 0:
        print("\n========================================================")
        print("  BUILD SUCCESSFUL! Windows Executable Generated!       ")
        print("========================================================")
        if is_onefile:
            exe_path = dist_dir / "JarvisX.exe"
            print(f"Standalone Executable: {exe_path}")
        else:
            exe_path = dist_dir / "JarvisX" / "JarvisX.exe"
            print(f"Executable Location: {exe_path}")
            print(f"Folder to distribute: {dist_dir / 'JarvisX'}")
        print("========================================================\n")
    else:
        print(f"\n[BUILD ERROR] PyInstaller exited with return code {res.returncode}")
        sys.exit(res.returncode)

if __name__ == "__main__":
    build()

