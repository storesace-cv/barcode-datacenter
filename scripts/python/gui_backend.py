#!/usr/bin/env python3
import json, os, sqlite3, datetime
from pathlib import Path

try:
    import webview
except Exception as e:
    webview = None

DB_PATH = Path("data/barcode_gui.db")

def now_utc():
    return datetime.datetime.utcnow().isoformat(timespec="seconds")

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS logs(
        ts TEXT, action TEXT, payload TEXT)""" )
    return conn

class ExposedAPI:
    def __init__(self):
        self.conn = get_conn()

    def log_action(self, action, payload):
        self.conn.execute("INSERT INTO logs VALUES(?,?,?)", (now_utc(), action, json.dumps(payload)))
        self.conn.commit()
        return {"ok": True}

    def get_dashboard_template(self):
        html_path = Path("gui/dashboard.html")
        return html_path.read_text(encoding="utf-8")

    def list_logs(self, limit=50):
        cur = self.conn.execute("SELECT ts,action,payload FROM logs ORDER BY ts DESC LIMIT ?", (limit,))
        rows = [{"ts": r[0], "action": r[1], "payload": r[2]} for r in cur.fetchall()]
        return rows

def main():
    if webview is None:
        print("pywebview not installed. Install with: pip install pywebview")
        return
    api = ExposedAPI()
    window = webview.create_window("Barcode Datacenter GUI", "gui/index.html", width=1200, height=800, js_api=api)
    webview.start()

if __name__ == "__main__":
    main()
