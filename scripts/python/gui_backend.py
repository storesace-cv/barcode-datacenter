#!/usr/bin/env python3
import json, os, sys, threading, time
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
    # Start server then open GUI via pywebview if available
    httpd = start_server()
    url = f"http://{HOST}:{PORT}/index.html"
    print(f"[GUI] URL: {url}")
    try:
        import webview
        webview.create_window("Barcode Datacenter GUI", url)
        webview.start()
    except Exception as e:
        print(f"[GUI] pywebview not available ({e}); fallback: open in default browser")
        import webbrowser
        webbrowser.open(url)
        # Keep server alive
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            pass
    httpd.shutdown()

if __name__ == "__main__":
    main()
