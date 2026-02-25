from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.routes.report import download_report
from app.schemas.ml import PredictRequest, PredictResponse
from app.services.predict_service import run_prediction


router = APIRouter(tags=["Public Aliases"])


@router.post("/predict", response_model=PredictResponse)
def predict_alias(payload: PredictRequest):
    return PredictResponse(**run_prediction(payload.model_id, payload.record))


@router.get("/download-report")
def download_report_alias(model_id: str, db: Session = Depends(get_db)) -> FileResponse:
    return download_report(model_id=model_id, db=db)
