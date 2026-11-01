import os
import shutil
import zipfile
from pathlib import Path

def clean_and_package():
    """Purges all __pycache__, bytecode, temporary logs, and creates a clean client release ZIP."""
    project_root = Path(__file__).resolve().parent
    release_dir = project_root.parent / "JarvisX_Client_Release"
    zip_filename = project_root.parent / "JarvisX_Client_Release.zip"

    print("========================================================")
    print("      JarvisX Clean Client Release Packaging Tool       ")
    print("========================================================")

    # 1. Purge __pycache__ and bytecode in workspace
    pycache_count = 0
    pyc_count = 0
    for root, dirs, files in os.walk(project_root):
        for d in dirs:
            if d == "__pycache__":
                full_path = os.path.join(root, d)
                try:
                    shutil.rmtree(full_path)
                    pycache_count += 1
                except Exception as e:
                    print(f"Error removing {full_path}: {e}")
        for f in files:
            if f.endswith((".pyc", ".pyo", ".log")):
                full_path = os.path.join(root, f)
                try:
                    os.remove(full_path)
                    pyc_count += 1
                except Exception as e:
                    print(f"Error removing {full_path}: {e}")

    print(f"[CLEAN] Purged {pycache_count} __pycache__ folders and {pyc_count} compiled bytecode files.")

    # 2. Exclude patterns for distribution ZIP
    EXCLUDE_DIRS = {".git", ".venv", ".venv-1", "__pycache__", "cache", ".idea", ".vscode"}
    EXCLUDE_EXTS = {".pyc", ".pyo", ".log", ".tmp", ".zip"}
    EXCLUDE_FILES = {"build_client_package.py"}

    if release_dir.exists():
        shutil.rmtree(release_dir)

    print(f"[BUILD] Copying clean source code to {release_dir.name}...")
    for root, dirs, files in os.walk(project_root):
        # Modify dirs in-place to skip excluded directories
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

    # 3. Create ZIP package
    print(f"[ZIP] Creating release ZIP archive: {zip_filename.name}...")
    if zip_filename.exists():
        os.remove(zip_filename)

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, release_dir)
                zipf.write(full_path, arcname)

    print("========================================================")
    print(f"SUCCESS! Clean Release Package created at:")
    print(f" -> Archive: {zip_filename}")
    print("========================================================")

if __name__ == "__main__":
    clean_and_package()
