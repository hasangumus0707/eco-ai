# Örnek Görseller (Gerçek Dünya Testi + Sunum Demosu)

Bu klasördeki fotoğraflar iki amaçla kullanılır:

1. **Gerçek dünya testi:** Model, Kaggle'daki temiz ürün fotoğraflarıyla eğitildi.
   Gerçek hayatta (farklı ışıkta, karışık arka planda, ezilmiş/kirli hâlde) çekilen
   fotoğraflarda ne kadar başarılı olduğunu bu fotoğraflarla ölçüyoruz.
2. **Sunum demosu:** Sunumda kamera çalışmazsa bu fotoğraflar yüklenerek demo yapılır.

## Klasörler

| Klasör | İçerik | Görsel |
|---|---|---:|
| `plastic/` | Pet şişe, plastik kap, şişe yığınları | 9 |
| `paper/` | Karton kutu, gazete, buruşuk kâğıt, kâğıt torba | 7 |
| `metal/` | İçecek kutusu, konserve, ezilmiş kutular | 11 |
| `glass/` | Cam şişe, bira/şarap şişesi | 8 |
| `other/` | Atık olmayan şeyler: insan, kedi, köpek, araba, yemek, telefon, ağaç | 13 |

## Kaynak ve lisans

Görsellerin tamamı **Wikimedia Commons**'tan alınmıştır ve açık lisanslıdır
(CC0, kamu malı, CC BY, CC BY-SA). Fotoğraflar bu projeye ait değildir. Her görselin yazarı,
lisansı ve kaynak bağlantısı **[`KAYNAKLAR.md`](KAYNAKLAR.md)** dosyasındadır
(makine okunabilir sürümü: `KAYNAKLAR.csv`).

**Yeni fotoğraf eklerken:** Repo herkese açık olduğu için yalnızca kendi çektiğiniz ya da
açık lisanslı fotoğrafları koyun. Açık lisanslı bir görsel eklerseniz `KAYNAKLAR.md`'ye satır ekleyin.
Lisansı belirsiz görselleri yalnızca yerel test için `ornek-gorseller/_internet/<sınıf>/` altına
koyun. Bu klasör git'e girmez ama test scripti onu da tarar.

## Testi çalıştırma

```bash
cd backend
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m training.evaluate_real
```

Sonuçlar `backend/reports/real_world/` klasörüne yazılır.
