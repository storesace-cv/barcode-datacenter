#!/usr/bin/env python3
import json
import sqlite3
import datetime
from pathlib import Path
from typing import Any, Dict, List

try:
    import webview
except Exception as e:
    webview = None

DB_PATH = Path("data/barcode_gui.db")
PIPELINE_OUTPUT = Path("data/unified_all.csv")
SEED_DASHBOARD_DATA = Path("data/seed/gui_demo_products.json")


def load_pipeline_products() -> List[Dict[str, Any]]:
    """Stub loader for the unified pipeline output.

    The real implementation will parse ``data/unified_all.csv`` and map the
    columns into the dashboard data model. For now we simply acknowledge the
    source without performing any I/O to keep the stub deterministic.
    """

    if PIPELINE_OUTPUT.exists():
        # Placeholder: the future implementation will transform the CSV rows.
        return []
    return []


def load_seed_products() -> List[Dict[str, Any]]:
    """Load deterministic GUI seed data when pipeline artifacts are missing."""

    if not SEED_DASHBOARD_DATA.exists():
        return []
    try:
        return json.loads(SEED_DASHBOARD_DATA.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # The stub should be resilient while the seed evolves.
        return []


def build_dashboard_payload() -> Dict[str, Any]:
    """Compose the dashboard payload using pipeline data with seed fallback."""

    products = load_pipeline_products() or load_seed_products()
    return {
        "generated_at": now_utc(),
        "metrics": {
            "total_products": len(products),
            "source": "stub",
        },
        "recent_products": products[:5],
        "classification": {
            "coverage": {},
            "summary": [],
        },
        "roadmap": {},
    }


def render_dashboard_html(payload: Dict[str, Any]) -> str:
    """Render an HTML dashboard for the GUI.

    The future implementation will inject structured metrics into a template.
    For now we reuse the static ``gui/dashboard.html`` file so that the stubbed
    backend remains backwards compatible with the existing frontend.
    """

    html_path = Path("gui/dashboard.html")
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    # Last resort stub content to avoid runtime errors while iterating.
    return "<html><body><p>Dashboard template missing.</p></body></html>"

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
        payload = build_dashboard_payload()
        return render_dashboard_html(payload)

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
