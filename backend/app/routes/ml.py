from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.dataset import Dataset
from app.models.model_artifact import ModelArtifact
from app.schemas.ml import ExplainResponse, PredictRequest, PredictResponse, TrainRequest, TrainResponse
from app.services.file_service import read_csv
from app.services.predict_service import load_model_bundle, run_prediction
from app.services.target_service import detect_target_column
from app.services.training_service import train_and_select_model


router = APIRouter(prefix="/ml", tags=["ML"])


@router.post("/train", response_model=TrainResponse)
def train_model(payload: TrainRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == payload.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = read_csv(dataset.file_path)
    target_column = payload.target_column
    problem_type = None
    if not target_column:
        detected_target, problem_type, _, _ = detect_target_column(df)
        target_column = detected_target
    if not target_column:
        raise HTTPException(status_code=400, detail="Unable to detect target column. Please provide manually.")
    if target_column not in df.columns:
        raise HTTPException(status_code=400, detail="Provided target column does not exist.")

    if not problem_type:
        series = df[target_column]
        problem_type = "classification" if series.nunique(dropna=True) <= 10 else "regression"

    result = train_and_select_model(df, target_column, problem_type)
    artifact = ModelArtifact(
        id=result["model_id"],
        dataset_id=dataset.id,
        target_column=target_column,
        problem_type=problem_type,
        best_model_name=result["best_model_name"],
        model_path=result["model_path"],
        all_metrics=result["all_metrics"],
        best_metrics=result["best_metrics"],
        feature_importance=result["feature_importance"],
        shap_summary=result["shap_summary"],
        confidence_score=result["confidence_score"],
    )
    db.add(artifact)
    db.commit()

    return TrainResponse(
        model_id=result["model_id"],
        target_column=target_column,
        problem_type=problem_type,
        best_model=result["best_model_name"],
        best_metrics=result["best_metrics"],
        all_metrics=result["all_metrics"],
        feature_importance=result["feature_importance"],
    )


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    result = run_prediction(payload.model_id, payload.record)
    return PredictResponse(**result)


@router.get("/explain/{model_id}", response_model=ExplainResponse)
def explain(model_id: str, db: Session = Depends(get_db)):
    artifact = db.query(ModelArtifact).filter(ModelArtifact.id == model_id).first()
    if artifact:
        return ExplainResponse(
            feature_importance=artifact.feature_importance or [],
            shap_summary=artifact.shap_summary or {},
        )

    bundle = load_model_bundle(model_id)
    return ExplainResponse(
        feature_importance=bundle.get("feature_importance", []),
        shap_summary=bundle.get("shap_summary", {}),
    )
