"""
Model servisi: eğitilmiş PyTorch modelini yükler ve tahmin yapar.

Model uygulama başlarken YALNIZCA BİR KEZ belleğe yüklenir (main.py -> lifespan).
Her istekte yeniden yüklemek hem yavaş hem de bellek israfı olurdu.
"""

import hashlib
import threading
from pathlib import Path

import torch
from PIL import Image

from app.config import WEIGHTS_DIR, load_model_config
from app.models.classifier import load_checkpoint
from app.utils.decision import Decision, decide
from app.utils.device import get_device
from app.utils.transforms import get_eval_transform


class ModelService:
    def __init__(self, model_file: str | None = None, threshold: float | None = None) -> None:
        """
        Varsayılan: weights/model_config.json'daki uygulama modeli.
        model_file / threshold verilirse başka bir aday model test edilebilir
        (ör. evaluate_real --model-file mobilenet_v3_large_v2.pth).
        """
        config = load_model_config()
        weights_path: Path = WEIGHTS_DIR / (model_file or config["model_file"])
        if not weights_path.exists():
            raise FileNotFoundError(f"Model dosyası bulunamadı: {weights_path}")

        self.device = get_device()
        self.model, checkpoint = load_checkpoint(str(weights_path), self.device)
        self.class_names: list[str] = checkpoint["class_names"]
        if self.class_names != config["class_names"]:
            raise ValueError("model_config.json ile .pth dosyasındaki sınıf listesi uyuşmuyor.")

        self.arch: str = checkpoint["arch"]
        self.threshold: float = float(threshold if threshold is not None else config["confidence_threshold"])
        self.test_accuracy: float = float(config.get("test_accuracy", 0.0))
        self.model_file: str = weights_path.name
        # Dosyanın parmak izi: /health'te gösterilir; çalışan modelin gerçekten bu .pth olduğunu kanıtlar.
        self.sha256: str = hashlib.sha256(weights_path.read_bytes()).hexdigest()[:12]
        self.transform = get_eval_transform()
        # Aynı anda gelen istekler modeli paralel kullanmasın (GPU/MPS için daha güvenli).
        self._lock = threading.Lock()

    @torch.no_grad()  # tahmin sırasında gradyan hesaplamaya gerek yok -> daha hızlı, daha az bellek
    def predict(self, image: Image.Image) -> tuple[dict[str, float], Decision]:
        """RGB görseli alır; (sınıf olasılıkları, karar) döndürür."""
        tensor = self.transform(image).unsqueeze(0).to(self.device)  # [1, 3, 224, 224]
        with self._lock:
            logits = self.model(tensor)
        probs = torch.softmax(logits, dim=1)[0].cpu().tolist()
        probabilities = {name: round(p, 4) for name, p in zip(self.class_names, probs)}
        return probabilities, decide(probabilities, self.threshold)
