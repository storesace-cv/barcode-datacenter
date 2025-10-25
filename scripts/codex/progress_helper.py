#!/usr/bin/env python3
import argparse, json, os, sys, datetime

PROGRESS_PATH = "docs/en/codex/progress.json"

def load_progress():
    if not os.path.exists(PROGRESS_PATH):
        return {"phases": {}}
    with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_progress(data):
    os.makedirs(os.path.dirname(PROGRESS_PATH), exist_ok=True)
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=str, required=True)
    ap.add_argument("--task", type=str, required=True)
    ap.add_argument("--value", type=int, required=True)
    ap.add_argument("--msg", type=str, required=True)
    args = ap.parse_args()

    data = load_progress()
    phases = data.setdefault("phases", {})
    phase = phases.setdefault(str(args.phase), {})
    tasks = phase.setdefault("tasks", {})
    task = tasks.setdefault(args.task, {})
    task["value"] = max(0, min(100, args.value))
    task["msg"] = args.msg
    phase["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    save_progress(data)
    print(f"Progress updated: phase {args.phase} / {args.task} = {task['value']} — {args.msg}")

if __name__ == "__main__":
    sys.exit(main())
