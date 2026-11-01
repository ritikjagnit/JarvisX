import os
import shutil
import zipfile
from pathlib import Path

def clean_and_package(output_dir=None):
    """Purges all __pycache__, bytecode, temporary logs, and creates a clean client release ZIP."""
    project_root = Path(__file__).resolve().parent
    
    # Destination directory & zip
    target_base = Path(output_dir) if output_dir else project_root
    release_dir = target_base / "JarvisX_Client_Release"
    zip_filename = target_base / "JarvisX_Client_Release.zip"

    print("========================================================")
    print("      JarvisX Clean Client Release Packaging Tool       ")
    print("========================================================")

    EXCLUDE_DIRS = {".git", ".venv", ".venv-1", "venv", "env", "__pycache__", "cache", ".idea", ".vscode", "JarvisX_Client_Release"}
    EXCLUDE_EXTS = {".pyc", ".pyo", ".log", ".tmp", ".zip", ".pem", ".key"}
    EXCLUDE_FILES = {"build_client_package.py", "test_qt_screen.jpg", "test_voice.mp3"}

    # 1. Fast purge of __pycache__ and compiled bytecode outside excluded dirs
    pycache_count = 0
    pyc_count = 0
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith((".pyc", ".pyo", ".log")):
                full_path = os.path.join(root, f)
                try:
                    os.remove(full_path)
                    pyc_count += 1
                except Exception:
                    pass

    print(f"[CLEAN] Purged temporary compiled bytecode files.")

    if release_dir.exists():
        shutil.rmtree(release_dir)

    print(f"[BUILD] Copying clean source code to {release_dir.name}...")
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        rel_path = os.path.relpath(root, project_root)
        target_path = release_dir if rel_path == "." else release_dir / rel_path
        target_path.mkdir(parents=True, exist_ok=True)

        for file in files:
            if file in EXCLUDE_FILES or any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                continue
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_path, file)
            shutil.copy2(src_file, dst_file)

    # 2. Create ZIP package
    print(f"[ZIP] Creating release ZIP archive: {zip_filename.name}...")
    if zip_filename.exists():
        os.remove(zip_filename)

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, release_dir)
                zipf.write(full_path, arcname)

    # Cleanup temporary unzipped release folder
    shutil.rmtree(release_dir, ignore_errors=True)

    file_size_mb = zip_filename.stat().st_size / (1024 * 1024)
    print("========================================================")
    print(f"SUCCESS! Clean Release Package created:")
    print(f" -> Archive: {zip_filename} ({file_size_mb:.2f} MB)")
    print("========================================================")
    return str(zip_filename)

if __name__ == "__main__":
    clean_and_package()
