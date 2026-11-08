"""
Yüklenen görsel için güvenlik ve geçerlilik kontrolleri.

Kullanıcıdan gelen her dosya potansiyel olarak tehlikelidir. Kontroller:
  1. Boyut sınırı        : 10 MB'tan büyük dosyalar reddedilir (sunucu belleğini korur)
  2. İçerik kontrolü     : Dosya UZANTISINA değil, gerçek İÇERİĞİNE bakılır.
                           "virus.exe" dosyasını "kedi.jpg" yapmak işe yaramaz.
  3. Bütünlük kontrolü   : Bozuk/yarım dosyalar reddedilir
  4. Piksel sınırı       : Küçük dosya boyutunda devasa çözünürlük ("decompression bomb")
                           bellek tüketme saldırılarını engeller
  5. Diske yazılmaz      : Görsel yalnızca bellekte işlenir, hiçbir geçici dosya oluşmaz.
"""

import io

from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import ALLOWED_FORMATS, MAX_IMAGE_PIXELS, MAX_UPLOAD_BYTES, MIN_IMAGE_SIDE

# Pillow'un kendi bomba korumasını da bizim sınırımıza ayarla
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


class ImageValidationError(ValueError):
    """Kullanıcıya gösterilebilecek, anlaşılır hata mesajı taşıyan istisna."""


def validate_and_load_image(data: bytes) -> Image.Image:
    """Ham baytları doğrular ve modele hazır bir RGB PIL görseline çevirir."""
    if not data:
        raise ImageValidationError("Dosya boş.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ImageValidationError(f"Dosya çok büyük. En fazla {MAX_UPLOAD_BYTES // (1024 * 1024)} MB yükleyebilirsiniz.")

    try:
        # 1. tur: yalnızca başlık ve bütünlük kontrolü (verify() görseli kullanılamaz hâle getirir)
        with Image.open(io.BytesIO(data)) as probe:
            fmt = probe.format
            probe.verify()
        if fmt not in ALLOWED_FORMATS:
            raise ImageValidationError("Desteklenmeyen dosya türü. Lütfen JPG, PNG veya WEBP yükleyin.")

        # 2. tur: gerçek yükleme
        image = Image.open(io.BytesIO(data))
        image.load()
    except ImageValidationError:
        raise
    except Image.DecompressionBombError:
        raise ImageValidationError("Görsel çözünürlüğü çok yüksek.")
    except (UnidentifiedImageError, OSError, SyntaxError):
        raise ImageValidationError("Dosya geçerli bir görsel değil veya bozuk.")

    if min(image.size) < MIN_IMAGE_SIDE:
        raise ImageValidationError(f"Görsel çok küçük (en az {MIN_IMAGE_SIDE}x{MIN_IMAGE_SIDE} piksel olmalı).")

    # Telefon fotoğrafları yönünü EXIF bilgisinde saklar; düzeltmezsek model yan yatmış görsel görür.
    image = ImageOps.exif_transpose(image)
    # Model 3 kanallı (RGB) görsel bekler; PNG saydamlığı ve paletli görseller dönüştürülür.
    return image.convert("RGB")
