#!/usr/bin/env python3
import sys, argparse, json, pathlib
from typing import Any, Dict

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True, choices=["PT","ANG","CV"])
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # Offline sample generator (no network). Acts as a stub.
    sample = [
        {
            "code": "5601234567890",
            "product_name": "Arroz Agulha 1kg",
            "brands": "BOM SUCESSO",
            "quantity": "1 kg",
            "categories": "Cereais e derivados, Arroz",
            "countries": "Portugal",
            "url": "https://openfoodfacts.org/product/5601234567890",
        },
        {
            "code": "5609876543210",
            "product_name": "Água Mineral 1,5L",
            "brands": "LUSO",
            "quantity": "1.5 l",
            "categories": "Bebidas, Águas",
            "countries": "Portugal",
            "url": "https://openfoodfacts.org/product/5609876543210",
        },
    ]
    outp = pathlib.Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", encoding="utf-8") as f:
        for i in range(args.limit):
            rec = sample[i % len(sample)].copy()
            # tweak code to keep uniqueness in stub
            rec["code"] = str(int(sample[i % len(sample)]["code"]) + i)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {args.limit} OFF-like records to {args.out}")

if __name__ == "__main__":
    main()
