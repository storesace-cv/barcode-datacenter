#!/usr/bin/env python3
import argparse, json, csv, re
try:
    from unidecode import unidecode
except ModuleNotFoundError:  # pragma: no cover - fallback path
    import unicodedata

    def unidecode(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value or "")
        return "".join(ch for ch in normalized if not unicodedata.combining(ch))

def norm(text: str) -> str:
    t = unidecode(text or "").upper()
    t = re.sub(r"[^A-Z0-9 ,.;:/()\-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def split_qty(quantity: str):
    q = norm(quantity)
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(KG|G|L|ML|UN|UNI|UNID|LITRO|LITROS|GRAMAS|MILILITROS)?", q)
    if not m:
        return "", ""
    qty = m.group(1)
    uom = (m.group(2) or "").replace("GRAMAS","G").replace("MILILITROS","ML").replace("LITROS","L").replace("LITRO","L")
    if uom in ("UNI","UNID"): uom = "UN"
    return qty, uom

def write_normalized(inp: str, out: str, country: str) -> int:
    count = 0
    with open(inp, "r", encoding="utf-8") as fin, open(out, "w", encoding="utf-8", newline="") as fout:
        w = csv.writer(fout)
        w.writerow(["gtin","name","brand","qty","uom","country","source","url","price","currency","category_raw","family","subfamily"])
        for line in fin:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            gtin = rec.get("code","")
            name = norm(rec.get("product_name",""))
            brand = norm(rec.get("brands",""))
            qty, uom = split_qty(rec.get("quantity",""))
            source = "OFF"
            url = rec.get("url","")
            price = ""
            currency = {"PT":"EUR","ANG":"AOA","CV":"CVE"}[country]
            category_raw = norm(rec.get("categories",""))
            w.writerow([gtin,name,brand,qty,uom,country,source,url,price,currency,category_raw,"",""])
            count += 1
    return count


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--country", choices=["PT","ANG","CV"], required=True)
    args = ap.parse_args(argv)

    count = write_normalized(args.inp, args.out, args.country)
    print(f"Wrote normalized CSV to {args.out} ({count} rows)")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
