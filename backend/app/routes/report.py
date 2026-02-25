from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.dataset import Dataset
from app.models.model_artifact import ModelArtifact
from app.services.file_service import read_csv
from app.services.report_service import generate_pdf_report


router = APIRouter(prefix="/report", tags=["Report"])


@router.get("/download-report/{model_id}")
def download_report(model_id: str, db: Session = Depends(get_db)):
    artifact = db.query(ModelArtifact).filter(ModelArtifact.id == model_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Model artifact not found.")

    dataset = db.query(Dataset).filter(Dataset.id == artifact.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = read_csv(dataset.file_path)
    payload = {
        "dataset_summary": {"rows": int(df.shape[0]), "columns": int(df.shape[1]), "columns_list": df.columns.tolist()},
        "eda_summary": {"missing_values": {col: int(v) for col, v in df.isna().sum().items()}},
        "model_comparison": artifact.all_metrics,
        "best_metrics": artifact.best_metrics,
        "feature_importance": artifact.feature_importance,
        "conclusion": f"Best model {artifact.best_model_name} selected for {artifact.problem_type}.",
    }
    file_name = f"{model_id}_report.pdf"
    report_path = generate_pdf_report(file_name, payload)

    if not Path(report_path).exists():
        raise HTTPException(status_code=500, detail="Report generation failed.")

    return FileResponse(
        path=report_path,
        media_type="application/pdf",
        filename=file_name,
    )
