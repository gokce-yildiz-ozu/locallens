# LocalLens — Proje Planı

## Proje Özeti

**Ne yapıyoruz:** İstanbul'da kullanıcının ilgi alanlarına ve ruh haline göre mekan öneren, embedding tabanlı bir semantic search sistemi.

**Neden yapıyoruz:** Klasik öneri sistemleri (TripAdvisor, Google Maps) popülerliğe göre sıralama yapar. Bu sistem, kullanıcının doğal dille ifade ettiği tercihleri ("sakin, yerel, Instagram'a uzak bir kahvaltı yeri") anlayıp semantik olarak eşleştirir.

**Ana değer önerisi:** Tourist trap'lerden kaçınma + kişiselleştirme.

---

## Hedefler

Bu projenin üç hedefi var ve **üçü birden tutulmalı**:

1. **Öğrenme** — Sentence transformers, embedding tabanlı retrieval, NLP pipeline'ları
2. **Portföy** — Master başvuruları için (AI/ML programları, Almanya/Hollanda, 2027 güzü)
3. **Kullanılabilir ürün** — Gerçekten çalışan, kendisinin de kullanabileceği bir MVP

---

## Kapsam (v0.1 — MVP)

### Dahil
- **Şehir:** İstanbul
- **Kategoriler:** Kafe, bar, gece kulübü, restoran, meyhane, manzara noktası, koşu/yürüyüş parkurları, müze
- **Veri:** Manuel olarak küratörlenmiş ~50-80 mekan (JSON dosyasında)
- **Core ML:** Sentence transformer ile embedding + cosine similarity retrieval
- **Arayüz:** Streamlit (basit ama fonksiyonel)
- **Kullanıcı deneyimi:** Doğal dille istek → top 5-10 mekan önerisi

