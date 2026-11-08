"""
Eğitim verisini PyTorch'a yükleyen yardımcılar.

dataset/processed/{train,val,test}/<sınıf>/*.jpg yapısındaki klasörleri okur.
torchvision'ın ImageFolder sınıfı klasör adını otomatik olarak etiket yapar.
"""

from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision import datasets

from app.models.classifier import CLASS_NAMES
from app.utils.transforms import get_eval_transform, get_train_transform

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "dataset" / "processed"


def make_dataset(split: str) -> datasets.ImageFolder:
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
    return ds


def make_loader(split: str, batch_size: int = 32, num_workers: int = 4) -> DataLoader:
    """Veriyi küçük gruplar (batch) hâlinde modele besleyen DataLoader oluşturur."""
    ds = make_dataset(split)
    return DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=(split == "train"),  # yalnızca eğitimde karıştır
        num_workers=num_workers,     # görselleri paralel okuyan işlem sayısı
        persistent_workers=num_workers > 0,
    )


def compute_class_weights(ds: datasets.ImageFolder) -> torch.Tensor:
    """
    Dengesiz sınıflar için kayıp ağırlıkları.

    Az örneği olan sınıf (ör. metal: 538) daha büyük ağırlık alır; böylece model
    onu ihmal ettiğinde daha çok cezalandırılır. Formül: toplam / (sınıf_sayısı * sınıf_örnek_sayısı)
    """
    counts = torch.bincount(torch.tensor(ds.targets), minlength=len(ds.classes)).float()
    return counts.sum() / (len(counts) * counts)
