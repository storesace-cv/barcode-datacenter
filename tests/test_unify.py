from scripts.python.dedupe_unify import make_key

def test_make_key_gtin():
    row = {"gtin":"5601234567890","gtin_valid":"1","name":"X","brand":"Y","qty":"1","uom":"KG"}
    k = make_key(row)
    assert k[0] == "GTIN"

def test_make_key_canonical():
    row = {"gtin":"", "gtin_valid":"0","name":"Água Mineral","brand":"Luso","qty":"1.5","uom":"l"}
    k = make_key(row)
    assert k[0] == "CANON"
