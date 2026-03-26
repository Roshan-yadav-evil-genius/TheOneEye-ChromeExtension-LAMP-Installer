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

PORT = 8090
SERVE_DIR = os.path.dirname(os.path.abspath(__file__))

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
        # Root path → show usage instructions
        if self.path == "/" or self.path == "":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            host = self.headers.get("Host", f"YOUR_IP:{PORT}")
            html = f"""<!DOCTYPE html>
<html>
<head><title>git_sync Installer</title>
<style>
  body {{ font-family: monospace; background:#1e1e1e; color:#d4d4d4; padding:40px; }}
  h1 {{ color:#4ec9b0; }} h2 {{ color:#9cdcfe; margin-top:30px; }}
  pre {{ background:#2d2d2d; padding:16px; border-radius:6px; border-left:3px solid #4ec9b0; overflow-x:auto; }}
  .os {{ color:#ce9178; font-weight:bold; }}
  code {{ color:#ce9178; }}
</style>
</head>
<body>
<h1>🔄 git_sync Installer</h1>
<p>Auto clone or pull a git repo to your Desktop every hour.</p>

<h2><span class="os">Linux / macOS</span></h2>
<pre>curl -sSL http://{host}/install.sh | bash</pre>

<h2><span class="os">Windows</span> (PowerShell as Administrator)</h2>
<pre>irm http://{host}/install.ps1 | iex</pre>

<h2>With a custom repo URL</h2>
<p><b>Linux/macOS:</b></p>
<pre>curl -sSL http://{host}/install.sh | bash -s -- https://github.com/user/repo.git</pre>
<p><b>Windows:</b></p>
<pre>$env:REPO_URL="https://github.com/user/repo.git"; irm http://{host}/install.ps1 | iex</pre>

<h2>Files</h2>
<pre><a href="/install.sh"  style="color:#4ec9b0">install.sh</a>   — Linux / macOS installer
<a href="/install.ps1" style="color:#4ec9b0">install.ps1</a>  — Windows installer (PowerShell)</pre>
</body></html>"""
            self.wfile.write(html.encode())
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
    for f in ["install.sh", "install.ps1"]:
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
