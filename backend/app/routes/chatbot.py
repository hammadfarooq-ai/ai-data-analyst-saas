from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.dataset import Dataset
from app.models.model_artifact import ModelArtifact
from app.services.chat_service import answer_question
from app.services.file_service import read_csv


class ChatRequest(BaseModel):
    dataset_id: str
    question: str


router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


@router.post("")
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == payload.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    artifact = (
        db.query(ModelArtifact)
        .filter(ModelArtifact.dataset_id == dataset.id)
        .order_by(ModelArtifact.created_at.desc())
        .first()
    )
    df = read_csv(dataset.file_path)
    result = answer_question(df, payload.question, artifact.shap_summary if artifact else None)
    return {"question": payload.question, **result}
