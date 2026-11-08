"""
Görsel ön işleme (preprocessing) adımları.

Bir sinir ağı ham fotoğrafı doğrudan anlayamaz; görselin
  1. sabit bir boyuta getirilmesi (224x224 piksel),
  2. sayılara (tensöre) çevrilmesi,
  3. normalize edilmesi gerekir.

NORMALİZASYON: Her renk kanalından (R, G, B) ImageNet ortalaması çıkarılıp
standart sapmaya bölünür. Önceden eğitilmiş model bu ölçekteki sayılara alışık
olduğu için aynı dönüşümü uygulamak zorundayız.

Eğitim ve tahmin AYNI eval dönüşümünü kullanmalıdır; bu yüzden tek bir yerde tanımlı.
"""

from torchvision import transforms

IMG_SIZE = 224
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def get_train_transform() -> transforms.Compose:
    """
    Eğitim dönüşümü + DATA AUGMENTATION (veri çoğaltma).

    Her epoch'ta aynı görsel biraz farklı (kırpılmış, çevrilmiş, döndürülmüş,
    farklı ışıkta) gösterilir. Model böylece "bu şişe tam bu açıda" diye
    ezberlemek yerine "şişe neye benzer" sorusunu öğrenir -> overfitting azalır.
    """
    return transforms.Compose([
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.7, 1.0)),  # rastgele yakınlaştır/kırp
        transforms.RandomHorizontalFlip(),                          # yatay ayna
        transforms.RandomRotation(15),                              # ±15° döndür
        transforms.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.25),  # ışık farkları
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])


def get_eval_transform() -> transforms.Compose:
    """Doğrulama, test ve gerçek tahmin için dönüşüm (rastgelelik YOK)."""
    return transforms.Compose([
        transforms.Resize(256),          # kısa kenarı 256 yap (en-boy oranı korunur)
        transforms.CenterCrop(IMG_SIZE),  # ortadan 224x224 kes
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
