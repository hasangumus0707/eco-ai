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
    # v2 (gerçek dünya ince ayarı): telefon fotoğraflarına benzesin diye daha güçlü
    # kırpma, ışık/renk değişimi, ara sıra bulanıklık ve gri tonlama eklendi.
    return transforms.Compose([
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.5, 1.0)),  # rastgele yakınlaştır/kırp
        transforms.RandomHorizontalFlip(),                          # yatay ayna
        transforms.RandomRotation(20),                              # ±20° döndür
        transforms.ColorJitter(brightness=0.35, contrast=0.35, saturation=0.35, hue=0.03),  # ışık farkları
        transforms.RandomApply([transforms.GaussianBlur(5, sigma=(0.1, 2.0))], p=0.2),  # odak kayması
        transforms.RandomGrayscale(p=0.05),
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
