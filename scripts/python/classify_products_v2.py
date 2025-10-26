#!/usr/bin/env python3
import argparse, csv, re, os
try:
    from unidecode import unidecode
except ModuleNotFoundError:  # pragma: no cover - fallback path
    import unicodedata

    def unidecode(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value or "")
        return "".join(ch for ch in normalized if not unicodedata.combining(ch))

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

def build_dictionaries(dict_root: str):
    uom_syn = load_map(os.path.join(dict_root, "synonyms_uom.csv"), "FROM", "TO")
    brand_map = load_map(os.path.join(dict_root, "brands_normalization.csv"), "ALIAS", "CANONICAL")
    fam_rules = load_rules(os.path.join(dict_root, "family_rules.csv"))
    sub_rules = load_rules(os.path.join(dict_root, "subfamily_rules.csv"))
    return uom_syn, brand_map, fam_rules, sub_rules


def norm_brand(b):
    b2 = up(b)
    return BRAND_MAP.get(b2, b2)


def classify(name, category_raw, country):
    txt = f"{name} {category_raw}"
    fam = None
    sub = None
    for r in FAM_RULES:
        if r.get("COUNTRY") in (country, "") and r.get("KEYWORD") and r["KEYWORD"] in txt:
            fam = r["FAMILY"]
            break
    if fam:
        for r in SUB_RULES:
            if r.get("COUNTRY") in (country, "") and r.get("FAMILY") == fam and r.get("KEYWORD") and r["KEYWORD"] in txt:
                sub = r["SUBFAMILY"]
                break
    if not fam:
        if "ARROZ" in txt:
            fam = "MERCEARIA"
        elif "MASSA" in txt or "ESPAGUETE" in txt or "ESPAGUETI" in txt:
            fam = "MERCEARIA"
        elif "AGUA" in txt:
            fam = "BEBIDAS"
    if not sub and fam:
        if fam == "MERCEARIA" and "ARROZ" in txt:
            sub = "ARROZ"
        elif fam == "MERCEARIA" and ("MASSA" in txt or "ESPAGUETE" in txt or "ESPAGUETI" in txt):
            sub = "MASSAS"
        elif fam == "BEBIDAS" and "AGUA" in txt:
            sub = "AGUAS"
    return (fam or "UNMAPPED", sub or "UNMAPPED")


def process_file(inp: str, out: str, country: str) -> int:
    with open(inp, newline="", encoding="utf-8") as fin, open(out, "w", newline="", encoding="utf-8") as fout:
        r = csv.DictReader(fin)
        cols = list(r.fieldnames or [])
        if "family" not in cols:
            cols.append("family")
        if "subfamily" not in cols:
            cols.append("subfamily")
        if "brand" not in cols:
            cols.append("brand")
        w = csv.DictWriter(fout, fieldnames=cols)
        w.writeheader()
        total = 0
        for row in r:
            total += 1
            row["brand"] = norm_brand(row.get("brand", ""))
            fam, sub = classify(up(row.get("name", "")), up(row.get("category_raw", "")), up(row.get("country", "")))
            row["family"], row["subfamily"] = fam, sub
            w.writerow(row)
    return total


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--country", choices=["PT","ANG","CV"], required=True)
    ap.add_argument("--dict-root", default="data/seed/dictionaries")
    args = ap.parse_args(argv)

    global UOM_SYN, BRAND_MAP, FAM_RULES, SUB_RULES  # type: ignore[assignment]
    UOM_SYN, BRAND_MAP, FAM_RULES, SUB_RULES = build_dictionaries(args.dict_root)

    total = process_file(args.inp, args.out, args.country)
    print(f"Classified v2 -> {args.out} ({total} rows)")
    return 0


# Dictionaries are loaded lazily via main() or tests can populate them explicitly
UOM_SYN, BRAND_MAP, FAM_RULES, SUB_RULES = build_dictionaries("data/seed/dictionaries")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
