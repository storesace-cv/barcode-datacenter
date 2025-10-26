#!/usr/bin/env python3
import argparse, json, os, datetime, sys
P = "docs/en/codex/progress.json"
def load():
    if not os.path.exists(P):
        return {"phases": {}}
    return json.load(open(P, "r", encoding="utf-8"))
def save(d):
    os.makedirs(os.path.dirname(P), exist_ok=True)
    json.dump(d, open(P, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--value", type=int, required=True)
    ap.add_argument("--msg", required=True)
    a = ap.parse_args()
    d = load()
    ph = d.setdefault("phases", {}).setdefault(str(a.phase), {})
    tasks = ph.setdefault("tasks", {})
    tasks.setdefault(a.task, {})
    tasks[a.task]["value"] = max(0, min(100, a.value))
    tasks[a.task]["msg"] = a.msg
    ph["updated_at"] = datetime.datetime.utcnow().isoformat()+"Z"
    save(d)
    print("OK")
