"""
Master Production API Key & Secret Manager for Shriva AI // JarvisX.
Automatically loads keys from local .env file, active shell, and system environment.
"""

from __future__ import annotations
import os
from pathlib import Path


def _load_local_env() -> None:
    """Finds and securely loads .env from project root or execution directory."""
    candidates = [
        Path(__file__).resolve().parent / ".env",
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent / ".env"
    ]
    for env_path in candidates:
        if env_path.exists():
            try:
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value:
                        os.environ[key] = value
                break
            except Exception as e:
                print(f"[API_KEYS WARNING] Error reading .env: {e}")


_load_local_env()

# Primary Production Keys loaded directly from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")
WOLFRAM_ALPHA_APP_ID = os.getenv("WOLFRAM_ALPHA_APP_ID", "") or os.getenv("WOLFRAM_APP_ID", "")
WOLFRAM_APP_ID = WOLFRAM_ALPHA_APP_ID

# Propagate all active keys into os.environ for seamless multi-module availability
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
if POLLINATIONS_API_KEY:
    os.environ["POLLINATIONS_API_KEY"] = POLLINATIONS_API_KEY
if WOLFRAM_ALPHA_APP_ID:
    os.environ["WOLFRAM_ALPHA_APP_ID"] = WOLFRAM_ALPHA_APP_ID
    os.environ["WOLFRAM_APP_ID"] = WOLFRAM_ALPHA_APP_ID
