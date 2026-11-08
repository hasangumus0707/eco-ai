"""
Geri dönüşüm bilgisi servisi: kutu renkleri ve önerileri JSON dosyasından okur.

Renkler kodun içine gömülmedi; app/data/recycling_config.json dosyası düzenlenerek
farklı bir belediyenin uygulamasına uyarlanabilir.
"""

import json
from dataclasses import dataclass

from app.config import RECYCLING_CONFIG_PATH

OTHER_NAME_TR = "Tanımlanamadı"


@dataclass
class BinInfo:
    name_tr: str
    bin_name: str
    bin_color: str
    bin_color_hex: str
    advice: list[str]


class RecyclingService:
    def __init__(self) -> None:
        data = json.loads(RECYCLING_CONFIG_PATH.read_text(encoding="utf-8"))
        self.region: str = data["region"]
        self.disclaimer: str = data["disclaimer"]
        self.bins: dict[str, BinInfo] = {key: BinInfo(**value) for key, value in data["classes"].items()}

    def name_tr(self, class_name: str) -> str:
        info = self.bins.get(class_name)
        return info.name_tr if info else OTHER_NAME_TR

    def get(self, class_name: str) -> BinInfo | None:
        return self.bins.get(class_name)
