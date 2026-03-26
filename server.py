#!/usr/bin/env python3
"""
server.py — FastAPI server for install scripts on port 8090
Run: python3 server.py

Users then run:
  Linux/macOS : curl -sSL http://YOUR_IP:8090/install.sh | bash
  Windows     : irm http://YOUR_IP:8090/install.ps1 | iex
"""

import os
import socket
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

PORT = 8090
SERVE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML = "index.html"
INDEX_PLACEHOLDER = "__HOST__"
INDEX_PATH = Path(SERVE_DIR) / INDEX_HTML
INSTALL_SH_PATH = Path(SERVE_DIR) / "install.sh"
INSTALL_PS1_PATH = Path(SERVE_DIR) / "install.ps1"

app = FastAPI(title="git_sync Install Server")


def resolve_host(request: Request, fallback_ip: str) -> str:
    return request.headers.get("host") or f"{fallback_ip}:{PORT}"


def render_index(host: str) -> str:
    if not INDEX_PATH.is_file():
        raise HTTPException(status_code=500, detail=f"{INDEX_HTML} missing")
    return INDEX_PATH.read_text(encoding="utf-8").replace(INDEX_PLACEHOLDER, host)


@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def serve_index(request: Request) -> HTMLResponse:
    host = resolve_host(request, get_local_ip())
    body = render_index(host)
    return HTMLResponse(content=body)


@app.get("/install.sh")
def serve_install_sh() -> FileResponse:
    if not INSTALL_SH_PATH.is_file():
        raise HTTPException(status_code=404, detail="install.sh missing")
    return FileResponse(INSTALL_SH_PATH, media_type="text/plain; charset=utf-8")


@app.get("/install.ps1")
def serve_install_ps1() -> FileResponse:
    if not INSTALL_PS1_PATH.is_file():
        raise HTTPException(status_code=404, detail="install.ps1 missing")
    return FileResponse(INSTALL_PS1_PATH, media_type="text/plain; charset=utf-8")


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    ip = get_local_ip()

    for f in ["install.sh", "install.ps1", INDEX_HTML]:
        path = os.path.join(SERVE_DIR, f)
        if not os.path.exists(path):
            print(f"[WARN] {f} not found in {SERVE_DIR}")

    print()
    print("=" * 52)
    print("  git_sync Install Server — Running")
    print("=" * 52)
    print(f"  Serving from : {SERVE_DIR}")
    print(f"  Listening on : 0.0.0.0:{PORT}")
    print()
    print("  Linux / macOS:")
    print(f"    curl -sSL http://{ip}:{PORT}/install.sh | bash")
    print()
    print("  Windows (PowerShell as Admin):")
    print(f"    irm http://{ip}:{PORT}/install.ps1 | iex")
    print()
    print("  Browser:")
    print(f"    http://{ip}:{PORT}/")
    print("=" * 52)
    print("  Press Ctrl+C to stop")
    print()

    try:
        uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
    except KeyboardInterrupt:
        print("\n[✓] Server stopped.")
        sys.exit(0)


app.mount("/", StaticFiles(directory=SERVE_DIR, html=False), name="static")


if __name__ == "__main__":
    main()
