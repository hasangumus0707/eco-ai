# Gerçek Dünya Testi Sonuçları

Model: `mobilenet_v3_large` · Güven eşiği: 0.719 · Görsel sayısı: 48

| Gerçek sınıf | Görsel | ✅ Doğru | ⚠️ Emin değil (zararsız) | ❌ Yanlış (zararlı) |
|---|---:|---:|---:|---:|
| Plastik | 9 | 1 | 8 | 0 |
| Kâğıt | 7 | 4 | 2 | 1 |
| Metal | 11 | 4 | 5 | 2 |
| Cam | 8 | 7 | 1 | 0 |
| Diğer | 13 | 12 | 0 | 1 |
| **Toplam** | **48** | **28** | **16** | **4** |

- Doğru sonuç oranı: **%58.3**
- Zararlı hata oranı (yanlış kategoriyi kesin sonuç olarak gösterme): **%8.3**
- Atık görsellerinde eşik uygulanmadan en yüksek olasılığın doğru olma oranı: **%65.7**

> "Diğer" için doğru sonuç, sistemin kesin bir atık kategorisi göstermemesidir.
