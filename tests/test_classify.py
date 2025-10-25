from scripts.python.classify_products import classify

def test_classify_arroz():
    fam, sub = classify("ARROZ AGULHA 1KG", "CEREAIS E DERIVADOS, ARROZ")
    assert fam == "MERCEARIA" and sub == "ARROZ"
