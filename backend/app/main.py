import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.session import init_db
from app.api.endpoints import router as api_router

# Ensure necessary directories exist
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
sample_dir = Path(settings.SAMPLE_DIR)
if not sample_dir.exists():
    sample_dir = settings.BASE_DIR / "data" / "samples"
sample_dir.mkdir(parents=True, exist_ok=True)

# Run database creation on startup
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Pre-warm AI detector model so inference is immediate on first upload
    try:
        from app.services.image_analysis.ai_detector import get_ai_detector
        detector = get_ai_detector()
        if detector.is_available():
            print(f"[TRUTHLENS] AI Authenticity Detector initialized: {detector.model_name}")
        else:
            print(f"[TRUTHLENS] AI Detector warning: {detector.get_load_error()}")
    except Exception as e:
        print(f"[TRUTHLENS] AI Detector pre-warm exception: {e}")
    yield

app = FastAPI(
    title="TRUTHLENS — AI Image Authenticity Detector API",
    description="FastAPI Backend for Pretrained AI-Generated vs Real Image Classification",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file routes for image serving
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")
app.mount("/samples", StaticFiles(directory=str(sample_dir)), name="samples")

# Include API Router at both /api and /api/v1 for maximum client compatibility
app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "platform": "TRUTHLENS — See Beyond the Image",
        "status": "online",
        "api_docs": "/docs",
        "version": "1.0.0"
    }
