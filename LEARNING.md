# LocalLens — Öğrenme Günlüğü

Bu dosya, proje boyunca öğrenilen teknik kavramların kaydını tutar.
Master başvurusu motivasyon mektubu yazarken buraya bak.

---

## Sentence Embedding (Cümle Gömme)

**Tarih:** 2026-04-20
**Faz:** Faz 2 — Embedding Pipeline

### Nedir?
Bir metni (kelime, cümle, paragraf) sabit boyutlu bir sayı vektörüne dönüştürme işlemi. Bu projede her mekan description'ı 384 sayılık bir listeye çevriliyor.

### Analoji
Renkleri RGB ile ifade etmek gibi. "Kırmızı" = (255, 0, 0), "Turuncu" = (255, 165, 0). Benzer renkler birbirine yakın sayılara sahip. Embedding'de de benzer anlamlı metinler birbirine yakın vektörlere sahip.

### Bu projede nerede kullanıldı?
`src/place_encoder.py` → `encode_descriptions()` fonksiyonu. 55 mekan description'ı → 55×384 numpy array.

### Kritik nokta
Embedding kelime saymaz, **anlam** yakalar. "Turistten uzak" ve "Instagram'a uzak" kelime olarak farklı ama vektör olarak yakın çıkabilir. Bu yüzden description zenginliği kritik.

### Daha derine inmek için
- [Sentence-Transformers dökümantasyonu](https://www.sbert.net/)
- [HuggingFace: paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)

---

## Cosine Similarity (Kosinüs Benzerliği)

**Tarih:** 2026-04-20
**Faz:** Faz 2 — Embedding Pipeline

### Nedir?
İki vektörün birbirine ne kadar "aynı yönü gösterdiğini" ölçer. 1.0 = aynı anlam, 0.0 = alakasız, -1.0 = zıt anlam.

### Analoji
İki pusula iğnesinin açısı gibi. Aynı yönü gösteriyorlarsa (açı = 0°) cosine = 1.0. Dik açıdaysa cosine = 0.0. Tam tersi yöndeyse cosine = -1.0.

### Bu projede nerede kullanıldı?
`src/place_encoder.py` → `sanity_check()` fonksiyonu. Sorgu vektörü ile her mekan vektörü arasındaki cosine similarity hesaplanıyor, en yüksek skorlu mekanlar öneriliyor.

### Kritik nokta
Neden Euclidean (düz mesafe) değil? Yüksek boyutlu uzaylarda (384 boyut) düz mesafe yanıltıcı olabiliyor — "curse of dimensionality". Cosine sadece yönü ölçtüğü için boyut sayısından etkilenmiyor.

### Daha derine inmek için
- [Wikipedia: Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
- [Why cosine similarity works for embeddings](https://www.sbert.net/examples/applications/semantic-search/README.html)

---

## Pooling (Havuzlama)

**Tarih:** 2026-04-20
**Faz:** Faz 2 — Embedding Pipeline

### Nedir?
Bir cümledeki her kelimenin ayrı bir vektörü var (token embedding). Pooling, bu kelime vektörlerini tek bir cümle vektörüne indirgeyen işlem. En yaygın yöntem: mean pooling (ortalamasını al).

### Analoji
Bir sınıftaki tüm öğrencilerin boy ortalamasını almak gibi. Tek tek boylar → bir sayı. Token vektörleri → bir cümle vektörü.

### Bu projede nerede kullanıldı?
Sentence-transformers kütüphanesi bunu otomatik yapıyor. `model.encode()` çağrısının arka planında her cümle için mean pooling uygulanıyor.

### Kritik nokta
Pooling yöntemi embedding kalitesini etkiler. Mean pooling en yaygın ve genellikle en iyi. Alternatifler: CLS token (BERT geleneği), max pooling. Sentence-transformers modelleri genellikle mean pooling için eğitilmiş.

### Daha derine inmek için
- [SBERT: Pooling Strategies](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)

---

## Precision@k (Değerlendirme Metriği)

**Tarih:** 2026-04-20
**Faz:** Faz 5 — Değerlendirme

### Nedir?
Sistemin döndürdüğü ilk k sonuç içinde kaç tanesinin gerçekten alakalı olduğunu ölçer. Precision@5 = 0.6 demek "5 sonuçtan 3'ü doğru" demek.

### Analoji
Bir arama motoruna sorgu yazdın, ilk 5 sonuca baktın. Kaçı işine yaradı? Bu sayıyı 5'e böl — Precision@5 bu.

### Bu projede nerede kullanıldı?
`tests/evaluate.py` — 12 manuel sorgu üzerinde test edildi. Başlangıç skoru 0.47, description iyileştirmeleri sonrası 0.53 oldu.

### Kritik nokta
Test setine göre veriyi optimize etmek **overfitting** sayılır. Eğer test sorguları için description yazarsak, gerçek kullanıcı sorgularında sistem yine başarısız olabilir. Değerlendirme ve geliştirme verisi ayrı tutulmalı.

### Daha derine inmek için
- [Information Retrieval Metrics](https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval))

---

## Veri Kalitesi vs Model Büyüklüğü

**Tarih:** 2026-04-20
**Faz:** Faz 5 — Değerlendirme

### Nedir?
ML'de sistemi geliştirmenin iki yolu: daha iyi model kullan veya daha iyi veri kullan. Çoğu zaman veri daha kolay kazanım sağlar.

### Analoji
Kötü malzemeyle iyi şef de iyi yemek yapamaz. Önce malzemeyi düzelt, sonra şef değiştir.

### Bu projede nerede kullanıldı?
3 mekanın description'ını zenginleştirdik → Precision@5 0.47'den 0.53'e çıktı. Model değişmedi, sadece veri iyileşti.

### Kritik nokta
"Daha büyük model" her zaman cevap değil. Bu projede baseline'ı geliştirmenin en kolay yolu daha zengin description yazmak.

---
