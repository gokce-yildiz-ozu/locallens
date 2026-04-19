"""
places.json dosyasının şema uygunluğunu kontrol eder.
Hatalı mekan varsa detaylı rapor verir, her şey yolundaysa özet basar.
"""

import json
from pathlib import Path

REQUIRED_FIELDS = {"id", "name", "category", "neighborhood", "price_level", "tags", "description", "coordinates"}
VALID_CATEGORIES = {"kafe", "restoran", "bar", "gece kulübü", "meyhane", "müze", "park", "koşu_parkuru", "manzara"}
VALID_PRICE_LEVELS = {1, 2, 3, 4}


def validate_place(place: dict, index: int) -> list[str]:
    errors = []
    place_id = place.get("id", f"index_{index}")

    missing = REQUIRED_FIELDS - place.keys()
    if missing:
        errors.append(f"[{place_id}] Eksik alanlar: {missing}")
        return errors  # eksik alan varsa diğer kontroller anlamsız

    if place["category"] not in VALID_CATEGORIES:
        errors.append(f"[{place_id}] Geçersiz kategori: '{place['category']}' — geçerliler: {VALID_CATEGORIES}")

    if place["price_level"] not in VALID_PRICE_LEVELS:
        errors.append(f"[{place_id}] Geçersiz price_level: {place['price_level']} — 1-4 arası olmalı")

    if not isinstance(place["tags"], list) or len(place["tags"]) == 0:
        errors.append(f"[{place_id}] 'tags' boş veya liste değil")

    # Embedding kalitesi için açıklama uzunluğu kritik
    if len(place["description"]) < 50:
        errors.append(f"[{place_id}] 'description' çok kısa ({len(place['description'])} karakter) — en az 50 karakter olmalı")

    coords = place["coordinates"]
    if not isinstance(coords, dict) or "lat" not in coords or "lng" not in coords:
        errors.append(f"[{place_id}] 'coordinates' eksik veya hatalı format")

    return errors


def validate_all(data_path: Path) -> None:
    with open(data_path, encoding="utf-8") as f:
        places = json.load(f)

    all_errors = []
    ids_seen = set()

    for i, place in enumerate(places):
        # Duplicate ID kontrolü
        place_id = place.get("id")
        if place_id in ids_seen:
            all_errors.append(f"[{place_id}] Duplicate ID!")
        ids_seen.add(place_id)

        errors = validate_place(place, i)
        all_errors.extend(errors)

    print(f"Toplam mekan: {len(places)}")

    if all_errors:
        print(f"HATA — {len(all_errors)} sorun bulundu:\n")
        for err in all_errors:
            print(f"  ✗ {err}")
    else:
        categories = {}
        for p in places:
            categories[p["category"]] = categories.get(p["category"], 0) + 1
        print("Tüm mekanlar geçerli.\n")
        print("Kategori dağılımı:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    data_path = Path(__file__).parent.parent / "data" / "places.json"
    validate_all(data_path)
