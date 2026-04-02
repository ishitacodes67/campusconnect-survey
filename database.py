"""
Database layer — SQLite with WAL mode for reliable concurrent reads.
"""

import sqlite3
from config import settings


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row           # dict-like rows
    conn.execute("PRAGMA journal_mode=WAL")  # safe concurrent access
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db():
    """Create tables and indexes if they don't already exist."""
    conn = get_db_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                submitted_at     TEXT    NOT NULL,
                role             TEXT    NOT NULL,
                year             TEXT    NOT NULL,
                dept             TEXT    NOT NULL,
                discover         TEXT    NOT NULL,
                missed           TEXT    NOT NULL,
                comm_score       INTEGER NOT NULL,
                interests        TEXT    NOT NULL,
                ai_reco          TEXT    NOT NULL,
                notif            TEXT    NOT NULL,
                notif_freq       TEXT    NOT NULL,
                features         TEXT    NOT NULL,
                privacy          TEXT    NOT NULL,
                likely_score     INTEGER NOT NULL,
                biggest_problem  TEXT    NOT NULL,
                wishlist         TEXT    DEFAULT '',
                other            TEXT    DEFAULT ''
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_dept ON responses(dept)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_role ON responses(role)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON responses(submitted_at)")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Database initialisation failed: {e}") from e
    finally:
        conn.close()
