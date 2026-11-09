"""
Eğitim verisini PyTorch'a yükleyen yardımcılar.

Ana veri  : dataset/processed/{train,val,test}/<sınıf>/*.jpg  (Kaggle)
Ek veri   : dataset/extra/<kaynak>/{train,val}/<sınıf>/*.jpg  (TACO, Wikimedia Commons)

Ek veri yalnızca use_extra=True ile ve yalnızca train/val için kullanılır.
TEST kümesi her zaman sadece Kaggle test kümesidir. Böylece eski ve yeni model
aynı test sorularıyla, adil şekilde karşılaştırılır.
"""

from pathlib import Path

import torch
from torch.utils.data import ConcatDataset, DataLoader, Subset
from torchvision import datasets

from app.models.classifier import CLASS_NAMES
from app.utils.transforms import get_eval_transform, get_train_transform

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "dataset" / "processed"
EXTRA_DIR = PROJECT_ROOT / "dataset" / "extra"

# Eğitimde her ek kaynağın kaç kez gösterileceği.
# 2. tur: Commons cam görselleri (çoğu stüdyo/müze fotoğrafı, şeffaf şişe) 2 kez
# gösterildiğinde model "şeffaf şişe = cam" kısayolunu öğrendi ve şeffaf plastikleri
# cam sanmaya başladı. Bu yüzden Commons 1 kez, gerçek ortam (TACO) 2 kez gösterilir.
SOURCE_REPEAT = {"taco": 2, "commons": 1}
# Ek olarak tekrarlanan alt türler: şeffaf plastik şişeler toplam 2 + 2 = 4 kez görülür.
FOCUS_REPEAT = {"clear_plastic_bottle": 2}


class FixedClassFolder(datasets.ImageFolder):
    """
    Sınıf listesi klasörlerden değil, modelin sınıf listesinden (CLASS_NAMES) alınır.
    Ek veri kaynaklarında bazı sınıflar hiç yok (ör. Commons'ta 'paper' yok). Normal
    ImageFolder bu durumda sınıf numaralarını kaydırırdı ve 'cam' etiketi 'metal'
    olarak okunurdu. Bu sınıf numaraları her kaynakta aynı tutar.
    """

    def find_classes(self, directory):
        return list(CLASS_NAMES), {c: i for i, c in enumerate(CLASS_NAMES)}


class TargetSubset(Subset):
    """Bir veri kümesinin seçilen görselleri (etiket listesiyle birlikte)."""

    def __init__(self, dataset, indices: list[int]):
        super().__init__(dataset, indices)
        self.targets = [dataset.targets[i] for i in indices]
        self.root = f"{dataset.root} (alt küme: {len(indices)})"


class CombinedDataset(ConcatDataset):
    """Birden fazla klasörü tek veri kümesi gibi gösterir (ImageFolder ile aynı alanlar)."""

    def __init__(self, parts: list[datasets.ImageFolder]):
        super().__init__(parts)
        self.classes = list(CLASS_NAMES)
        self.targets = [t for p in parts for t in p.targets]
        self.sources = {str(p.root): len(p) for p in parts}


def extra_folders(split: str) -> list[Path]:
    """dataset/extra/<kaynak>/<split> klasörleri (varsa)."""
    if not EXTRA_DIR.exists():
        return []
    return sorted(d / split for d in EXTRA_DIR.iterdir() if (d / split).is_dir())


def make_dataset(split: str, use_extra: bool = False):
    """split: 'train', 'val' veya 'test'."""
    folder = DATA_DIR / split
    if not folder.exists():
        raise FileNotFoundError(
            f"{folder} bulunamadı. Önce şunu çalıştır: python -m training.prepare_dataset"
        )
    transform = get_train_transform() if split == "train" else get_eval_transform()
    # ImageFolder varsayılan olarak her görseli RGB'ye çevirir (paletli 'P' görseller dahil).
    ds = datasets.ImageFolder(folder, transform=transform)

    # Güvenlik kontrolü: klasör sırası modeldeki sınıf sırasıyla aynı olmalı,
    # yoksa model "cam" dediğinde biz "metal" anlarız.
    if ds.classes != CLASS_NAMES:
        raise ValueError(f"Sınıf sırası uyuşmuyor! Klasörler: {ds.classes}, beklenen: {CLASS_NAMES}")

    if not use_extra or split == "test":
        return ds
    parts = [ds]
    for d in extra_folders(split):
        extra = FixedClassFolder(d, transform=transform, allow_empty=True)
        if split != "train":  # doğrulamada tekrar yok: her görsel bir kez sayılır
            parts.append(extra)
            continue
        # Eğitimde gerçek ortam görselleri birkaç kez gösterilir (her seferinde farklı
        # augmentation ile). Aksi hâlde 5.296 Kaggle görselinin yanında az kalır.
        parts += [extra] * SOURCE_REPEAT.get(d.parent.name, 1)
        # Belirli alt türler (dosya adındaki TACO kategorisi) ek olarak tekrarlanır
        for key, times in FOCUS_REPEAT.items():
            idx = [i for i, (path, _) in enumerate(extra.samples) if key in Path(path).name]
            if idx:
                parts += [TargetSubset(extra, idx)] * times
    return CombinedDataset(parts)


def make_loader(split: str, batch_size: int = 32, num_workers: int = 4, use_extra: bool = False) -> DataLoader:
    """Veriyi küçük gruplar (batch) hâlinde modele besleyen DataLoader oluşturur."""
    ds = make_dataset(split, use_extra)
    return DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=(split == "train"),  # yalnızca eğitimde karıştır
        num_workers=num_workers,     # görselleri paralel okuyan işlem sayısı
        persistent_workers=num_workers > 0,
    )


def compute_class_weights(ds) -> torch.Tensor:
    """
    Dengesiz sınıflar için kayıp ağırlıkları.

    Az örneği olan sınıf (ör. metal: 538) daha büyük ağırlık alır; böylece model
    onu ihmal ettiğinde daha çok cezalandırılır. Formül: toplam / (sınıf_sayısı * sınıf_örnek_sayısı)
    """
    counts = torch.bincount(torch.tensor(ds.targets), minlength=len(ds.classes)).float()
    return counts.sum() / (len(counts) * counts)
