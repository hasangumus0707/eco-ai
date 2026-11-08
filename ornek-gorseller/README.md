# Örnek Görseller (Gerçek Dünya Testi + Sunum Demosu)

Bu klasördeki fotoğraflar iki amaçla kullanılır:

1. **Gerçek dünya testi:** Model, Kaggle'daki temiz ürün fotoğraflarıyla eğitildi.
   Gerçek hayatta (evde, farklı ışıkta, karışık arka planda) çekilen fotoğraflarda
   ne kadar başarılı olduğunu bu fotoğraflarla ölçüyoruz.
2. **Sunum demosu:** Sunumda kamera çalışmazsa bu fotoğraflar yüklenerek demo yapılır.

## Klasörler

| Klasör | Ne konur? |
|---|---|
| `plastic/` | Pet şişe, plastik kap, deterjan kutusu… |
| `paper/` | Gazete, karton kutu, kâğıt… |
| `metal/` | Kola kutusu, konserve… |
| `glass/` | Cam şişe, kavanoz… |
| `other/` | Atık olmayan şeyler: insan, el, araba, yemek, telefon, hayvan… |

Her klasöre **5–10 fotoğraf** önerilir. Dosya adı önemli değildir (jpg, png, webp).

## ⚠️ Telif hakkı

GitHub reposu **herkese açık**. Bu klasöre yalnızca **kendi çektiğiniz** fotoğrafları koyun.
İnternetten bulunan görselleri test için kullanabilirsiniz ama repoya yüklemeyin; onları
`ornek-gorseller/_internet/` altına koyun (bu klasör git'e girmez).

## Testi çalıştırma

```bash
cd backend
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m training.evaluate_real
```

Sonuçlar `backend/reports/real_world/` klasörüne yazılır.
