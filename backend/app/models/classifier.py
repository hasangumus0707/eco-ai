"""
Model mimarisi: Transfer Learning ile atık sınıflandırıcı.

TRANSFER LEARNING NEDİR?
  Sıfırdan bir görüntü modeli eğitmek milyonlarca görsel ve günlerce GPU süresi ister.
  Bunun yerine ImageNet (1.2 milyon görsel, 1000 sınıf) üzerinde önceden eğitilmiş
  bir model alıyoruz. Bu model kenar, doku, şekil gibi genel görsel özellikleri
  zaten öğrenmiş durumda. Biz sadece:
    1. Son katmanı (1000 sınıflı "kafa") atıp yerine 5 sınıflı yeni bir katman koyuyoruz.
    2. Tüm ağı kendi verimizle kısa süre "ince ayar" (fine-tuning) yapıyoruz.
  Böylece ~7.500 görselle bile yüksek başarı elde edebiliyoruz.

Bu dosya hem eğitimde (training/train.py) hem de backend'de (tahmin) kullanılır.
"""

import torch
from torch import nn
from torchvision import models

# Sınıf sırası, torchvision ImageFolder'ın klasör adlarını alfabetik sıralamasıyla aynıdır.
# Modelin 0. çıkışı "glass", 1. çıkışı "metal", ... anlamına gelir.
CLASS_NAMES: list[str] = ["glass", "metal", "other", "paper", "plastic"]

SUPPORTED_ARCHS = ("mobilenet_v3_large", "resnet18")


def build_model(arch: str, num_classes: int = len(CLASS_NAMES), pretrained: bool = True) -> nn.Module:
    """
    İstenen mimariyi oluşturur ve son katmanını num_classes çıkışlı yapar.

    pretrained=True  -> ImageNet ağırlıkları indirilir (eğitim başlangıcı için)
    pretrained=False -> boş mimari (kendi .pth dosyamızı yükleyeceğimiz zaman)
    """
    if arch == "mobilenet_v3_large":
        # MobileNetV3: telefonlar için tasarlanmış, hafif (~5.4M parametre) ve hızlı.
        weights = models.MobileNet_V3_Large_Weights.IMAGENET1K_V2 if pretrained else None
        model = models.mobilenet_v3_large(weights=weights)
        # classifier = [Linear, Hardswish, Dropout(0.2), Linear(1280 -> 1000)]
        # Yalnızca son Linear katmanı değiştiriyoruz; Dropout overfitting'e karşı korur.
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Linear(in_features, num_classes)

    elif arch == "resnet18":
        # ResNet18: klasik, 18 katmanlı "artık bağlantılı" ağ (~11.7M parametre).
        weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        model = models.resnet18(weights=weights)
        in_features = model.fc.in_features
        # Orijinal ResNet18'de dropout yok; overfitting'i azaltmak için ekliyoruz.
        model.fc = nn.Sequential(nn.Dropout(p=0.3), nn.Linear(in_features, num_classes))

    else:
        raise ValueError(f"Desteklenmeyen mimari: {arch}. Seçenekler: {SUPPORTED_ARCHS}")

    return model


def load_checkpoint(path: str, device: torch.device) -> tuple[nn.Module, dict]:
    """
    Kaydedilmiş .pth dosyasından modeli yükler.
    Dönüş: (değerlendirme modunda model, checkpoint içindeki ek bilgiler)
    """
    # weights_only=True: dosyadan yalnızca tensör ve basit veri okunur,
    # rastgele Python kodu çalıştırılamaz (güvenlik önlemi).
    checkpoint = torch.load(path, map_location=device, weights_only=True)
    model = build_model(checkpoint["arch"], num_classes=len(checkpoint["class_names"]), pretrained=False)
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device).eval()
    return model, checkpoint
