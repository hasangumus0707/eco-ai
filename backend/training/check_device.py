"""
Ortam kontrol scripti.

Çalıştırma (backend klasöründeyken):
    python -m training.check_device

PyTorch'un kurulu olduğunu, hangi donanımı kullanacağını ve
o donanım üzerinde gerçekten hesap yapabildiğini doğrular.
"""

import platform
import time

import torch
import torchvision

from app.utils.device import get_device


def main() -> None:
    print(f"İşletim sistemi : {platform.system()} {platform.machine()}")
    print(f"Python          : {platform.python_version()}")
    print(f"PyTorch         : {torch.__version__}")
    print(f"Torchvision     : {torchvision.__version__}")

    device = get_device()
    print(f"Seçilen donanım : {device}")

    # Küçük bir test: iki büyük matrisi çarp ve süreyi ölç.
    # Bu işlem sinir ağlarının temelindeki hesaplamanın ta kendisidir.
    a = torch.randn(2000, 2000, device=device)
    b = torch.randn(2000, 2000, device=device)
    start = time.perf_counter()
    for _ in range(10):
        c = a @ b
    _ = c.sum().item()  # .item() GPU'nun işini bitirmesini bekletir
    elapsed = time.perf_counter() - start

    print(f"Test hesaplaması: 10 matris çarpımı {elapsed:.3f} saniyede tamamlandı")
    print("✅ Ortam hazır!")


if __name__ == "__main__":
    main()
