import sqlite3, datetime
from pathlib import Path

DB_PATH = Path("data/barcode_gui.db")

def now_utc():
    return datetime.datetime.utcnow().isoformat(timespec="seconds")

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS logs(
        ts TEXT, action TEXT, payload TEXT)""")
    return conn
