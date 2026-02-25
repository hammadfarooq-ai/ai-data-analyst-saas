from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.models.dataset import Dataset  # noqa: F401
from app.models.model_artifact import ModelArtifact  # noqa: F401
from app.routes.chatbot import router as chatbot_router
from app.routes.eda import router as eda_router
from app.routes.ml import router as ml_router
from app.routes.report import router as report_router
from app.routes.upload import router as upload_router
from app.services.file_service import ensure_storage_dirs


Base.metadata.create_all(bind=engine)
ensure_storage_dirs()

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix=settings.api_prefix)
app.include_router(eda_router, prefix=settings.api_prefix)
app.include_router(ml_router, prefix=settings.api_prefix)
app.include_router(report_router, prefix=settings.api_prefix)
app.include_router(chatbot_router, prefix=settings.api_prefix)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name}
