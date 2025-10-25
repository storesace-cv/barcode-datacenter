#!/usr/bin/env python3
import argparse, csv

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", required=True)
ap.add_argument("--out", dest="out", required=True)
ap.add_argument("--country", choices=["PT","ANG","CV"], required=True)
args = ap.parse_args()

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

with open(args.inp, newline="", encoding="utf-8") as fin, open(args.out, "w", newline="", encoding="utf-8") as fout:
    r = csv.DictReader(fin)
    cols = r.fieldnames
    w = csv.DictWriter(fout, fieldnames=cols)
    w.writeheader()
    for row in r:
        fam, sub = classify(row["name"], row["category_raw"])
        row["family"], row["subfamily"] = fam, sub
        w.writerow(row)
print(f"Classified -> {args.out}")
