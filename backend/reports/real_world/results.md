# Gerçek Dünya Testi Sonuçları

Model: `mobilenet_v3_large` · Güven eşiği: 0.823 · Görsel sayısı: 48

| Gerçek sınıf | Görsel | ✅ Doğru | ⚠️ Emin değil (zararsız) | ❌ Yanlış (zararlı) |
|---|---:|---:|---:|---:|
| Plastik | 9 | 4 | 5 | 0 |
| Kâğıt | 7 | 3 | 3 | 1 |
| Metal | 11 | 5 | 6 | 0 |
| Cam | 8 | 6 | 2 | 0 |
| Diğer | 13 | 13 | 0 | 0 |
| **Toplam** | **48** | **31** | **16** | **1** |

- Doğru sonuç oranı: **%64.6**
- Zararlı hata oranı (yanlış kategoriyi kesin sonuç olarak gösterme): **%2.1**
- Atık görsellerinde eşik uygulanmadan en yüksek olasılığın doğru olma oranı: **%60.0**

> "Diğer" için doğru sonuç, sistemin kesin bir atık kategorisi göstermemesidir.
