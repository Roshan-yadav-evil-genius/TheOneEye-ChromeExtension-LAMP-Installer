# git_sync — Hosted One-Liner Installer

Host this folder and users can install with a single command.

---

## 1. Setup — Edit your repo URL (and optional default branch)

**`install.sh`** (Linux/macOS) — defaults for repo URL and branch (`main`):
```bash
REPO_URL="${1:-https://github.com/Roshan-yadav-evil-genius/TheOneEye-ChromeExtension-LAMP-build.git}"
SYNC_BRANCH="${2:-main}"
```

**`install.ps1`** (Windows):
```powershell
$REPO_URL    = if ($env:REPO_URL) { $env:REPO_URL } else { "https://github.com/Roshan-yadav-evil-genius/TheOneEye-ChromeExtension-LAMP-build.git" }
$SYNC_BRANCH = if ($env:SYNC_BRANCH) { $env:SYNC_BRANCH } else { "main" }
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

**With a custom repo URL (and optional branch):**
```bash
# Linux/macOS — default branch main
curl -sSL http://YOUR_IP:8090/install.sh | bash -s -- https://github.com/user/repo.git

# Linux/macOS — sync `master` instead of `main`
curl -sSL http://YOUR_IP:8090/install.sh | bash -s -- https://github.com/user/repo.git master

# Windows
$env:REPO_URL="https://github.com/user/repo.git"; irm http://YOUR_IP:8090/install.ps1 | iex

# Windows — non-default branch
$env:REPO_URL="https://github.com/user/repo.git"; $env:SYNC_BRANCH="master"; irm http://YOUR_IP:8090/install.ps1 | iex
```

---

## 4. What happens after install

| Situation | Action |
|-----------|--------|
| Repo not on Desktop | `git clone` it |
| Repo already on Desktop | `git fetch origin`, then `git checkout <branch>`, then `git reset --hard origin/<branch>` (discards local commits and uncommitted changes on that clone) |
| Default branch | `main` (override: 2nd arg to `install.sh`, or `$env:SYNC_BRANCH` on Windows) |
| Runs every | 1 hour |
| Logs | `~/.git_sync.log` (Windows: `%USERPROFILE%\.git_sync.log`) |
| Scheduler | `cron` (Linux/macOS) / Task Scheduler (Windows) |

To pick up script changes after you edit the installers, **re-run the install command** so `~/.git_sync/git_sync.sh` (or `git_sync.ps1`) is regenerated.

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
