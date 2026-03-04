# 🔵 BlueLock — AI Password Manager

A local, AI-powered password manager for desktop.
No cloud, no external servers — everything encrypted on your machine.

---

## Project Structure

```
bluelock/
├── backend/              ← Python (FastAPI)
│   ├── main.py           ← Server + Hotkey Listener
│   ├── vault.py          ← Encrypted Database
│   ├── matcher.py        ← AI Screenshot Comparison
│   ├── notifier.py       ← System Notifications
│   └── requirements.txt
│
├── frontend/             ← Electron
│   ├── main.js           ← Tray, Window Management
│   ├── package.json
│   └── windows/
│       ├── widget.html   ← Floating Widget (always visible)
│       └── popup.html    ← Input Popup (F3)
│
└── bluelock.html         ← Main Vault UI (Tray click)
```

---

## Setup & Installation

### 1. Install Python Backend

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Electron Frontend

```bash
cd frontend
npm install
```

---

## Running

### Start Backend (Terminal 1):
```bash
cd backend
python main.py
```

### Start Electron App (Terminal 2):
```bash
cd frontend
npm start
```

---

## How to Use

| Action | What happens |
|--------|-------------|
| **Press F3** | Screenshot is taken + input popup appears |
| Enter username + password | Inside the BlueLock popup (no keylogger!) |
| Click **"Save"** | Everything is saved with AES-256 encryption |
| Widget shows | "✓ Saved!" |
| **Press F4** | AI scans screen, recognizes app, autofills credentials |
| Widget shows | "✓ Data successfully filled in!" |
| **Double-click tray icon** | Main vault UI opens |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Main UI | HTML/CSS (Glassmorphism) |
| Desktop App | Electron |
| Backend | Python + FastAPI |
| Encryption | AES-256 (Fernet) |
| Database | SQLite (local) |
| AI Matching | OpenCV (ORB + Histogram) |
| Autofill | PyAutoGUI |
| Tray | Electron Tray API |

---

## Privacy & Security

- ✅ Everything **local** — no cloud, no internet required
- ✅ Passwords encrypted with **AES-256**
- ✅ No keylogger — credentials entered in BlueLock's own window
- ✅ Screenshots stored locally only
- ✅ Vault key stored in `~/.bluelock/vault.key` (owner access only)
---

## Contributing

Everyone is welcome to contribute, test ideas, or suggest improvements.  
Join in and help make **BlueLock** even cooler! 🚀
