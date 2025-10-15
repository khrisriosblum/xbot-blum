
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os
from .settings import settings

DDL = """
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    sheet TEXT,
    col TEXT,
    row INTEGER,
    title TEXT,
    posted_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_posts_url ON posts(url);
CREATE INDEX IF NOT EXISTS idx_posts_posted_at ON posts(posted_at);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TEXT,           -- YYYY-MM-DD
    slot_label TEXT,         -- 12:00 / 15:00 / etc.
    scheduled_at TEXT,       -- ISO datetime when planned
    executed_at TEXT,        -- ISO datetime when executed
    status TEXT,             -- planned|success|skipped|error
    selected_url TEXT,
    error TEXT
);
"""

class Storage:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.executescript(DDL)
        self.conn.commit()

    def record_post(self, url: str, sheet: str, col: str, row: int, title: str = ""):
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO posts(url, sheet, col, row, title, posted_at) VALUES (?,?,?,?,?,?)",
                    (url, sheet, col, row, title, datetime.utcnow().isoformat()))
        self.conn.commit()

    def was_posted_within_days(self, url: str, days: int) -> bool:
        cur = self.conn.cursor()
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        cur.execute("SELECT 1 FROM posts WHERE url=? AND posted_at>=? LIMIT 1", (url, cutoff))
        return cur.fetchone() is not None

    def add_run(self, run_date: str, slot_label: str, scheduled_at: str, status: str = "planned", selected_url: str = None, error: str = None):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO runs(run_date, slot_label, scheduled_at, status, selected_url, error) VALUES (?,?,?,?,?,?)",
                    (run_date, slot_label, scheduled_at, status, selected_url, error))
        self.conn.commit()
        return cur.lastrowid

    def update_run(self, run_id: int, **kwargs):
        keys = ", ".join([f"{k}=?" for k in kwargs.keys()])
        params = list(kwargs.values())
        params.append(run_id)
        cur = self.conn.cursor()
        cur.execute(f"UPDATE runs SET {keys} WHERE id=?", params)
        self.conn.commit()

    def list_recent_posts(self, limit: int = 50):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM posts ORDER BY posted_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]

    def list_runs(self, limit: int = 50):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]


storage = Storage(settings.DB_PATH)
