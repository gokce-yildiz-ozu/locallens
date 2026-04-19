import sys
sys.stdout.reconfigure(encoding="utf-8")

from sentence_transformers import SentenceTransformer
from src.retrieval import load_index, search, format_results

places, embeddings = load_index()
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

query = "deniz kenarı sakin kahvaltı"

print("=== Filtresiz ===")
results = search(query, places, embeddings, model)
print(format_results(results))

print("=== Sadece kafe/restoran ===")
kafe = search(query, places, embeddings, model, category="kafe")
restoran = search(query, places, embeddings, model, category="restoran")
combined = sorted(kafe + restoran, key=lambda x: x["score"], reverse=True)[:5]
print(format_results(combined))
