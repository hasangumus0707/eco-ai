"""
Tahmin karar kuralı: model sonucunu ne zaman "güvenilir" kabul ediyoruz?

NEDEN GEREKLİ?
  Softmax çıktıları her zaman toplamı 1 olan olasılıklardır. Model hiç görmediği
  bir araba fotoğrafı için bile "%70 metal" diyebilir. Yüksek güven skoru, görselin
  gerçekten atık olduğunu KANITLAMAZ. Bu yüzden iki katmanlı bir kontrol uyguluyoruz:

  KATMAN 1 – "other" sınıfı:
    Model eğitimde kıyafet, ayakkabı, yemek artığı, pil ve karışık çöp görselleriyle
    "bunlar 4 geri dönüşüm sınıfından biri değil" demeyi öğrendi.
    En yüksek olasılık "other" ise -> sonuç geçersiz.

  KATMAN 2 – güven eşiği:
    En yüksek olasılık bir atık sınıfına ait ama eşiğin altındaysa -> "emin değilim".
    Eşik uydurulmaz; evaluate.py doğrulama verisinden hesaplar ve
    weights/model_config.json dosyasına yazar.

SINIRLAR (dürüst olmak gerekirse):
  - Model insan, araba, hayvan gibi nesneleri eğitimde hiç görmedi. "other" sınıfı
    bunları çoğu zaman yakalar ama garanti veremez. Parlak, silindirik bir nesne
    (ör. termos) "metal" sanılabilir.
  - Eşik yükseldikçe yanlış sonuç azalır ama doğru atıkların bir kısmı da reddedilir.
    Bu bir ödünleşimdir (trade-off).
"""

from dataclasses import dataclass

OTHER_CLASS = "other"


@dataclass
class Decision:
    predicted_class: str      # en yüksek olasılıklı sınıf
    confidence: float         # o sınıfın olasılığı (0-1)
    is_valid: bool            # sonucu kullanıcıya kesin olarak gösterebilir miyiz?
    reason: str               # "ok" | "not_recyclable" | "low_confidence"


def decide(probabilities: dict[str, float], threshold: float) -> Decision:
    """Sınıf olasılıklarından nihai kararı üretir."""
    predicted = max(probabilities, key=probabilities.__getitem__)
    confidence = probabilities[predicted]

    if predicted == OTHER_CLASS:
        return Decision(predicted, confidence, False, "not_recyclable")
    if confidence < threshold:
        return Decision(predicted, confidence, False, "low_confidence")
    return Decision(predicted, confidence, True, "ok")
