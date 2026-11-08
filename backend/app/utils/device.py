"""
Donanım seçimi yardımcı modülü.

PyTorch hesaplamaları farklı donanımlarda yapabilir:
  - "mps"  : Apple Silicon (M1/M2/M3) Mac'lerin GPU'su  -> Hasan'ın MacBook'u
  - "cuda" : NVIDIA ekran kartı                          -> varsa Windows/Linux
  - "cpu"  : İşlemci (her bilgisayarda vardır)           -> yedek seçenek

Bu fonksiyon en hızlı kullanılabilir donanımı otomatik seçer.
Böylece aynı kod hem Mac'te hem Windows'ta değişiklik yapmadan çalışır.
"""

import torch


def get_device() -> torch.device:
    """Kullanılabilir en hızlı donanımı döndürür (MPS -> CUDA -> CPU)."""
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")
