#!/usr/bin/env python3
import argparse, csv, json, os, sqlite3

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", required=True)
ap.add_argument("--outdir", required=True)
args = ap.parse_args()

os.makedirs(args.outdir, exist_ok=True)
csv_out = os.path.join(args.outdir, "barcode_unified.csv")
jsonl_out = os.path.join(args.outdir, "barcode_unified.jsonl")
db_out = os.path.join(args.outdir, "barcode_unified.sqlite")

# Copy CSV (normalized header order)
with open(args.inp, newline="", encoding="utf-8") as fin:
    r = csv.DictReader(fin)
    cols = r.fieldnames or []
    rows = list(r)
    with open(csv_out, "w", newline="", encoding="utf-8") as fout:
        w = csv.DictWriter(fout, fieldnames=cols)
        w.writeheader()
        for row in rows:
            w.writerow(row)

# JSONL
with open(csv_out, newline="", encoding="utf-8") as fin, open(jsonl_out, "w", encoding="utf-8") as jout:
    r = csv.DictReader(fin)
    for row in r:
        jout.write(json.dumps(row, ensure_ascii=False) + "\n")

# SQLite
con = sqlite3.connect(db_out)
cols = rows[0].keys() if rows else []
col_defs = ", ".join(f'"{c}" TEXT' for c in cols)
con.execute(f'CREATE TABLE IF NOT EXISTS products ({col_defs});')
if rows:
    placeholders = ", ".join(["?"]*len(cols))
    con.executemany(f'INSERT INTO products VALUES ({placeholders});', [tuple(row.get(c) for c in cols) for row in rows])
# Indices utilitários
try:
    con.execute('CREATE INDEX IF NOT EXISTS idx_gtin ON products(gtin);')
    con.execute('CREATE INDEX IF NOT EXISTS idx_brand ON products(brand);')
    con.execute('CREATE INDEX IF NOT EXISTS idx_family_sub ON products(family, subfamily);')
except Exception:
    pass
con.commit(); con.close()

print(f"Wrote artifacts:\n - {csv_out}\n - {jsonl_out}\n - {db_out}")
