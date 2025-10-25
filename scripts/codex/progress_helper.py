#!/usr/bin/env python3
import argparse, json, os, sys, datetime
PROGRESS_PATH = "docs/en/codex/progress.json"
def load_progress():
    if not os.path.exists(PROGRESS_PATH):
        return {"phases": {}}
    return json.load(open(PROGRESS_PATH, "r", encoding="utf-8"))
def save_progress(data):
    os.makedirs(os.path.dirname(PROGRESS_PATH), exist_ok=True)
    json.dump(data, open(PROGRESS_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--value", type=int, required=True)
    ap.add_argument("--msg", required=True)
    a = ap.parse_args()
    data = load_progress()
    phases = data.setdefault("phases", {})
    phase = phases.setdefault(str(a.phase), {})
    tasks = phase.setdefault("tasks", {})
    task = tasks.setdefault(a.task, {})
    task["value"] = max(0, min(100, a.value))
    task["msg"] = a.msg
    phase["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    save_progress(data)
    print(f"Updated: phase {a.phase} / {a.task} = {task['value']} — {a.msg}")
if __name__ == "__main__":
    sys.exit(main())
