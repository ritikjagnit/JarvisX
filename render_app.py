"""Render-compatible web entrypoint for JarvisX.

The full JarvisX assistant is a Windows desktop app. Render runs Linux web
services, so this module exposes a lightweight HTTP status page without
starting PyQt, voice capture, text-to-speech, or OS automation.
"""

from __future__ import annotations

import json
import os
import platform
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parent
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "10000"))


def _json_response(payload: dict[str, Any], status: str = "ready") -> bytes:
    body = {"status": status, **payload}
    return json.dumps(body, indent=2).encode("utf-8")


def _html_response() -> bytes:
    has_openai_key = bool(os.getenv("OPENAI_API_KEY"))
    desktop_files = [
        "main.py",
        "ui/dashboard.py",
        "command_router.py",
        "voice_engine.py",
    ]
    missing_files = [name for name in desktop_files if not (PROJECT_ROOT / name).exists()]
    readiness = "ready" if not missing_files else "partial"

    key_state = "configured" if has_openai_key else "not configured"
    missing_text = ", ".join(missing_files) if missing_files else "none"

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JarvisX</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #080b0f;
      --panel: #111820;
      --text: #ecf4ff;
      --muted: #a9b7c5;
      --accent: #38d7c5;
      --line: #273340;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top left, #122833 0, var(--bg) 42%);
      color: var(--text);
      display: grid;
      place-items: center;
      padding: 32px 18px;
    }}
    main {{
      width: min(860px, 100%);
      border: 1px solid var(--line);
      background: color-mix(in srgb, var(--panel) 86%, transparent);
      border-radius: 8px;
      padding: clamp(24px, 5vw, 46px);
      box-shadow: 0 18px 70px rgba(0, 0, 0, 0.35);
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: clamp(36px, 7vw, 72px);
      line-height: 0.95;
      letter-spacing: 0;
    }}
    p {{
      margin: 0;
      color: var(--muted);
      font-size: 18px;
      line-height: 1.6;
      max-width: 64ch;
    }}
    dl {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin: 34px 0 0;
    }}
    div {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      background: rgba(255, 255, 255, 0.03);
      min-height: 96px;
    }}
    dt {{
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}
    dd {{
      margin: 0;
      font-size: 18px;
      overflow-wrap: anywhere;
    }}
    a {{ color: var(--accent); }}
  </style>
</head>
<body>
  <main>
    <h1>JarvisX</h1>
    <p>
      Render web service is online. The complete JarvisX assistant is a local
      Windows desktop experience, so voice, PyQt UI, and system automation stay
      disabled on this public server.
    </p>
    <dl>
      <div>
        <dt>Service</dt>
        <dd>{readiness}</dd>
      </div>
      <div>
        <dt>OpenAI Key</dt>
        <dd>{key_state}</dd>
      </div>
      <div>
        <dt>Python</dt>
        <dd>{platform.python_version()}</dd>
      </div>
      <div>
        <dt>Missing Files</dt>
        <dd>{missing_text}</dd>
      </div>
    </dl>
  </main>
</body>
</html>"""
    return html.encode("utf-8")


class RenderHandler(BaseHTTPRequestHandler):
    server_version = "JarvisXRender/1.0"

    def do_GET(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"

        if path == "/":
            self._send(_html_response(), "text/html; charset=utf-8")
            return

        if path == "/healthz":
            self._send(_json_response({"ok": True}), "application/json")
            return

        if path == "/api/status":
            payload = {
                "app": "JarvisX",
                "runtime": "render-web",
                "desktop_features": "disabled",
                "openai_key_configured": bool(os.getenv("OPENAI_API_KEY")),
                "python": platform.python_version(),
                "render": bool(os.getenv("RENDER")),
            }
            self._send(_json_response(payload), "application/json")
            return

        self._send(
            _json_response({"error": "Not found"}, status="error"),
            "application/json",
            HTTPStatus.NOT_FOUND,
        )

    def do_POST(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/api/chat":
            payload = {
                "message": (
                    "JarvisX command execution is disabled on Render. Run "
                    "`python main.py` locally for the desktop assistant."
                )
            }
            self._send(_json_response(payload, status="disabled"), "application/json", HTTPStatus.ACCEPTED)
            return

        self._send(
            _json_response({"error": "Not found"}, status="error"),
            "application/json",
            HTTPStatus.NOT_FOUND,
        )

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format % args}")

    def _send(
        self,
        body: bytes,
        content_type: str,
        status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), RenderHandler)
    print(f"JarvisX Render service listening on {HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
