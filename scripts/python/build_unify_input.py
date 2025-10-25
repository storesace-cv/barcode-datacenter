#!/usr/bin/env python3
import argparse, json, os, glob

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
args = ap.parse_args()

# discover validated or classified CSVs
candidates = []
for pat in ["data/validated_*.csv", "data/classified_*.csv", "data/classified_*_v2.csv"]:
    for p in glob.glob(pat):
        if os.path.isfile(p) and os.path.getsize(p) > 0:
            candidates.append(p)

manifest = {"inputs": sorted(set(candidates))}
os.makedirs("data", exist_ok=True)
with open(args.out, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)
print(f"Wrote manifest with {len(manifest['inputs'])} inputs -> {args.out}")
