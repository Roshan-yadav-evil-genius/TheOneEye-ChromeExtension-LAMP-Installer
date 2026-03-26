# git_sync — Hosted One-Liner Installer

Host this folder and users can install with a single command.

---

## 1. Setup — Edit your repo URL

**`install.sh`** (Linux/macOS) — change line 11:
```bash
REPO_URL="${1:-https://github.com/YOUR_USERNAME/YOUR_REPO.git}"
```

**`install.ps1`** (Windows) — change line 10:
```powershell
$REPO_URL = if ($env:REPO_URL) { $env:REPO_URL } else { "https://github.com/YOUR_USERNAME/YOUR_REPO.git" }
```

---

## 2. Start the server

```bash
python3 server.py
```

The server auto-detects your local IP and prints the install commands.

---

## 3. Share with users

**Linux / macOS:**
```bash
curl -sSL http://YOUR_IP:8090/install.sh | bash
```

**Windows** (PowerShell as Administrator):
```powershell
irm http://YOUR_IP:8090/install.ps1 | iex
```

**With a custom repo URL:**
```bash
# Linux/macOS
curl -sSL http://YOUR_IP:8090/install.sh | bash -s -- https://github.com/user/repo.git

# Windows
$env:REPO_URL="https://github.com/user/repo.git"; irm http://YOUR_IP:8090/install.ps1 | iex
```

---

## 4. What happens after install

| Situation | Action |
|-----------|--------|
| Repo not on Desktop | `git clone` it |
| Repo already on Desktop | `git pull` it |
| Runs every | 1 hour |
| Logs | `~/.git_sync.log` |
| Scheduler | `cron` (Linux/macOS) / Task Scheduler (Windows) |

---

## Files

| File | Purpose |
|------|---------|
| `server.py` | Python HTTP server (port 8090) |
| `install.sh` | Linux/macOS self-contained installer |
| `install.ps1` | Windows self-contained installer (PowerShell) |

---

## Uninstall

**Linux/macOS:**
```bash
crontab -l | grep -v '# git_sync_hourly' | crontab -
rm -rf ~/.git_sync
```

**Windows (PowerShell):**
```powershell
Unregister-ScheduledTask -TaskName "GitSyncHourly" -Confirm:$false
Remove-Item -Recurse -Force "$env:USERPROFILE\.git_sync"
```

---

## Run server on startup (optional)

**Linux (systemd):**
```bash
# Create /etc/systemd/system/git-sync-server.service
[Unit]
Description=git_sync install server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/server.py
Restart=always
User=youruser

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable --now git-sync-server
```

**macOS (launchd)** / **Windows (NSSM)** — run `python3 server.py` in a persistent terminal or service manager.
