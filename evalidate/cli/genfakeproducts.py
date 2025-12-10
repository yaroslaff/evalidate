#!/usr/bin/env python3
"""
gen_products.py
Generate fake e-commerce products (USD, no images) using Faker.

Default:
    10,000 products → products.json
Example:
    python3 gen_products.py --out /tmp/products.json --count 5000
"""

import argparse, json, random, uuid
from datetime import datetime, UTC
try:
    from faker import Faker
except ImportError:
    print("Faker library is required. You can reinstall evalidate with the 'generate' extra: pipx install 'evalidate[generate]'")
    exit(1)

fake = Faker()


BRANDS = {
    "phones":  ["Samsung", "Apple", "Xiaomi", "OnePlus", "Google"],
    "laptops": ["Dell", "HP", "Lenovo", "Asus", "Acer", "Apple"],
    "audio":   ["Sony", "JBL", "Bose", "Sennheiser", "Marshall"],
    "tv":      ["LG", "Samsung", "Philips", "TCL", "Panasonic"],
    "camera":  ["Canon", "Nikon", "Sony", "Fujifilm", "GoPro"],
    "appliances": ["Bosch", "Philips", "Panasonic", "Midea", "Tefal"]
}

SUFFIXES = ["", " Pro", " Max", " Plus", " Ultra", " SE"]

def make_title(category, brand):
    letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
    numbers = str(random.randint(100, 9999))
    suffix = random.choice(SUFFIXES)
    return f"{brand} {letters}-{numbers}{suffix}"

def make_price(category):
    base = {
        "phones": 300, "laptops": 800, "audio": 120,
        "tv": 400, "camera": 600, "appliances": 200
    }.get(category, 100)
    p = base * random.uniform(0.7, 1.8)
    return round(p - 0.01, 2)

def make_description(category, brand):
    return fake.sentence(nb_words=random.randint(12, 24)) + f" {brand} {category} designed for modern users."

def make_attributes(category):
    attrs = {}
    if category in ("phones", "laptops"):
        attrs["storage"] = random.choice(["64GB","128GB","256GB","512GB","1TB"])
    if category in ("phones","audio","camera"):
        attrs["color"] = random.choice(["black","white","blue","red","silver"])
    if category in ("tv","appliances"):
        attrs["power_w"] = random.choice([800,1200,1500,2000])
    return attrs

def gen_product():
    category = random.choice(list(BRANDS.keys()))
    brand = random.choice(BRANDS[category])
    uid = str(uuid.uuid4())
    return {
        "id": uid,
        "sku": f"SKU-{uid[:8].upper()}",
        "title": make_title(category, brand),
        "brand": brand,
        "category": category,
        "description": make_description(category, brand),
        "price": make_price(category),
        "currency": "USD",
        "stock": random.randint(0, 500),
        "rating": round(random.uniform(3.0, 5.0), 2),
        "reviews_count": random.randint(0, 1000),
        "attributes": make_attributes(category),
        "tags": random.sample(["new","bestseller","discount","limited","eco"], k=random.randint(0,3)),
    }

def main():
    ap = argparse.ArgumentParser(description="Generate fake e-commerce products in JSON format.")
    ap.add_argument("-n", "--num", type=int, default=10000, help="Number of products to generate (default: 10000).")
    ap.add_argument("-o", "--out", type=str, default="products.json", help="Output JSON file path (default: products.json).")
    args = ap.parse_args()

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("[\n")
        for i in range(args.num):
            json.dump(gen_product(), f, ensure_ascii=False)
            if i != args.num - 1:
                f.write(",\n")
        f.write("\n]\n")

    print(f"Wrote {args.num} products to {args.out}")

if __name__ == "__main__":
    main()