### Dahil değil (şimdilik)
- Google Places / Foursquare API entegrasyonu
- Gerçek zamanlı veri güncelleme
- Kullanıcı hesapları / authentication
- Rota optimizasyonu
- Mobil uygulama
- Tourist trap classifier (v0.2'de eklenecek)

---

## Mimari

```
┌─────────────────────────────────────────────┐
│              Kullanıcı (Streamlit UI)        │
│   "Sakin, yerel, Boğaz manzaralı bir yer"   │
└───────────────────┬─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│           Query Encoder                      │
│   (sentence-transformers, pre-trained)       │
│   text → 384-dim vector                      │
└───────────────────┬─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│           Similarity Search                  │
│   cosine_sim(query_vec, place_vecs)          │
│   → top-k places                             │
└───────────────────┬─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│           Place Index (önceden hesaplanmış) │
│   places.json + embeddings.npy               │
└─────────────────────────────────────────────┘
```

---

## Faz Yapısı

Proje fazlara bölünmüş. Her faz sonunda **öğrenme checkpoint** var.

### Faz 0 — Kurulum ve Ortam
- Proje klasör yapısı
- `pyproject.toml` veya `requirements.txt`
- Git repo başlatma
- `.gitignore`
- `README.md` iskelet

**Checkpoint:** —

### Faz 1 — Veri Modeli ve Seed Data
- Mekan veri şemasını tasarla (hangi alanlar olacak?)
- `places.json` oluştur — 50-80 İstanbul mekanı
  - Her mekan için: id, ad, kategori, konum, açıklama (2-3 cümle), ruh hali tag'leri, fiyat seviyesi
  - **Açıklamalar önemli** — embedding bunlardan üretilecek
- Veri validation scripti

**Checkpoint:** Neden zengin text description'lar embedding kalitesi için kritik? Structured fields (kategori, fiyat) yetmez mi?

### Faz 2 — Embedding Pipeline
- Sentence transformer modelini seç ve yükle
- `place_encoder.py` — mekan description'larını embed eder
- `embeddings.npy` dosyasını oluştur ve kaydet
- Embedding'leri inspect etme scripti (similarity matrix, nearest neighbors)

**Checkpoint:**
- Cosine similarity nedir, neden euclidean değil?
- Pooling nedir, neden gerekli?
- `paraphrase-multilingual-MiniLM` yerine daha büyük model seçsek ne değişir?

### Faz 3 — Query ve Retrieval
- `retrieval.py` — kullanıcı sorgusunu embed et, top-k bul
- Filtering katmanı (kategori, fiyat gibi hard filter'lar)
- Debug mode: her sonucun neden seçildiğini göster (similarity score + hangi embedding bileşenleri)

**Checkpoint:**
- Semantic search vs keyword search farkı nedir?
- Hard filter mi re-ranking mi? Hangisi ne zaman?
- Binlerce mekan olsa FAISS gibi bir vector DB neden gerekirdi?

### Faz 4 — Streamlit UI
- Minimal, temiz arayüz
- Text input → sonuç listesi (kart görünümü)
- Filtre kontrolleri
- Debug panel (opsiyonel, "neden bu sonuç" göstergesi)

**Checkpoint:** —

### Faz 5 — Değerlendirme ve Analiz
- Manuel test set'i hazırla (20-30 sorgu + beklenen sonuçlar)
- Precision@k, recall@k hesapla
- Failure case analizi — nerede kötü çalışıyor, neden?

**Checkpoint:**
- Bu sistemi nasıl geliştirirdin? (fine-tuning, re-ranking, daha iyi veri?)
- Hangi metrikler bu problem için uygun, hangileri değil?

### Faz 6 — Dokümantasyon ve Polish
- README'yi tamamla (demo GIF, kurulum, kullanım)
- `LEARNING.md` review
- Kod temizliği, type hints
- (Opsiyonel) Deploy to Streamlit Cloud

---

## Teknik Kararlar ve Gerekçeleri

### Dil ve Framework
- **Python 3.12+** — ML ekosistemi, kullanıcının ana dili
- **PyTorch** (sentence-transformers üzerinden) — dolaylı kullanım, direkt yazmayacağız

### Model Seçimi (başlangıç)
- **`paraphrase-multilingual-MiniLM-L12-v2`**
  - Türkçe + İngilizce destekli (kullanıcı Türkçe ve İngilizce sorgu yapabilsin)
  - 384 boyutlu (küçük, hızlı)
  - CPU'da rahat çalışır
  - Başlangıç için ideal, sonra daha büyük model denenebilir

### Neden manuel veri?
- API entegrasyonu başta zaman öldürüyor ve ML öğrenme akışını bozuyor
- Kaliteli küçük veri > çöp büyük veri
- Embedding kalitesi test etmek için kontrolü sende olmalı

### Neden Streamlit?
- Prototip hızı çok yüksek
- Python-native, ekstra frontend bilgisi gerektirmez
- Deploy kolay

---

## Dosya Yapısı

```
locallens/
├── .venv/                    # virtual env (gitignore)
├── data/
│   ├── places.json           # seed mekan verisi
│   └── embeddings.npy        # hesaplanmış embedding'ler (gitignore)
├── src/
│   ├── __init__.py
│   ├── data_loader.py        # places.json okuma + validation
│   ├── place_encoder.py      # mekan description → embedding
│   ├── retrieval.py          # query → top-k places
│   └── utils.py
├── scripts/
│   ├── build_index.py        # embedding'leri offline hesapla
│   └── inspect_embeddings.py # debug/analiz
├── app.py                    # Streamlit UI
├── tests/
│   └── test_retrieval.py
├── requirements.txt
├── README.md
├── LEARNING.md               # öğrenme günlüğü
├── CLAUDE.md                 # Claude Code için direktifler
├── PROJECT_PLAN.md           # bu dosya
└── .gitignore
```

---

## Başarı Kriterleri

v0.1 bittiğinde:

- [ ] Streamlit'te "yerel, sakin, otantik bir kahvaltı yeri" gibi bir sorgu yapıp makul sonuçlar alabiliyorum
- [ ] Sonuçların neden geldiğini (similarity score ve açıklama) görebiliyorum
- [ ] LEARNING.md dolu ve okunduğunda embedding tabanlı retrieval'ın nasıl çalıştığı anlaşılıyor
- [ ] README.md bir başkasının projeyi çalıştırabilmesini sağlıyor
- [ ] Her modülün ne yaptığını ve neden öyle yazıldığını açıklayabiliyorum
- [ ] Faz sonu checkpoint sorularını cevaplayabiliyorum

---

## Sonraki Versiyonlar (v0.2+)

Buraya not alıyoruz, şimdi yapılmayacak:

- Tourist trap dedektörü (yorum verisi + classifier)
- Google Places / Foursquare API entegrasyonu
- Kullanıcı feedback'i ile re-ranking
- Rota optimizasyonu (TSP yaklaşık çözüm)
- Cross-encoder ile re-ranking
- Fine-tuning (eğer veri biriktirebilirsek)
