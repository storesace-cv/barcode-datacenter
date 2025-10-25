#!/usr/bin/env python3
import argparse, csv, json, re, os
from unidecode import unidecode

def up(s:str)->str:
    import re
    return re.sub(r"\s+"," ", unidecode((s or "").upper()).strip())

def make_key(row):
    gtin = (row.get("gtin") or "").strip()
    gtin_valid = (row.get("gtin_valid") or "0").strip()
    if gtin and gtin_valid in ("1","true","TRUE"):
        return ("GTIN", gtin)
    # fallback canonical key
    name = up(row.get("name",""))
    brand = up(row.get("brand",""))
    qty = (row.get("qty","") or "").strip()
    uom = up(row.get("uom",""))
    return ("CANON", f"{name}|{brand}|{qty}{uom}")

ap = argparse.ArgumentParser()
ap.add_argument("--manifest", required=True)
ap.add_argument("--out-csv", required=True)
ap.add_argument("--dup-report", required=True)
args = ap.parse_args()

with open(args.manifest, "r", encoding="utf-8") as f:
    manifest = json.load(f)

inputs = manifest.get("inputs", [])
rows_all = []
for path in inputs:
    if not os.path.isfile(path): 
        continue
    with open(path, newline="", encoding="utf-8") as fin:
        r = csv.DictReader(fin)
        for row in r:
            rows_all.append(row)

# Unify
by_key = {}
dups = []
for row in rows_all:
    k = make_key(row)
    base = by_key.get(k)
    if base is None:
        # initialize base with provenance list
        base = dict(row)
        base["provenance"] = json.dumps([row.get("source","") or "UNKNOWN"])
        by_key[k] = base
    else:
        # merge: prefer truthy/fresh fields, append provenance
        for field, val in row.items():
            if not base.get(field) and val:
                base[field] = val
        # provenance
        prov = json.loads(base.get("provenance","[]"))
        src = row.get("source","") or "UNKNOWN"
        if src and src not in prov:
            prov.append(src)
        base["provenance"] = json.dumps(sorted(set(prov)))
        dups.append({"key_type":k[0], "key":k[1], "gtin":row.get("gtin",""), "name":row.get("name",""), "source":src})

# Write unified
os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
with open(args.out_csv, "w", newline="", encoding="utf-8") as fout:
    # unify fieldnames
    fieldnames = set()
    for v in by_key.values():
        fieldnames.update(v.keys())
    cols = ["gtin","gtin_valid","name","brand","qty","uom","country","source","url","price","currency","category_raw","family","subfamily","provenance"]
    for c in sorted(fieldnames):
        if c not in cols:
            cols.append(c)
    w = csv.DictWriter(fout, fieldnames=cols)
    w.writeheader()
    for v in by_key.values():
        w.writerow(v)

# Write duplicates report
with open(args.dup_report, "w", newline="", encoding="utf-8") as fdup:
    cols = ["key_type","key","gtin","name","source"]
    w = csv.DictWriter(fdup, fieldnames=cols)
    w.writeheader()
    for d in dups:
        w.writerow(d)

print(f"Unified {len(by_key)} unique rows from {len(rows_all)} inputs.")
print(f"Duplicates report size: {len(dups)}")
