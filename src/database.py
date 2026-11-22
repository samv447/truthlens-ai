"""Local SQLite prediction history; no full article text is stored."""
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / 'data' / 'history.sqlite3'

def connect(path=DB_PATH):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute('CREATE TABLE IF NOT EXISTS predictions (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, preview TEXT NOT NULL, label TEXT NOT NULL CHECK(label IN (\'FAKE\',\'REAL\')), score REAL NOT NULL CHECK(score >= 0 AND score <= 1))')
    connection.commit()
    return connection

def add_prediction(preview, label, score, path=DB_PATH):
    if label not in ('FAKE', 'REAL') or not 0 <= float(score) <= 1:
        raise ValueError('Invalid prediction record.')
    with connect(path) as db:
        db.execute('INSERT INTO predictions(created_at, preview, label, score) VALUES (?, ?, ?, ?)', (datetime.now(timezone.utc).isoformat(timespec='seconds'), str(preview)[:180], label, float(score)))

def get_history(path=DB_PATH, limit=1000):
    with connect(path) as db:
        return [dict(row) for row in db.execute('SELECT id, created_at, preview, label, score FROM predictions ORDER BY id DESC LIMIT ?', (max(1, min(int(limit), 10000)),)).fetchall()]

def delete_prediction(record_id, path=DB_PATH):
    with connect(path) as db:
        db.execute('DELETE FROM predictions WHERE id=?', (int(record_id),))

def clear_history(path=DB_PATH):
    with connect(path) as db:
        db.execute('DELETE FROM predictions')
