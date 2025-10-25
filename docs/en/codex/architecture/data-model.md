# Data Model

## Input (examples)
- JSONL from OFF (`code`, `product_name`, `brands`, `quantity`, `categories`, `countries`, `url`)
- Retailer HTML/JSON (structure varies)

## Normalized Schema (CSV)
`gtin,name,brand,qty,uom,country,source,url,price,currency,category_raw,family,subfamily`

- `qty` numeric; `uom` normalized (G, KG, ML, L, UN).
- `family/subfamily` empty before classification; then filled by classifier.
