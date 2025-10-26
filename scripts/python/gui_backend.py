#!/usr/bin/env python3
"""HTTP backend powering the smart-mode dashboard and GUI."""

from __future__ import annotations

import json
import os
import platform
import sys
import threading
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Optional

from pipeline import ARTIFACTS_ROOT, LOGS_DIR
from pipeline.orchestrator import SmartPipelineRunner

HOST, PORT = "127.0.0.1", 6754
ROOT = Path(__file__).resolve().parents[2] / "gui"
ROOT = ROOT.resolve()

RUNNER = SmartPipelineRunner()
RUN_LOCK = threading.Lock()


def _read_json_body(handler: SimpleHTTPRequestHandler) -> Dict[str, object]:
    length = int(handler.headers.get("Content-Length", "0"))
    if length == 0:
        return {}
    data = handler.rfile.read(length).decode("utf-8")
    if not data:
        return {}
    return json.loads(data)


def _artifact_listing() -> Dict[str, list]:
    artifacts = {"working": [], "outputs": [], "logs": []}
    for key in ("working", "outputs", "logs"):
        directory = ARTIFACTS_ROOT / key
        if not directory.exists():
            continue
        files = []
        for path in sorted(directory.glob("**/*")):
            if path.is_file():
                files.append(str(path.relative_to(ARTIFACTS_ROOT)))
        artifacts[key] = files
    return artifacts


def _run_pipeline_action(slug: str, payload: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    payload = payload or {}
    overrides = payload.get("overrides") if isinstance(payload.get("overrides"), dict) else {}
    with RUN_LOCK:
        if slug == "pipeline":
            RUNNER.run_all(overrides=overrides if isinstance(overrides, dict) else None)
            result = {"status": "ok", "steps": RUNNER.status()}
        else:
            step_overrides = overrides if isinstance(overrides, dict) else {}
            step_result = RUNNER.run_step(slug, **step_overrides)
            result = {"status": "ok", "step": step_result.to_dict()}
    return result


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split('?',1)[0].split('#',1)[0]
        new_path = str(ROOT)
        for part in path.strip('/').split('/'):
            if part:
                new_path = os.path.join(new_path, part)
        return new_path

    def _json_response(self, payload: Dict[str, object], status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/api/status"):
            payload = {
                "ok": True,
                "ts": time.time(),
                "steps": RUNNER.status(),
            }
            return self._json_response(payload)
        if self.path.startswith("/api/artifacts"):
            return self._json_response({"artifacts": _artifact_listing()})
        if self.path.startswith("/api/logs"):
            logs = {}
            for path in LOGS_DIR.glob("*.log"):
                logs[path.name] = path.read_text(encoding="utf-8")
            return self._json_response({"logs": logs})
        if self.path in ("/", ""):
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/run/"):
            slug = self.path.rsplit('/', 1)[-1]
            try:
                payload = _read_json_body(self)
                result = _run_pipeline_action(slug, payload)
            except KeyError:
                return self._json_response({"error": f"unknown action: {slug}"}, status=404)
            except Exception as exc:  # pragma: no cover - runtime error path
                return self._json_response({"error": str(exc)}, status=500)
            return self._json_response(result)
        return self._json_response({"error": "unsupported endpoint"}, status=404)


def start_server():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def _missing_modules(names):
    import importlib.util

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
    idx = ROOT / "index.html"
    ok = idx.is_file()
    print(f"[GUI] index.html exists: {ok}")
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
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    httpd.shutdown()


if __name__ == "__main__":
    main()
