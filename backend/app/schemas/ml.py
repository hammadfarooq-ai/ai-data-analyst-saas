from typing import Any

from pydantic import BaseModel


class TargetDetectionResponse(BaseModel):
    detected_target: str | None
    problem_type: str | None
    candidates: list[str]
    reason: str


class TrainRequest(BaseModel):
    dataset_id: str
    target_column: str | None = None


class TrainResponse(BaseModel):
    model_id: str
    target_column: str
    problem_type: str
    best_model: str
    best_metrics: dict[str, float]
    all_metrics: dict[str, Any]
    feature_importance: list[dict[str, float | str]]


class PredictRequest(BaseModel):
    model_id: str
    record: dict[str, Any]


class PredictResponse(BaseModel):
    prediction: Any
    probability: float | None
    confidence_score: float


class ExplainResponse(BaseModel):
    feature_importance: list[dict]
    shap_summary: dict
