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

def process_file(inp: str, out: str) -> int:
    with open(inp, newline="", encoding="utf-8") as fin, open(out, "w", newline="", encoding="utf-8") as fout:
        r = csv.DictReader(fin)
        cols = list(r.fieldnames or [])
        if "gtin_valid" not in cols:
            cols.append("gtin_valid")
        w = csv.DictWriter(fout, fieldnames=cols)
        w.writeheader()
        count = 0
        for row in r:
            gtin = row.get("gtin", "")
            row["gtin_valid"] = "1" if gtin and valid_gtin(gtin) else "0"
            w.writerow(row)
            count += 1
    return count


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    args = ap.parse_args(argv)

    count = process_file(args.inp, args.out)
    print(f"Validated -> {args.out} ({count} rows)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
