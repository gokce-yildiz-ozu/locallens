"""
Test seti üzerinde Precision@k hesaplar, başarısız sorguları raporlar.
"""

import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
from src.retrieval import load_index, search

K = 5


def precision_at_k(retrieved_ids: list[str], expected_ids: list[str], k: int) -> float:
    top_k = retrieved_ids[:k]
    hits = sum(1 for r in top_k if r in expected_ids)
    return hits / k


def main() -> None:
    eval_path = Path(__file__).parent / "eval_queries.json"
    with open(eval_path, encoding="utf-8") as f:
        queries = json.load(f)

    print("Index ve model yükleniyor...")
    places, embeddings = load_index()
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    scores = []
    failures = []

    print(f"\n{'─'*60}")
    for q in queries:
        results = search(q["query"], places, embeddings, model, top_k=K)
        retrieved_ids = [r["id"] for r in results]
        score = precision_at_k(retrieved_ids, q["expected"], K)
        scores.append(score)

        status = "✓" if score >= 0.4 else "✗"
        print(f"{status} [{score:.1f}] {q['query']}")

        if score < 0.4:
            failures.append({
                "query": q["query"],
                "score": score,
                "retrieved": [r["name"] for r in results],
                "expected": q["expected"],
            })

    print(f"{'─'*60}")
    avg = sum(scores) / len(scores)
    print(f"\nOrtalama Precision@{K}: {avg:.2f}  ({len(queries)} sorgu)")

    if failures:
        print(f"\n--- Başarısız sorgular ({len(failures)}) ---")
        for f in failures:
            print(f"\nSorgu: '{f['query']}'  [score: {f['score']:.1f}]")
            print(f"  Dönen : {f['retrieved']}")
            print(f"  Beklenen ID'ler: {f['expected']}")


if __name__ == "__main__":
    main()
