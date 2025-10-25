from scripts.python.classify_products_v2 import up, classify, norm_brand

def test_up():
    assert up("Água Mineral") == "AGUA MINERAL"

def test_brand_norm():
    assert norm_brand("coca cola") == "COCA-COLA"

def test_classify_arroz():
    fam, sub = classify("ARROZ AGULHA 1KG", "CEREAIS E DERIVADOS, ARROZ", "PT")
    assert fam == "MERCEARIA" and sub == "ARROZ"
