from scripts.python.normalize_products import norm, split_qty

def test_norm_basic():
    assert norm("Água Mineral 1,5L").startswith("AGUA MINERAL")

def test_split_qty():
    assert split_qty("1 kg") == ("1", "KG")
    assert split_qty("1.5 l") == ("1.5", "L")
