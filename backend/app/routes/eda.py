from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.dataset import Dataset
from app.schemas.eda import EDAResponse
from app.schemas.ml import TargetDetectionResponse
from app.services.eda_service import build_eda_payload
from app.services.file_service import read_csv
from app.services.target_service import detect_target_column


router = APIRouter(prefix="/eda", tags=["EDA"])


@router.get("/{dataset_id}", response_model=EDAResponse)
def get_eda(dataset_id: str, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    df = read_csv(dataset.file_path)
    payload = build_eda_payload(df)
    return EDAResponse(**payload)


@router.get("/detect-target/{dataset_id}", response_model=TargetDetectionResponse)
def detect_target(dataset_id: str, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    df = read_csv(dataset.file_path)
    detected_target, problem_type, candidates, reason = detect_target_column(df)
    return TargetDetectionResponse(
        detected_target=detected_target,
        problem_type=problem_type,
        candidates=candidates,
        reason=reason,
    )
