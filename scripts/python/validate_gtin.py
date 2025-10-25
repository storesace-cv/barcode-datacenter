#!/usr/bin/env python3
import argparse, csv

def valid_gtin(code: str) -> bool:
    if not code.isdigit() or len(code) not in (8,12,13,14):
        return False
    digits = list(map(int, code))
    check = digits[-1]
    body = digits[:-1]
    factor = 3
    s = 0
    for d in reversed(body):
        s += d * factor
        factor = 1 if factor==3 else 3
    calc = (10 - (s % 10)) % 10
    return calc == check

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", required=True)
ap.add_argument("--out", dest="out", required=True)
args = ap.parse_args()

with open(args.inp, newline="", encoding="utf-8") as fin, open(args.out, "w", newline="", encoding="utf-8") as fout:
    r = csv.DictReader(fin)
    cols = r.fieldnames + ["gtin_valid"]
    w = csv.DictWriter(fout, fieldnames=cols)
    w.writeheader()
    for row in r:
        gtin = row.get("gtin","")
        row["gtin_valid"] = "1" if gtin and valid_gtin(gtin) else "0"
        w.writerow(row)
print(f"Validated -> {args.out}")
