# REMATES — Stack & Interface Recommendations

## Overview

A lightweight, fully offline web interface for the REMATES scraper, accessible from PC and Android, with simple backup built in. No new languages required — everything runs in pure Python.

---

## Recommended Stack

### 1. SQLite — local database

- Single `.db` file, zero server setup required
- Built into Python's standard library — no `pip install` needed
- Handles full CRUD at this scale with no performance issues
- The file itself is the backup: copy it anywhere, open with [DB Browser for SQLite](https://sqlitebrowser.org/), or export to CSV with one SQL command

### 2. Flask — web server

- ~100 lines of Python to serve a full web UI
- Accessible from any device on your local network, including Android via WiFi IP (e.g. `http://192.168.1.x:5000`)
- No app to install, no Play Store — works in Chrome on Android out of the box
- Responsive HTML makes it usable on both desktop and mobile screen sizes

### 3. Browser-based UI (PC + Android)

- No native app needed — any browser works
- Responsive layout adapts automatically between desktop table view and mobile card view

---

## Interface Features

| Feature | Description |
|---|---|
| Searchable table | Filter by keyword across all fields |
| Source filter | Show only IMPO, ANRTCI, or Intendencia results |
| Inline edit | Edit description or notes directly in the table |
| Delete | Remove individual entries |
| Annotation field | Add personal notes per remate (e.g. "llamar lunes") |
| "Visto" toggle | Mark entries as seen/reviewed |
| CSV export | `/export` endpoint downloads current filtered view |

---

## Database Schema (suggested)

```sql
CREATE TABLE remates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fuente      TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    link        TEXT,
    notas       TEXT,
    visto       INTEGER DEFAULT 0,
    fecha_scrape TEXT DEFAULT (date('now'))
);
```

---

## Backup Strategy

Two complementary layers:

1. **File-level backup** — the `.db` file can be copied to a USB drive or cloud sync folder with a one-liner cron job:
   ```bash
   cp remates.db ~/Dropbox/backups/remates_$(date +%F).db
   ```

2. **CSV export endpoint** — a `/export` route in Flask lets you download a fresh CSV from any device (including Android) at any time. Opens natively in Excel or Google Sheets.

---

## How the Pieces Connect

```
scraper.py  →  SQLite (.db file)  →  Flask (local server)  →  Browser (PC / Android)
                     ↓
              .db file copy  +  /export CSV endpoint  →  Backup
```

---

## Setup Summary

```bash
pip install flask
python app.py        # starts server at http://localhost:5000
```

On Android: open Chrome and navigate to `http://<your-PC-local-IP>:5000` while on the same WiFi network.

---

## Notes

- Everything runs entirely offline — no cloud dependency
- The scraper writes directly to SQLite; the Flask app reads and displays from the same file
- Existing `scraper.py` needs only one change: replace `save_to_csv()` with a `save_to_db()` function using Python's built-in `sqlite3` module
- To find your local IP on Windows: `ipconfig` → IPv4 Address. On Linux/Mac: `ip a` or `ifconfig`
