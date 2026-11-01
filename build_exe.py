"""
JarvisX Automated Windows Executable (.exe) Compiler using PyInstaller.

Usage:
  python build_exe.py           # Compiles into dist/JarvisX/ and creates dist/JarvisX_Setup.zip (Recommended)
  python build_exe.py --onefile # Compiles into single standalone dist/JarvisX.exe
"""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path

def build():
    project_root = Path(__file__).resolve().parent
    is_onefile = "--onefile" in sys.argv

    print("========================================================")
    print("      JarvisX Windows Executable (.exe) Compiler        ")
    print("========================================================")
    print(f"Target Mode: {'Single File (.exe)' if is_onefile else 'Directory Package (dist/JarvisX/)'}")
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
        "--console",  # Keep console window for startup logs & camera diagnostic status
        "--onefile" if is_onefile else "--onedir",
        # Asset directories & templates
        "--add-data=jarvis_data/sfx;jarvis_data/sfx",
        "--add-data=jarvis_data/voice_settings.json;jarvis_data",
        "--add-data=jarvis_data/memory.json;jarvis_data",
        "--add-data=ui;ui",
        "--add-data=web_remote;web_remote",
        "--add-data=letter_writer;letter_writer",
        "--add-data=plugins;plugins",
        # Collect models & binary data packages
        "--collect-all=vosk",
        "--collect-all=sounddevice",
        "--collect-all=_sounddevice_data",
        "--collect-all=face_recognition_models",
        # Hidden imports
        "--hidden-import=face_recognition",
        "--hidden-import=face_recognition_models",
        "--hidden-import=cv2",
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=pyautogui",
        "--hidden-import=pyttsx3",
        "--hidden-import=speech_recognition",
        "--hidden-import=sounddevice",
        "--hidden-import=vosk",
        "--hidden-import=psutil",
        "--hidden-import=plyer",
        "--hidden-import=fitz",
        "--hidden-import=pymupdf",
        "--hidden-import=comtypes",
        "--hidden-import=comtypes.stream",
        "--hidden-import=numpy",
        "--hidden-import=engineio.async_drivers.threading",
        # Main entry script
        str(project_root / "main.py")
    ]

    print("\n[BUILD] Running PyInstaller compilation pipeline...")
    res = subprocess.run(cmd, cwd=project_root)
    if res.returncode == 0:
        print("\n========================================================")
        print("  BUILD SUCCESSFUL! Windows Executable Generated!       ")
        print("========================================================")
        if is_onefile:
            exe_path = dist_dir / "JarvisX.exe"
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Standalone Executable: {exe_path} ({size_mb:.2f} MB)")
        else:
            exe_folder = dist_dir / "JarvisX"
            exe_path = exe_folder / "JarvisX.exe"
            print(f"Executable Location: {exe_path}")
            print(f"Directory: {exe_folder}")

            # Ensure essential assets exist directly in executable folder for runtime access
            for asset_folder in ["jarvis_data", "letter_writer"]:
                src = project_root / asset_folder
                dst = exe_folder / asset_folder
                if src.exists() and not dst.exists():
                    shutil.copytree(src, dst)

            # Also create zip for distribution
            zip_out = dist_dir / "JarvisX_Windows_Setup.zip"
            print(f"\n[ZIP] Creating release distribution ZIP: {zip_out.name}...")
            with zipfile.ZipFile(zip_out, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(exe_folder):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, dist_dir)
                        zipf.write(full_path, arcname)
            zip_size = zip_out.stat().st_size / (1024 * 1024)
            print(f"Release Archive: {zip_out} ({zip_size:.2f} MB)")

        print("========================================================\n")
    else:
        print(f"\n[BUILD ERROR] PyInstaller exited with return code {res.returncode}")
        sys.exit(res.returncode)

if __name__ == "__main__":
    build()
