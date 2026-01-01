import json
import sqlite3
from datetime import datetime, timezone

_SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    asin        TEXT,
    url         TEXT,
    title       TEXT,
    price       REAL,
    currency    TEXT,
    rating      REAL,
    availability TEXT,
    image_urls  TEXT,
    fetch_token TEXT,
    internal_seller_id TEXT,
    created_at  TEXT,
    updated_at  TEXT
);
"""


def _now():
    return datetime.now(timezone.utc).isoformat()


def connect(db_path):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn):
    conn.executescript(_SCHEMA)
    conn.commit()


def _row_to_product(row):
    if row is None:
        return None
    data = dict(row)
    raw_images = data.get("image_urls")
    data["image_urls"] = json.loads(raw_images) if raw_images else []
    return data


def get_by_asin(conn, asin):
    row = conn.execute("SELECT * FROM products WHERE asin = ?", (asin,)).fetchone()
    return _row_to_product(row)


def get_by_url(conn, url):
    row = conn.execute("SELECT * FROM products WHERE url = ?", (url,)).fetchone()
    return _row_to_product(row)


def list_products(conn):
    rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    return [_row_to_product(r) for r in rows]


def insert(conn, asin, url, details):
    now = _now()
    conn.execute(
        """
        INSERT INTO products
            (asin, url, title, price, currency, availability, image_urls, fetch_token, internal_seller_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            asin,
            url,
            details.get("title"),
            details.get("price"),
            details.get("currency"),
            details.get("availability"),
            json.dumps(details.get("image_urls") or []),
            details.get("fetch_token"),
            details.get("internal_seller_id"),
            now,
            now,
        ),
    )
    conn.commit()
    return get_by_asin(conn, asin)


def update(conn, asin, details):
    now = _now()
    conn.execute(
        """
        UPDATE products
           SET currency = ?,
               availability = ?,
               image_urls = ?,
               created_at = ?,
               updated_at = ?
         WHERE asin = ?
        """,
        (
            details.get("currency"),
            details.get("availability"),
            json.dumps(details.get("image_urls") or []),
            now,
            now,
            asin,
        ),
    )
    conn.commit()
    return get_by_asin(conn, asin)


def delete(conn, asin):
    cur = conn.execute("DELETE FROM products WHERE asin = ?", (asin,))
    conn.commit()
    return cur.rowcount
