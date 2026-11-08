"""
API yanıt şemaları (Pydantic modelleri).

Pydantic, API'nin döndürdüğü JSON'un yapısını tanımlar ve doğrular.
FastAPI bu şemalardan otomatik dokümantasyon üretir: http://localhost:8000/docs
"""

from typing import Literal

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    predicted_class: str = Field(description="Modelin en yüksek olasılık verdiği sınıf (İngilizce)")
    predicted_class_tr: str = Field(description="Sınıfın Türkçe adı")
    confidence: float = Field(ge=0, le=1, description="Tahmin edilen sınıfın olasılığı (0-1)")
    probabilities: dict[str, float] = Field(description="Tüm sınıfların olasılıkları")
    is_valid_prediction: bool = Field(description="Sonuç güvenilir mi? False ise kesin sonuç gösterilmemeli")
    reason: Literal["ok", "not_recyclable", "low_confidence"]
    message: str = Field(description="Kullanıcıya gösterilecek açıklama")
    bin_name: str | None = Field(description="Önerilen kutu (geçersiz tahminde null)")
    bin_color: str | None = Field(description="Kutu rengi adı, ör. 'Sarı' (geçersiz tahminde null)")
    bin_color_hex: str | None
    recycling_advice: list[str]
    region_note: str = Field(description="Kutu renklerinin yerel uygulamaya göre değişebileceği uyarısı")
    threshold: float = Field(description="Kullanılan güven eşiği")


class ClassInfo(BaseModel):
    id: str
    name_tr: str
    bin_name: str
    bin_color: str
    bin_color_hex: str
    advice: list[str]


class ClassesResponse(BaseModel):
    classes: list[ClassInfo]
    region: str
    disclaimer: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model_loaded: bool
    model_arch: str
    model_file: str
    model_sha256: str = Field(description="Model dosyasının parmak izi (ilk 12 karakter); gerçek .pth'nin yüklendiğinin kanıtı")
    device: str
    confidence_threshold: float
    test_accuracy: float


class ErrorResponse(BaseModel):
    detail: str
