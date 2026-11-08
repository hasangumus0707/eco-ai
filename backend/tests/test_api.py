"""
API testleri.

Çalıştırma (backend klasöründeyken):
    python -m pytest -v

Gerçek model yüklenir; sahte (mock) model KULLANILMAZ.
Veri seti bilgisayarda varsa gerçek test görselleriyle de doğruluk kontrolü yapılır.
"""

import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

TEST_IMAGES_DIR = Path(__file__).resolve().parents[2] / "dataset" / "processed" / "test"
EXPECTED_KEYS = {"predicted_class", "predicted_class_tr", "confidence", "probabilities",
                 "bin_color", "recycling_advice", "is_valid_prediction"}


@pytest.fixture(scope="module")
def client():
    # 'with' bloğu lifespan'i tetikler -> model bir kez yüklenir
    with TestClient(app) as c:
        yield c


def make_image(fmt: str = "JPEG", size=(300, 300), color=(120, 160, 90)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format=fmt)
    return buf.getvalue()


# ---------- Bilgi endpointleri ----------

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["model_file"] == "eco_ai_model.pth"
    assert body["model_arch"] == "mobilenet_v3_large"
    assert 0.5 <= body["confidence_threshold"] <= 0.95


def test_classes(client):
    r = client.get("/classes")
    assert r.status_code == 200
    ids = {c["id"] for c in r.json()["classes"]}
    assert ids == {"plastic", "paper", "metal", "glass"}
    assert r.json()["disclaimer"]  # yerel kural uyarısı boş olmamalı


# ---------- /predict: yanıt yapısı ----------

def test_predict_response_shape(client):
    r = client.post("/predict", files={"file": ("x.jpg", make_image(), "image/jpeg")})
    assert r.status_code == 200
    body = r.json()
    assert EXPECTED_KEYS <= body.keys()
    assert abs(sum(body["probabilities"].values()) - 1) < 0.01
    assert set(body["probabilities"]) == {"glass", "metal", "other", "paper", "plastic"}


@pytest.mark.parametrize("fmt,mime", [("PNG", "image/png"), ("WEBP", "image/webp")])
def test_predict_other_formats(client, fmt, mime):
    r = client.post("/predict", files={"file": (f"x.{fmt.lower()}", make_image(fmt), mime)})
    assert r.status_code == 200


# ---------- /predict: güvenlik kontrolleri ----------

def test_rejects_wrong_content_type(client):
    r = client.post("/predict", files={"file": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 415


def test_rejects_fake_image(client):
    """Uzantısı ve türü jpg görünen ama içi görsel olmayan dosya."""
    r = client.post("/predict", files={"file": ("fake.jpg", b"bu bir resim degil" * 50, "image/jpeg")})
    assert r.status_code == 400


def test_rejects_unsupported_real_format(client):
    """Gerçek bir görsel ama izin verilmeyen formatta (GIF), jpeg gibi gönderilmiş."""
    r = client.post("/predict", files={"file": ("x.jpg", make_image("GIF"), "image/jpeg")})
    assert r.status_code == 400


def test_rejects_too_large(client):
    big = b"\xff\xd8" + b"0" * (10 * 1024 * 1024 + 10)
    r = client.post("/predict", files={"file": ("big.jpg", big, "image/jpeg")})
    assert r.status_code == 413


def test_rejects_tiny_image(client):
    r = client.post("/predict", files={"file": ("t.png", make_image("PNG", size=(10, 10)), "image/png")})
    assert r.status_code == 400


def test_rejects_empty(client):
    r = client.post("/predict", files={"file": ("e.jpg", b"", "image/jpeg")})
    assert r.status_code == 400


# ---------- Gerçek model kontrolü ----------

@pytest.mark.skipif(not TEST_IMAGES_DIR.exists(), reason="Veri seti bu bilgisayarda yok")
def test_real_images_are_classified_correctly(client):
    """
    Her sınıftan 10 gerçek test görseli gönderilir. Model gerçekten eğitilmiş ve
    doğru yüklenmişse büyük çoğunluğu doğru bilinmelidir. Rastgele bir model
    5 sınıfta ~%20 doğruluk verir; bu test onu yakalar.
    """
    correct = total = 0
    for class_dir in sorted(TEST_IMAGES_DIR.iterdir()):
        for img_path in sorted(class_dir.iterdir())[:10]:
            mime = "image/png" if img_path.suffix.lower() == ".png" else "image/jpeg"
            r = client.post("/predict", files={"file": (img_path.name, img_path.read_bytes(), mime)})
            assert r.status_code == 200
            correct += r.json()["predicted_class"] == class_dir.name
            total += 1
    assert correct / total >= 0.85, f"Doğruluk beklenenden düşük: {correct}/{total}"


def test_invalid_prediction_has_no_bin(client):
    """Geçersiz tahminlerde kutu önerisi verilmemeli."""
    r = client.post("/predict", files={"file": ("x.jpg", make_image(color=(0, 0, 0)), "image/jpeg")})
    body = r.json()
    if not body["is_valid_prediction"]:
        assert body["bin_color"] is None
        assert body["recycling_advice"] == []
