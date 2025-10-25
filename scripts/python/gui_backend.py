#!/usr/bin/env python3
import importlib.util
import json
import os
import platform
import sys
import threading
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

HOST, PORT = "127.0.0.1", 6754
ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "gui")
ROOT = os.path.abspath(ROOT)

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve from GUI root
        path = path.split('?',1)[0].split('#',1)[0]
        new_path = ROOT
        for part in path.strip('/').split('/'):
            if part:
                new_path = os.path.join(new_path, part)
        return new_path

    def do_GET(self):
        if self.path.startswith("/api/status"):
            data = {"ok": True, "ts": time.time(), "root": ROOT}
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return
        if self.path.startswith("/api/run/"):
            act = self.path.rsplit('/',1)[-1]
            if act == "verify-phase5":
                res = {"runner":500,"status":"ok"}
            elif act == "export-artifacts":
                res = {"task":"export_artifacts","status":"queued"}
            else:
                res = {"error":"unknown action"}
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return
        # default static files
        if self.path in ("/", ""):
            self.path = "/index.html"
        return super().do_GET()

def start_server():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def _missing_modules(names):
    return [name for name in names if importlib.util.find_spec(name) is None]


def _macos_runtime_check():
    if platform.system() != "Darwin":
        return True, []
    missing = _missing_modules(["objc"])
    return len(missing) == 0, missing


def _configure_pywebview_environment():
    if platform.system() == "Darwin":
        os.environ.setdefault("PYWEBVIEW_GUI", "cocoa")
        os.environ.setdefault("PYWEBVIEW_OPEN_IN_BROWSER", "0")
    else:
        os.environ.setdefault("PYWEBVIEW_GUI", "qt")

def selftest():
    httpd = start_server()
    print(f"[GUI] Serving {ROOT} at http://{HOST}:{PORT}/index.html")
    # simple check: file exists
    idx = os.path.join(ROOT, "index.html")
    ok = os.path.isfile(idx)
    print(f"[GUI] index.html exists: {ok}")
    # stop after short delay
    time.sleep(1.0)
    httpd.shutdown()
    return 0 if ok else 2

def main():
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    ok, missing = _macos_runtime_check()
    if not ok:
        print("[GUI] Missing macOS dependencies for pywebview:")
        for module in missing:
            print(f"       - {module} (install pyobjc)")
    _configure_pywebview_environment()
    httpd = start_server()
    url = f"http://{HOST}:{PORT}/index.html"
    print(f"[GUI] URL: {url}")
    try:
        import webview
        if not ok:
            raise RuntimeError("PyObjC runtime unavailable")
        backend = os.environ.get("PYWEBVIEW_GUI", "auto")
        print(f"[GUI] Launching pywebview backend='{backend}'")
        webview.create_window("Barcode Datacenter GUI", url)
        webview.start(gui=backend)
    except Exception as e:
        print(f"[GUI] pywebview not available ({e}); fallback: open in default browser")
        import webbrowser
        webbrowser.open(url)
        # Keep server alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    httpd.shutdown()

if __name__ == "__main__":
    main()
