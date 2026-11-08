# Veri Seti

> Görseller boyut ve lisans nedeniyle **GitHub'a yüklenmez**. Uygulamayı yalnızca
> çalıştırmak isteyenlerin veri setine ihtiyacı yoktur, çünkü eğitilmiş model repoda bulunur.
> Veri setini sadece modeli yeniden eğitmek isteyenlerin indirmesi gerekir.

## Kaynak ve lisans

| | |
|---|---|
| **Ad** | Garbage Classification (12 classes) |
| **Yayınlayan** | Mostafa Mohamed (Kaggle: `mostafaabla`) |
| **Bağlantı** | https://www.kaggle.com/datasets/mostafaabla/garbage-classification |
| **Lisans** | Veritabanı: **Open Database License (ODbL)** · İçerik (görseller): **© Orijinal sahipleri** |
| **Boyut** | 15.515 görsel, 12 sınıf, ~250 MB |

**Lisansın bizim için anlamı:** Görsellerin telif hakkı orijinal sahiplerine aittir.
Bu yüzden görselleri repoda yeniden dağıtmıyoruz, yalnızca kaynağı gösteriyoruz.
Proje akademik ve ticari olmayan bir ders projesidir.

**Bilinen sınırlama:** Görseller internetten toplanmıştır. Çoğu temiz arka planlı ve
iyi ışıklı ürün fotoğraflarıdır. Gerçek hayattaki ezilmiş, kirli ya da kısmen görünen
atıklarda başarı daha düşük olabilir.

## Sınıf eşleştirmesi (12 → 5)

| Orijinal sınıf(lar) | Bizim sınıfımız | Gerekçe |
|---|---|---|
| plastic | **plastic** | doğrudan |
| metal | **metal** | doğrudan |
| paper, cardboard | **paper** | Kâğıt ve karton aynı geri dönüşüm akışına gider |
| brown-glass, green-glass, white-glass | **glass** | Renge göre ayırmaya gerek yok |
| battery, biological, clothes, shoes, trash | **other** | 4 geri dönüşüm sınıfının dışındaki nesneler. Modelin "bu bir atık sınıfı değil" demeyi öğrenmesi için kullanılır |

*Pil (battery) bilerek "other" sınıfına konmuştur. Pil tehlikeli atıktır ve metal kutusuna atılmamalıdır.*

## Temizleme adımları

`backend/training/prepare_dataset.py` scripti şunları yapar:

1. **Bozuk görsel kontrolü:** 0 bozuk görsel bulundu.
2. **Kopya temizleme:** 16 birebir kopya görsel atıldı. Kopyalar kalsaydı aynı resim hem eğitim hem test kümesine düşebilir ve başarı yapay olarak yüksek çıkardı.
3. **Çelişkili etiket temizleme:** 6 görsel atıldı. Bunlar aynı fotoğrafın hem plastic/metal hem white-glass klasöründe bulunduğu 3 durumdu.
4. **"other" dengeleme:** Orijinal 5 kaynak sınıf toplam ~9.900 görsel içeriyordu (yalnızca clothes 5.325). Her kaynaktan rastgele 400 görsel alındı, toplam 2.000.
5. **Katmanlı bölme:** Her sınıf kendi içinde %70 train / %15 val / %15 test olarak bölündü (seed = 42).

## Sonuç: sınıf dağılımı

| Sınıf | Train | Val | Test | Toplam |
|---|---:|---:|---:|---:|
| glass | 1395 | 299 | 299 | 1993 |
| metal | 538 | 115 | 115 | 768 |
| other | 1400 | 300 | 300 | 2000 |
| paper | 1359 | 291 | 291 | 1941 |
| plastic | 604 | 129 | 130 | 863 |
| **Toplam** | **5296** | **1134** | **1135** | **7565** |

⚠️ **Dengesizlik:** metal ve plastic sınıflarında diğerlerinin yaklaşık yarısı kadar örnek var.
Eğitimde **sınıf ağırlıklı kayıp fonksiyonu** (class-weighted loss) ile telafi edilecektir.
Tam sayılar `dataset/stats.json` dosyasındadır.

## Veriyi yeniden hazırlama

1. Zip'i Kaggle sayfasından indir (`archive.zip`).
2. `dataset/raw/` klasörüne aç. Sonuçta `dataset/raw/garbage_classification/<12 klasör>` oluşmalı.
3. `backend` klasöründe şu komutu çalıştır:
   ```bash
   python -m training.prepare_dataset
   ```

## Klasör yapısı

```
dataset/
  raw/garbage_classification/   ← Kaggle'dan gelen orijinal veri (dokunulmaz, git'e girmez)
  processed/                    ← script çıktısı (git'e girmez)
    train/{glass,metal,other,paper,plastic}/
    val/  {...}
    test/ {...}
  stats.json                    ← sınıf sayıları (git'e girer)
```
