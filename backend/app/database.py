import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.config import settings

def get_db_path() -> Path:
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        path_str = db_url.replace("sqlite:///", "")
        return Path(path_str).resolve()
    return Path("geospatial.db").resolve()

def get_db_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

_db_initialized = False

def ensure_db():
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True

def init_db():
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_records (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    feature_count INTEGER DEFAULT 0,
                    crs TEXT,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    created_at TEXT NOT NULL
                )
            """)
    finally:
        conn.close()

init_db()

def create_file_record(
    file_id: str,
    filename: str,
    file_type: str,
    file_path: str,
    status: str = "PROCESSING",
    crs: Optional[str] = None,
    feature_count: int = 0,
    error_message: Optional[str] = None
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
                INSERT INTO file_records (
                    id, filename, file_type, file_path, feature_count, crs, status, error_message, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (file_id, filename, file_type, file_path, feature_count, crs, status, error_message, now))
        return get_file_record(file_id)
    finally:
        conn.close()

def update_file_record(
    file_id: str,
    status: str,
    feature_count: int = 0,
    crs: Optional[str] = None,
    error_message: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
                UPDATE file_records
                SET status = ?, feature_count = ?, crs = ?, error_message = ?
                WHERE id = ?
            """, (status, feature_count, crs, error_message, file_id))
        return get_file_record(file_id)
    finally:
        conn.close()

def get_file_record(file_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM file_records WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()

def list_file_records() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM file_records ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
