import psycopg2
import psycopg2.extras
from config import DB_CONFIG


def _connect():
    return psycopg2.connect(**DB_CONFIG)


def fetch(sql, params=None):
    conn = _connect()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            cols = [d.name for d in cur.description]
        return rows, cols
    finally:
        conn.close()


def execute(sql, params=None):
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()