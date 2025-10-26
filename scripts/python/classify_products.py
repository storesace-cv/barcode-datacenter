#!/usr/bin/env python3
import argparse, csv

rules = [
    ("MERCEARIA","ARROZ", ["ARROZ","RISOTTO"]),
    ("BEBIDAS","AGUAS", ["AGUA","AGUAS"]),
    ("MERCEARIA","MASSAS", ["MASSA","ESPAGUETE","ESPAGUETI","MACARRAO","PASTA"]),
]

def classify(name, category_raw):
    t = f"{name} {category_raw}"
    for fam, sub, keys in rules:
        if any(k in t for k in keys):
            return fam, sub
    return "UNMAPPED","UNMAPPED"

def process_file(inp: str, out: str) -> int:
    with open(inp, newline="", encoding="utf-8") as fin, open(out, "w", newline="", encoding="utf-8") as fout:
        r = csv.DictReader(fin)
        cols = r.fieldnames or []
        if "family" not in cols:
            cols.append("family")
        if "subfamily" not in cols:
            cols.append("subfamily")
        w = csv.DictWriter(fout, fieldnames=cols)
        w.writeheader()
        count = 0
        for row in r:
            fam, sub = classify(row.get("name", ""), row.get("category_raw", ""))
            row["family"], row["subfamily"] = fam, sub
            w.writerow(row)
            count += 1
    return count


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--country", choices=["PT","ANG","CV"], required=True)
    args = ap.parse_args(argv)

    count = process_file(args.inp, args.out)
    print(f"Classified -> {args.out} ({count} rows)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
