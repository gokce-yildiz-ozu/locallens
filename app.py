import sys
import streamlit as st
from sentence_transformers import SentenceTransformer
from src.retrieval import load_index, search

sys.stdout.reconfigure(encoding="utf-8")

CATEGORIES = ["Hepsi", "kafe", "restoran", "bar", "gece kulübü", "meyhane", "müze", "park", "koşu_parkuru", "manzara"]


def get_neighborhoods(places: list[dict]) -> list[str]:
    return ["Hepsi"] + sorted(set(p["neighborhood"] for p in places))


# model ve index her sorguda yeniden yüklenmez — bir kez belleğe alınır
@st.cache_resource
def load_model_and_index():
    places, embeddings = load_index()
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return places, embeddings, model


st.title("LocalLens")
st.caption("İstanbul için semantik mekan öneri sistemi")

places, embeddings, model = load_model_and_index()

query = st.text_input("Ne arıyorsun?", placeholder="sakin, yerel, Boğaz manzaralı bir kahvaltı yeri...")

col1, col2, col3 = st.columns(3)
with col1:
    category_label = st.selectbox("Kategori", CATEGORIES)
with col2:
    max_price = st.selectbox("Maksimum fiyat", [4, 1, 2, 3], format_func=lambda x: "₺" * x)
with col3:
    neighborhood_label = st.selectbox("Semt", get_neighborhoods(places))

if st.button("Ara", type="primary") and query.strip():
    category = None if category_label == "Hepsi" else category_label
    neighborhood = None if neighborhood_label == "Hepsi" else neighborhood_label

    results = search(query, places, embeddings, model, top_k=5, category=category, max_price=max_price, neighborhood=neighborhood)

    if not results:
        st.warning("Sonuç bulunamadı. Filtreleri gevşet veya sorguyu değiştir.")
    else:
        for r in results:
            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.subheader(r["name"])
                    st.caption(f"{r['neighborhood']}  ·  {'₺' * r['price_level']}  ·  {r['category']}")
                with col_b:
                    st.metric("Benzerlik", f"{r['score']:.2f}")
                st.write(r["description"])
                st.write(" ".join(f"`{t}`" for t in r["tags"]))
