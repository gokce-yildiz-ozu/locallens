# LocalLens

İstanbul için embedding tabanlı semantik mekan öneri sistemi.

Doğal dille sorgu yap → ilgili mekanları bul.

> "sakin, yerel, Boğaz manzaralı bir kahvaltı yeri" → Kuzguncuk Bostanı, Bebek Kahvesi...

## Neden?

Google Maps popülerliğe göre sıralar. LocalLens, sorgunun **anlamını** anlayarak öneri yapar. "Instagram'a uzak" ile "turistten uzak" kelime olarak farklı ama sistem ikisini aynı kastı taşıyan ifadeler olarak eşleştirir.

## Nasıl Çalışır?

```
Kullanıcı sorgusu (doğal dil)
    → Sentence Transformer → 384 boyutlu vektör
    → Cosine similarity (önceden hesaplanmış mekan vektörleriyle)
    → Kategori / semt / fiyat filtreleri
    → Top-5 mekan önerisi
```

**Model:** `paraphrase-multilingual-MiniLM-L12-v2` — Türkçe ve İngilizce sorgular için.

**Veri:** 55 İstanbul mekanı, manuel küratörlenmiş (`data/places.json`). Kafe, restoran, bar, gece kulübü, meyhane, müze, park, koşu parkuru, manzara noktası kategorilerinde.

**Değerlendirme:** 12 sorgu üzerinde Precision@5 = 0.53 (baseline).

## Kurulum

```bash
git clone <repo-url>
cd locallens

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Kullanım

**1. Embedding'leri oluştur** (ilk kurulumda bir kez):

```bash
python -X utf8 src/place_encoder.py
```

İlk çalıştırmada model indirilir (~120MB).

**2. Uygulamayı başlat:**

```bash
streamlit run app.py
```

**3. (Opsiyonel) Değerlendirme:**

```bash
python -X utf8 tests/evaluate.py
```

## Proje Yapısı

```
locallens/
├── app.py                  # Streamlit arayüzü
├── data/
│   ├── places.json         # 55 İstanbul mekanı
│   └── embeddings.npy      # Önceden hesaplanmış vektörler
├── src/
│   ├── place_encoder.py    # Description → embedding pipeline
│   ├── retrieval.py        # Sorgu → top-k mekan
│   └── validate_data.py    # Veri şema doğrulama
├── tests/
│   ├── evaluate.py         # Precision@k değerlendirme
│   └── eval_queries.json   # Test sorgu seti
├── LEARNING.md             # Öğrenilen kavramlar günlüğü
└── requirements.txt
```

## Teknik Detaylar

- **Embedding:** Sentence Transformers ile mean pooling → 384 boyutlu vektör
- **Benzerlik:** Cosine similarity (yüksek boyutlu uzayda Euclidean'a göre daha güvenilir)
- **Filtreleme:** Hard filter (kategori, semt, fiyat) embedding hesabından önce uygulanır
- **Cache:** `@st.cache_resource` ile model bir kez yüklenir, her sorguda yeniden yüklenmez

## Proje Durumu

- [x] Faz 0 — Kurulum ve ortam
- [x] Faz 1 — Veri modeli ve seed data (55 mekan)
- [x] Faz 2 — Embedding pipeline
- [x] Faz 3 — Query ve retrieval
- [x] Faz 4 — Streamlit UI
- [x] Faz 5 — Değerlendirme (Precision@5 = 0.53)
- [x] Faz 6 — Dokümantasyon

## Sonraki Adımlar (v0.2)

- Daha fazla mekan verisi
- UI iyileştirmeleri
- Tourist trap classifier
- Google Places API entegrasyonu
