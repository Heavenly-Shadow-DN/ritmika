"""SQLite: подключение на время запроса и схема базы Ritmika."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    items_total INTEGER NOT NULL,
    delivery INTEGER NOT NULL,
    total INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id TEXT NOT NULL,
    name TEXT NOT NULL,
    size TEXT NOT NULL,
    qty INTEGER NOT NULL,
    price INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    consent INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def get_db() -> sqlite3.Connection:
    """Возвращает соединение на текущий запрос, создавая его при первом обращении."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc: BaseException | None = None) -> None:
    """Закрывает соединение в конце запроса (teardown_appcontext)."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(database: str) -> None:
    """Создаёт файл базы и схему, если их ещё нет."""
    conn = sqlite3.connect(database)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    """Одна строка результата или None."""
    return get_db().execute(sql, params).fetchone()


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    """Все строки результата."""
    return get_db().execute(sql, params).fetchall()


def iterate_rows(sql: str, params: tuple = ()) -> Iterator[sqlite3.Row]:
    """Курсор-генератор для больших выборок (сейчас не используется, оставлен для роста)."""
    yield from get_db().execute(sql, params)
