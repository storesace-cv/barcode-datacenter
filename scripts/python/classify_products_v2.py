#!/usr/bin/env python3
import argparse, csv, re, os
from unidecode import unidecode

def up(s:str)->str:
    return re.sub(r"\s+"," ", unidecode((s or "").upper()).strip())

def load_map(path, key_col, val_col, sep=';'):
    m = {}
    if not os.path.isfile(path): return m
    with open(path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f, delimiter=sep)
        for row in r:
            k = up(row[key_col])
            v = up(row[val_col])
            if k:
                m[k]=v
    return m

def load_rules(path, sep=';'):
    rules = []
    if not os.path.isfile(path): return rules
    with open(path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f, delimiter=sep)
        for row in r:
            rules.append({k: up(v) for k,v in row.items()})
    return rules

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", required=True)
ap.add_argument("--out", dest="out", required=True)
ap.add_argument("--country", choices=["PT","ANG","CV"], required=True)
ap.add_argument("--dict-root", default="data/seed/dictionaries")
args = ap.parse_args()

# Load dictionaries
uom_syn = load_map(os.path.join(args.dict_root, "synonyms_uom.csv"), "FROM", "TO")
brand_map = load_map(os.path.join(args.dict_root, "brands_normalization.csv"), "ALIAS", "CANONICAL")
fam_rules = load_rules(os.path.join(args.dict_root, "family_rules.csv"))
sub_rules = load_rules(os.path.join(args.dict_root, "subfamily_rules.csv"))

def norm_brand(b):
    b2 = up(b)
    return brand_map.get(b2, b2)

def classify(name, category_raw, country):
    txt = f"{name} {category_raw}"
    fam = None
    sub = None
    # FAMILY by rules (country-first)
    for r in fam_rules:
        if r.get("COUNTRY") in (country, "") and r.get("KEYWORD") and r["KEYWORD"] in txt:
            fam = r["FAMILY"]; break
    # SUBFAMILY by rules (requires family)
    if fam:
        for r in sub_rules:
            if r.get("COUNTRY") in (country, "") and r.get("FAMILY")==fam and r.get("KEYWORD") and r["KEYWORD"] in txt:
                sub = r["SUBFAMILY"]; break
    # Heuristics fallback
    if not fam:
        if "ARROZ" in txt: fam="MERCEARIA"
        elif "MASSA" in txt or "ESPAGUETE" in txt or "ESPAGUETI" in txt: fam="MERCEARIA"
        elif "AGUA" in txt: fam="BEBIDAS"
    if not sub and fam:
        if fam=="MERCEARIA" and "ARROZ" in txt: sub="ARROZ"
        elif fam=="MERCEARIA" and ("MASSA" in txt or "ESPAGUETE" in txt or "ESPAGUETI" in txt): sub="MASSAS"
        elif fam=="BEBIDAS" and "AGUA" in txt: sub="AGUAS"
    return (fam or "UNMAPPED", sub or "UNMAPPED")

with open(args.inp, newline="", encoding="utf-8") as fin, open(args.out, "w", newline="", encoding="utf-8") as fout:
    r = csv.DictReader(fin)
    cols = r.fieldnames
    if "family" not in cols: cols += ["family"]
    if "subfamily" not in cols: cols += ["subfamily"]
    if "brand" not in cols: cols += ["brand"]
    w = csv.DictWriter(fout, fieldnames=cols)
    w.writeheader()
    total = 0; unmapped = 0
    for row in r:
        total += 1
        # normalize brand via dictionary
        row["brand"] = norm_brand(row.get("brand",""))
        fam, sub = classify(up(row.get("name","")), up(row.get("category_raw","")), up(row.get("country","")))
        row["family"], row["subfamily"] = fam, sub
        if fam=="UNMAPPED" or sub=="UNMAPPED":
            unmapped += 1
        w.writerow(row)
print(f"Classified v2 -> {args.out}")
