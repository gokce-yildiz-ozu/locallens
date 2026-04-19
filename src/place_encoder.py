"""
Mekan description'larını sentence transformer ile encode eder.
Çıktı: data/embeddings.npy — her satır bir mekanın vektörü.
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

DATA_DIR = Path(__file__).parent.parent / "data"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def load_places(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def encode_descriptions(descriptions: list[str], model: SentenceTransformer) -> np.ndarray:
    # batch olarak göndermek tek tek göndermekten çok daha hızlı
    # show_progress_bar=True: 55 mekan için gerek yok ama alışkanlık olarak bıraktım
    embeddings = model.encode(descriptions, show_progress_bar=True, convert_to_numpy=True)
    return embeddings


def save_embeddings(embeddings: np.ndarray, path: Path) -> None:
    np.save(path, embeddings)
    print(f"Kaydedildi: {path}  |  shape: {embeddings.shape}")


def sanity_check(places: list[dict], embeddings: np.ndarray, model: SentenceTransformer) -> None:
    """İlk birkaç sorgu ile sistemin mantıklı sonuç verdiğini doğrular."""
    test_queries = [
        "sakin, yerel bir kahvaltı yeri",
        "Boğaz manzaralı romantik akşam yemeği",
        "koşu parkuru açık hava",
    ]

    print("\n--- Sanity Check ---")
    for query in test_queries:
        query_vec = model.encode(query, convert_to_numpy=True)

        # cosine similarity: iki vektörün nokta çarpımı / (büyüklükleri çarpımı)
        # normalize edilmiş vektörlerde bu sadece nokta çarpımına indirgenir
        norms = np.linalg.norm(embeddings, axis=1)
        query_norm = np.linalg.norm(query_vec)
        similarities = (embeddings @ query_vec) / (norms * query_norm)

        top3 = np.argsort(similarities)[::-1][:3]
        print(f"\nSorgu: '{query}'")
        for rank, idx in enumerate(top3, 1):
            print(f"  {rank}. {places[idx]['name']}  (score: {similarities[idx]:.3f})")


def main() -> None:
    places_path = DATA_DIR / "places.json"
    embeddings_path = DATA_DIR / "embeddings.npy"

    print("Mekanlar yükleniyor...")
    places = load_places(places_path)
    descriptions = [p["description"] for p in places]
    print(f"{len(descriptions)} mekan bulundu.")

    print(f"\nModel yükleniyor: {MODEL_NAME}")
    print("(İlk çalıştırmada ~120MB indirme yapılabilir)")
    model = SentenceTransformer(MODEL_NAME)

    print("\nDescription'lar encode ediliyor...")
    embeddings = encode_descriptions(descriptions, model)

    save_embeddings(embeddings, embeddings_path)
    sanity_check(places, embeddings, model)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    main()
