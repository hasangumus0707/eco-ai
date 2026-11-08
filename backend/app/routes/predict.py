"""POST /predict – yüklenen görseli sınıflandırır."""

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.config import ALLOWED_CONTENT_TYPES, MAX_UPLOAD_BYTES
from app.schemas.prediction import ErrorResponse, PredictionResponse
from app.services.model_service import ModelService
from app.services.recycling_service import RecyclingService
from app.utils.image_validation import ImageValidationError, validate_and_load_image

router = APIRouter(tags=["Tahmin"])

MESSAGES = {
    "ok": "Atık başarıyla sınıflandırıldı.",
    "not_recyclable": "Bu görsel plastik, kâğıt, metal veya cam atık gibi görünmüyor. "
                      "Lütfen tek bir atığın net fotoğrafını yükleyin.",
    "low_confidence": "Bu görseli güvenilir şekilde sınıflandıramadım. "
                      "Atığı düz bir zemine koyup daha yakından ve iyi ışıkta tekrar çekmeyi deneyin.",
}


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}, 415: {"model": ErrorResponse}},
    summary="Atık fotoğrafını sınıflandır",
)
def predict(request: Request, file: UploadFile = File(..., description="JPG, PNG veya WEBP görsel (en fazla 10 MB)")):
    # Not: 'async def' yerine 'def' kullanıyoruz. FastAPI bu fonksiyonu ayrı bir iş parçacığında
    # çalıştırır; böylece model hesaplaması sunucunun diğer isteklerini kilitlemez.

    # 1) Tarayıcının bildirdiği tür (ilk eleme; asıl kontrol içerikten yapılır)
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(415, "Desteklenmeyen dosya türü. Lütfen JPG, PNG veya WEBP yükleyin.")

    # 2) Sınırdan 1 bayt fazla oku: dosya sınırı aşıyorsa tamamını belleğe almadan anlarız.
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"Dosya çok büyük. En fazla {MAX_UPLOAD_BYTES // (1024 * 1024)} MB yükleyebilirsiniz.")

    # 3) İçerik doğrulama
    try:
        image = validate_and_load_image(data)
    except ImageValidationError as exc:
        raise HTTPException(400, str(exc)) from exc

    # 4) Tahmin
    model: ModelService = request.app.state.model_service
    recycling: RecyclingService = request.app.state.recycling_service
    probabilities, decision = model.predict(image)

    # 5) Geri dönüşüm bilgisi yalnızca güvenilir tahminlerde verilir
    bin_info = recycling.get(decision.predicted_class) if decision.is_valid else None

    return PredictionResponse(
        predicted_class=decision.predicted_class,
        predicted_class_tr=recycling.name_tr(decision.predicted_class),
        confidence=round(decision.confidence, 4),
        probabilities=probabilities,
        is_valid_prediction=decision.is_valid,
        reason=decision.reason,
        message=MESSAGES[decision.reason],
        bin_name=bin_info.bin_name if bin_info else None,
        bin_color=bin_info.bin_color if bin_info else None,
        bin_color_hex=bin_info.bin_color_hex if bin_info else None,
        recycling_advice=bin_info.advice if bin_info else [],
        region_note=recycling.disclaimer,
        threshold=model.threshold,
    )
