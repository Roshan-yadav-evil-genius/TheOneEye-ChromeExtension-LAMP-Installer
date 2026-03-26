#!/usr/bin/env python3
"""
server.py — Hosts install.sh and install.ps1 on port 8090
Run: python3 server.py

Users then run:
  Linux/macOS : curl -sSL http://YOUR_IP:8090/install.sh | bash
  Windows     : irm http://YOUR_IP:8090/install.ps1 | iex
"""

import http.server
import socketserver
import os
import socket
import sys
from urllib.parse import urlparse

PORT = 8090
SERVE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML = "index.html"
INDEX_PLACEHOLDER = "__HOST__"

# MIME types for our scripts
MIME_TYPES = {
    ".sh":   "text/plain; charset=utf-8",
    ".ps1":  "text/plain; charset=utf-8",
    ".bat":  "text/plain; charset=utf-8",
    ".txt":  "text/plain; charset=utf-8",
    ".html": "text/html; charset=utf-8",
}

class InstallHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SERVE_DIR, **kwargs)

    def guess_type(self, path):
        ext = os.path.splitext(path)[1].lower()
        return MIME_TYPES.get(ext, "text/plain; charset=utf-8")

    def log_message(self, format, *args):
        client = self.client_address[0]
        print(f"  [{client}] {format % args}")

    def do_GET(self):
        path = urlparse(self.path).path or "/"
        if path in ("/", "/index.html"):
            index_path = os.path.join(SERVE_DIR, INDEX_HTML)
            if not os.path.isfile(index_path):
                self.send_error(500, f"{INDEX_HTML} missing")
                return
            host = self.headers.get("Host", f"YOUR_IP:{PORT}")
            with open(index_path, encoding="utf-8") as f:
                body = f.read().replace(INDEX_PLACEHOLDER, host)
            data = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        super().do_GET()


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
    os.chdir(SERVE_DIR)

    # Check that scripts exist
    for f in ["install.sh", "install.ps1", INDEX_HTML]:
        path = os.path.join(SERVE_DIR, f)
        if not os.path.exists(path):
            print(f"[WARN] {f} not found in {SERVE_DIR}")

    ip = get_local_ip()

    with socketserver.TCPServer(("", PORT), InstallHandler) as httpd:
        httpd.allow_reuse_address = True
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
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[✓] Server stopped.")
            sys.exit(0)


if __name__ == "__main__":
    main()
