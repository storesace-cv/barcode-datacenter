# Taxonomy Design (Family/Subfamily)

This taxonomy serves Portugal (PT), Angola (ANG) and Cabo Verde (CV). It follows a pragmatic mapping:
- Base layer inspired by GS1/GPC families (high-level).
- Retailer categories are mapped via heuristics to these families/subfamilies.
- OFF categories are used as a fallback when retailer mapping is absent.

Seed CSVs are in `data/seed/*.csv`. Extend by appending rows. Keep names UPPERCASE and ASCII-only for determinism.
