
from __future__ import annotations

import os
import sqlite3
import threading
from datetime import datetime
from typing import Any

try:
    import psycopg2  # type: ignore
    import psycopg2.extras  # type: ignore
except Exception:  # pragma: no cover - fallback if psycopg2 is unavailable
    psycopg2 = None  # type: ignore

_CONN = None
_BACKEND = None
_LOCK = threading.Lock()


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _use_postgres() -> bool:
    return bool(psycopg2) and bool(os.getenv("DB_HOST"))


def _sqlite_path() -> str:
    return os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "chat.db"))


def get_conn():
    global _CONN, _BACKEND

    if _CONN is not None:
        if _BACKEND == "postgres":
            if getattr(_CONN, "closed", 1) == 0:
                return _CONN
        else:
            return _CONN

    if _use_postgres():
        _CONN = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "chatdb"),
            user=os.getenv("DB_USER", "chatuser"),
            password=os.getenv("DB_PASS", "chatpass"),
        )
        _CONN.autocommit = True
        _BACKEND = "postgres"
        return _CONN

    _CONN = sqlite3.connect(_sqlite_path(), check_same_thread=False)
    _CONN.row_factory = sqlite3.Row
    _BACKEND = "sqlite"
    return _CONN


def _placeholder_sql(sql: str) -> str:
    if _BACKEND == "sqlite":
        return sql.replace("%s", "?")
    return sql


def _execute(sql: str, params: tuple[Any, ...] = (), fetchone: bool = False, fetchall: bool = False):
    conn = get_conn()
    with _LOCK:
        cur = conn.cursor()
        try:
            cur.execute(_placeholder_sql(sql), params)
            if fetchone:
                return cur.fetchone()
            if fetchall:
                return cur.fetchall()
            return None
        finally:
            cur.close()


def init_db():
    get_conn()

    if _BACKEND == "postgres":
        _execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                last_ip TEXT,
                last_seen TEXT
            )
            """
        )

        _execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id BIGSERIAL PRIMARY KEY,
                msg_id INTEGER UNIQUE NOT NULL,
                msg_type TEXT NOT NULL,
                channel TEXT,
                sender_username TEXT,
                receiver_username TEXT,
                content TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        _execute(
            """
            CREATE TABLE IF NOT EXISTS attachments (
                id BIGSERIAL PRIMARY KEY,
                message_id INTEGER REFERENCES messages(msg_id) ON DELETE CASCADE,
                mime_type TEXT,
                data BYTEA
            )
            """
        )
    else:
        _execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                last_ip TEXT,
                last_seen TEXT
            )
            """
        )

        _execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                msg_id INTEGER UNIQUE NOT NULL,
                msg_type TEXT NOT NULL,
                channel TEXT,
                sender_username TEXT,
                receiver_username TEXT,
                content TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        _execute(
            """
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                mime_type TEXT,
                data BLOB,
                FOREIGN KEY(message_id) REFERENCES messages(msg_id) ON DELETE CASCADE
            )
            """
        )


def get_max_msg_id() -> int:
    row = _execute("SELECT MAX(msg_id) FROM messages", fetchone=True)
    if not row:
        return 0
    value = row[0] if not isinstance(row, dict) else list(row.values())[0]
    return int(value or 0)


def upsert_user(username: str, last_ip: str | None = None, last_seen: str | None = None):
    last_seen = last_seen or _now_text()
    _execute(
        """
        INSERT INTO users (username, last_ip, last_seen)
        VALUES (%s, %s, %s)
        ON CONFLICT(username)
        DO UPDATE SET last_ip = excluded.last_ip,
                      last_seen = excluded.last_seen
        """,
        (username, last_ip, last_seen),
    )


def insert_message(
    msg_id: int,
    msg_type: str,
    channel: str | None,
    sender: str | None,
    receiver: str | None,
    content: str,
    timestamp: str | None = None,
):
    timestamp = timestamp or _now_text()
    _execute(
        """
        INSERT INTO messages
            (msg_id, msg_type, channel, sender_username, receiver_username, content, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (msg_id, msg_type, channel, sender, receiver, content, timestamp),
    )
    return msg_id


def update_message_content(msg_id: int, content: str):
    _execute(
        """
        UPDATE messages
        SET content = %s
        WHERE msg_id = %s
        """,
        (content, msg_id),
    )


def insert_attachment(message_id: int, data_bytes: bytes, mime_type: str | None = None):
    _execute(
        """
        INSERT INTO attachments (message_id, mime_type, data)
        VALUES (%s, %s, %s)
        """,
        (message_id, mime_type, data_bytes),
    )


def get_history_for_user(username: str, limit: int = 200):
    rows = _execute(
        """
        SELECT msg_id, msg_type, channel, sender_username, receiver_username, content, created_at
        FROM messages
        WHERE msg_type != 'private'
           OR sender_username = %s
           OR receiver_username = %s
        ORDER BY msg_id ASC
        LIMIT %s
        """,
        (username, username, limit),
        fetchall=True,
    ) or []

    history = []
    for row in rows:
        if isinstance(row, dict):
            item = dict(row)
        else:
            item = {
                "msg_id": row[0],
                "msg_type": row[1],
                "channel": row[2],
                "sender_username": row[3],
                "receiver_username": row[4],
                "content": row[5],
                "created_at": row[6],
            }
        history.append(
            {
                "msg_id": item["msg_id"],
                "msg_type": item["msg_type"],
                "channel": item["channel"],
                "sender": item["sender_username"],
                "receiver": item["receiver_username"],
                "content": item["content"],
                "timestamp": item["created_at"],
            }
        )
    return history
