"""
Uygulama ayarları.

Tüm sabit değerler burada toplanır; kod içinde "sihirli sayı" olmaz.
Bazı ayarlar ortam değişkeniyle (environment variable) değiştirilebilir,
böylece kodu değiştirmeden farklı bilgisayarlarda farklı ayar kullanılabilir.
"""

import json
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
WEIGHTS_DIR = BACKEND_DIR / "weights"
MODEL_CONFIG_PATH = WEIGHTS_DIR / "model_config.json"

# Geri dönüşüm kutusu renkleri ve önerileri. Belediyeye göre değişebileceği için
# ayrı bir JSON dosyasında tutulur; ECO_AI_RECYCLING_CONFIG ile başka dosya gösterilebilir.
RECYCLING_CONFIG_PATH = Path(
    os.getenv("ECO_AI_RECYCLING_CONFIG", Path(__file__).resolve().parent / "data" / "recycling_config.json")
)

# --- Yükleme güvenliği ---
MAX_UPLOAD_BYTES = 10 * 1024 * 1024        # 10 MB
MAX_IMAGE_PIXELS = 40_000_000              # ~40 megapiksel; "decompression bomb" saldırısına karşı
MIN_IMAGE_SIDE = 32                        # bundan küçük görsel anlamlı değil
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}  # Pillow'un dosya İÇERİĞİNDEN tespit ettiği format
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

# --- CORS: hangi web adresleri bu API'ye tarayıcıdan istek atabilir? ---
# Vite geliştirme sunucusu varsayılan olarak 5173 portunu kullanır.
CORS_ORIGINS = os.getenv(
    "ECO_AI_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")


def load_model_config() -> dict:
    """weights/model_config.json dosyasını okur (evaluate.py --deploy üretir)."""
    if not MODEL_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"{MODEL_CONFIG_PATH} bulunamadı. Model dosyaları eksik: "
            "'git pull' yaptığından emin ol veya modeli eğitip "
            "'python -m training.evaluate --arch mobilenet_v3_large --deploy' çalıştır."
        )
    return json.loads(MODEL_CONFIG_PATH.read_text(encoding="utf-8"))
