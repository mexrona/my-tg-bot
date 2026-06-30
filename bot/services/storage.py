import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class StoredMessage:
    id: int
    user_id: int
    username: str | None
    text: str
    created_at: str
    replied_at: str | None


@dataclass
class InboxStats:
    total: int
    replied: int
    unreplied: int


class Storage:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    replied_at TEXT
                );
                """
            )
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(messages)").fetchall()
            }
            if "replied_at" not in columns:
                conn.execute("ALTER TABLE messages ADD COLUMN replied_at TEXT")

    def _row_to_message(self, row: sqlite3.Row) -> StoredMessage:
        return StoredMessage(
            id=row["id"],
            user_id=row["user_id"],
            username=row["username"],
            text=row["text"],
            created_at=row["created_at"],
            replied_at=row["replied_at"],
        )

    def get_setting(self, key: str, default: str = "") -> str:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?",
                (key,),
            ).fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )

    def save_message(
        self,
        user_id: int,
        username: str | None,
        text: str,
        created_at: datetime | None = None,
    ) -> int:
        moment = (created_at or datetime.now()).isoformat(timespec="seconds")
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO messages (user_id, username, text, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, username, text, moment),
            )
            return int(cursor.lastrowid)

    def get_message(self, message_id: int) -> StoredMessage | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM messages WHERE id = ?",
                (message_id,),
            ).fetchone()
            if not row:
                return None
            return self._row_to_message(row)

    def mark_replied(self, message_id: int, replied_at: datetime | None = None) -> bool:
        moment = (replied_at or datetime.now()).isoformat(timespec="seconds")
        with self._connect() as conn:
            cursor = conn.execute(
                """
                UPDATE messages
                SET replied_at = ?
                WHERE id = ? AND replied_at IS NULL
                """,
                (moment, message_id),
            )
            return cursor.rowcount > 0

    def get_stats(self) -> InboxStats:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(replied_at) AS replied,
                    COUNT(*) - COUNT(replied_at) AS unreplied
                FROM messages
                """
            ).fetchone()
            return InboxStats(
                total=row["total"],
                replied=row["replied"],
                unreplied=row["unreplied"],
            )

    def get_all_unreplied(self) -> list[StoredMessage]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM messages
                WHERE replied_at IS NULL
                ORDER BY id ASC
                """
            ).fetchall()
            return [self._row_to_message(row) for row in rows]

    def get_unreplied(self, limit: int = 10, offset: int = 0) -> list[StoredMessage]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM messages
                WHERE replied_at IS NULL
                ORDER BY id DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()
            return [self._row_to_message(row) for row in rows]

    def clear_messages(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS total FROM messages").fetchone()
            deleted = row["total"]
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM sqlite_sequence WHERE name = 'messages'")
            return deleted

    def delete_message(self, message_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM messages WHERE id = ?",
                (message_id,),
            )
            return cursor.rowcount > 0
