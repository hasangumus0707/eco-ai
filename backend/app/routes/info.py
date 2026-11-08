"""GET /health ve GET /classes – bilgi endpointleri."""

from fastapi import APIRouter, Request

from app.schemas.prediction import ClassesResponse, ClassInfo, HealthResponse
from app.services.model_service import ModelService
from app.services.recycling_service import RecyclingService

router = APIRouter(tags=["Bilgi"])


@router.get("/health", response_model=HealthResponse, summary="Backend ve model durumu")
def health(request: Request):
    model: ModelService = request.app.state.model_service
    return HealthResponse(
        status="ok",
        model_loaded=True,
        model_arch=model.arch,
        model_file=model.model_file,
        model_sha256=model.sha256,
        device=str(model.device),
        confidence_threshold=model.threshold,
        test_accuracy=model.test_accuracy,
    )


@router.get("/classes", response_model=ClassesResponse, summary="Desteklenen atık kategorileri")
def classes(request: Request):
    recycling: RecyclingService = request.app.state.recycling_service
    return ClassesResponse(
        classes=[ClassInfo(id=key, **vars(info)) for key, info in recycling.bins.items()],
        region=recycling.region,
        disclaimer=recycling.disclaimer,
    )
