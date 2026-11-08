"""
ECO AI – FastAPI uygulamasının giriş noktası.

Çalıştırma (backend klasöründeyken, sanal ortam aktifken):
    uvicorn app.main:app --reload

Sonra tarayıcıda:
    http://localhost:8000/docs    -> otomatik API dokümantasyonu (buradan deneme yapılabilir)
    http://localhost:8000/health  -> durum kontrolü
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routes import info, predict
from app.services.model_service import ModelService
from app.services.recycling_service import RecyclingService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("eco-ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Uygulama açılırken bir kez çalışır: modeli belleğe yükler.
    'yield'den sonrası uygulama kapanırken çalışır.
    """
    logger.info("Model yükleniyor...")
    app.state.model_service = ModelService()
    app.state.recycling_service = RecyclingService()
    m = app.state.model_service
    logger.info(f"✅ Model hazır: {m.arch} | dosya: {m.model_file} (sha256 {m.sha256}) | "
                f"donanım: {m.device} | eşik: {m.threshold}")
    yield
    logger.info("Uygulama kapanıyor.")


app = FastAPI(
    title="ECO AI – Akıllı Geri Dönüşüm Asistanı API",
    description="Atık fotoğraflarını PyTorch (MobileNetV3, transfer learning) modeli ile sınıflandırır.",
    version="1.0.0",
    lifespan=lifespan,
)

# Frontend (localhost:5173) farklı bir portta çalıştığı için tarayıcının
# bu API'ye istek atmasına izin vermemiz gerekir (CORS).
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(info.router)
app.include_router(predict.router)


@app.get("/", include_in_schema=False)
def root():
    return {"message": "ECO AI API çalışıyor. Dokümantasyon için /docs adresine gidin."}
