"""
BlueLock - Vault
Handles all encrypted storage using SQLite + AES-256
"""

import sqlite3
import os
import base64
import json
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


VAULT_PATH = os.path.join(os.path.expanduser("~"), ".bluelock", "vault.db")
KEY_PATH = os.path.join(os.path.expanduser("~"), ".bluelock", "vault.key")


class Vault:
    def __init__(self):
        os.makedirs(os.path.dirname(VAULT_PATH), exist_ok=True)
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)
        self._init_db()

    # ─── Key Management ────────────────────────────────────────────────────────

    def _load_or_create_key(self) -> bytes:
        """Load existing key or generate a new one"""
        if os.path.exists(KEY_PATH):
            with open(KEY_PATH, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_PATH, "wb") as f:
                f.write(key)
            # Restrict file permissions (owner only)
            os.chmod(KEY_PATH, 0o600)
            return key

    # ─── DB Setup ──────────────────────────────────────────────────────────────

    def _init_db(self):
        """Create database tables if they don't exist"""
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    username_enc TEXT NOT NULL,
                    password_enc TEXT NOT NULL,
                    screenshot_b64 TEXT,
                    created_at TEXT NOT NULL,
                    last_used TEXT,
                    use_count INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY,
                    total_autofills INTEGER DEFAULT 0,
                    last_autofill TEXT
                )
            """)
            # Insert default stats row
            conn.execute("INSERT OR IGNORE INTO stats (id, total_autofills) VALUES (1, 0)")

    def _get_conn(self):
        return sqlite3.connect(VAULT_PATH)

    # ─── Encryption ────────────────────────────────────────────────────────────

    def _encrypt(self, text: str) -> str:
        return self.fernet.encrypt(text.encode()).decode()

    def _decrypt(self, text: str) -> str:
        return self.fernet.decrypt(text.encode()).decode()

    # ─── CRUD ──────────────────────────────────────────────────────────────────

    def save(self, app_name: str, username: str, password: str, screenshot_b64: str):
        """Save a new credential entry"""
        username_enc = self._encrypt(username)
        password_enc = self._encrypt(password)
        now = datetime.now().isoformat()

        with self._get_conn() as conn:
            # Check if entry for this app already exists → update it
            existing = conn.execute(
                "SELECT id FROM entries WHERE app_name = ?", (app_name,)
            ).fetchone()

            if existing:
                conn.execute("""
                    UPDATE entries 
                    SET username_enc=?, password_enc=?, screenshot_b64=?, created_at=?
                    WHERE app_name=?
                """, (username_enc, password_enc, screenshot_b64, now, app_name))
            else:
                conn.execute("""
                    INSERT INTO entries (app_name, username_enc, password_enc, screenshot_b64, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (app_name, username_enc, password_enc, screenshot_b64, now))

    def get_all(self) -> list:
        """Get all entries (decrypted, without screenshots)"""
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT id, app_name, username_enc, password_enc, created_at, last_used, use_count
                FROM entries ORDER BY use_count DESC
            """).fetchall()

        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "app_name": row[1],
                "username": self._decrypt(row[2]),
                "password": self._decrypt(row[3]),
                "created_at": row[4],
                "last_used": row[5],
                "use_count": row[6]
            })
        return result

    def get_all_with_screenshots(self) -> list:
        """Get all entries including screenshots (for AI matching)"""
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT id, app_name, username_enc, password_enc, screenshot_b64
                FROM entries
            """).fetchall()

        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "app_name": row[1],
                "username": self._decrypt(row[2]),
                "password": self._decrypt(row[3]),
                "screenshot_b64": row[4]
            })
        return result

    def update_last_used(self, entry_id: int):
        """Update last used timestamp and increment use count"""
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE entries SET last_used=?, use_count=use_count+1 WHERE id=?
            """, (now, entry_id))
            conn.execute("""
                UPDATE stats SET total_autofills=total_autofills+1, last_autofill=? WHERE id=1
            """, (now,))

    def delete(self, entry_id: int):
        """Delete an entry"""
        with self._get_conn() as conn:
            conn.execute("DELETE FROM entries WHERE id=?", (entry_id,))

    def get_stats(self) -> dict:
        """Get vault statistics"""
        with self._get_conn() as conn:
            total_entries = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
            stats = conn.execute("SELECT total_autofills, last_autofill FROM stats WHERE id=1").fetchone()

        return {
            "total_entries": total_entries,
            "total_autofills": stats[0] if stats else 0,
            "last_autofill": stats[1] if stats else None
        }
