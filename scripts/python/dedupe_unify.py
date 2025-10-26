#!/usr/bin/env python3
import argparse, csv, json, re, os
try:
    from unidecode import unidecode
except ModuleNotFoundError:  # pragma: no cover - fallback path
    import unicodedata

    def unidecode(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value or "")
        return "".join(ch for ch in normalized if not unicodedata.combining(ch))

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

def load_manifest(manifest_path: str) -> list[str]:
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    return manifest.get("inputs", [])


def unify_files(inputs: list[str]) -> tuple[dict, list]:
    rows_all = []
    for path in inputs:
        if not os.path.isfile(path):
            continue
        with open(path, newline="", encoding="utf-8") as fin:
            r = csv.DictReader(fin)
            rows_all.extend(r)

    by_key = {}
    dups = []
    for row in rows_all:
        k = make_key(row)
        base = by_key.get(k)
        if base is None:
            base = dict(row)
            base["provenance"] = json.dumps([row.get("source", "") or "UNKNOWN"])
            by_key[k] = base
        else:
            for field, val in row.items():
                if not base.get(field) and val:
                    base[field] = val
            prov = json.loads(base.get("provenance", "[]"))
            src = row.get("source", "") or "UNKNOWN"
            if src and src not in prov:
                prov.append(src)
            base["provenance"] = json.dumps(sorted(set(prov)))
            dups.append({"key_type": k[0], "key": k[1], "gtin": row.get("gtin", ""), "name": row.get("name", ""), "source": src})

    return by_key, dups


def write_outputs(out_csv: str, dup_report: str, by_key: dict, dups: list) -> None:
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as fout:
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

    with open(dup_report, "w", newline="", encoding="utf-8") as fdup:
        cols = ["key_type","key","gtin","name","source"]
        w = csv.DictWriter(fdup, fieldnames=cols)
        w.writeheader()
        for d in dups:
            w.writerow(d)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--dup-report", required=True)
    args = ap.parse_args(argv)

    inputs = load_manifest(args.manifest)
    by_key, dups = unify_files(inputs)
    write_outputs(args.out_csv, args.dup_report, by_key, dups)
    print(f"Unified {len(by_key)} unique rows from {len(inputs)} inputs.")
    print(f"Duplicates report size: {len(dups)}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
