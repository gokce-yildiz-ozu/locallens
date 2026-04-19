"""
Kullanıcı sorgusunu alır, en alakalı mekanları döndürür.
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

DATA_DIR = Path(__file__).parent.parent / "data"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def load_index() -> tuple[list[dict], np.ndarray]:
    with open(DATA_DIR / "places.json", encoding="utf-8") as f:
        places = json.load(f)
    embeddings = np.load(DATA_DIR / "embeddings.npy")
    return places, embeddings


def search(
    query: str,
    places: list[dict],
    embeddings: np.ndarray,
    model: SentenceTransformer,
    top_k: int = 5,
    category: str | None = None,
    max_price: int | None = None,
    neighborhood: str | None = None,
) -> list[dict]:
    # hard filter önce: embedding hesaplamadan önce adayları daralt
    # bu sıra önemli — önce filtrele, sonra similarity hesapla
    candidates = list(range(len(places)))
    if category:
        candidates = [i for i in candidates if places[i]["category"] == category]
    if max_price:
        candidates = [i for i in candidates if places[i]["price_level"] <= max_price]
    if neighborhood:
        candidates = [i for i in candidates if places[i]["neighborhood"] == neighborhood]

    if not candidates:
        return []

    query_vec = model.encode(query, convert_to_numpy=True)
    candidate_embeddings = embeddings[candidates]

    # normalize edilmiş cosine similarity
    norms = np.linalg.norm(candidate_embeddings, axis=1)
    query_norm = np.linalg.norm(query_vec)
    similarities = (candidate_embeddings @ query_vec) / (norms * query_norm)

    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for rank_idx in top_indices:
        place_idx = candidates[rank_idx]
        results.append({
            **places[place_idx],
            "score": float(similarities[rank_idx]),
        })
    return results


def format_results(results: list[dict]) -> str:
    if not results:
        return "Sonuç bulunamadı."
    lines = []
    for i, r in enumerate(results, 1):
        price = "₺" * r["price_level"]
        lines.append(f"{i}. {r['name']} ({r['neighborhood']}) {price}  [{r['score']:.2f}]")
        lines.append(f"   {r['description'][:80]}...")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    print("Index yükleniyor...")
    places, embeddings = load_index()
    model = SentenceTransformer(MODEL_NAME)

    # interaktif test döngüsü
    print("Hazır. Çıkmak için 'q' yaz.\n")
    while True:
        query = input("Sorgu: ").strip()
        if query.lower() == "q":
            break
        if not query:
            continue
        results = search(query, places, embeddings, model)
        print("\n" + format_results(results))
