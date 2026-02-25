from pathlib import Path

import joblib
import pandas as pd
from fastapi import HTTPException

from app.core.config import settings


def load_model_bundle(model_id: str) -> dict:
    path = Path(settings.model_dir) / f"{model_id}.joblib"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Model not found.")
    return joblib.load(path)


def run_prediction(model_id: str, record: dict) -> dict:
    bundle = load_model_bundle(model_id)
    pipeline = bundle["pipeline"]
    df = pd.DataFrame([record])
    pred = pipeline.predict(df)[0]

    probability = None
    if hasattr(pipeline.named_steps["model"], "predict_proba"):
        probs = pipeline.predict_proba(df)[0]
        probability = float(max(probs))

    return {
        "prediction": pred.item() if hasattr(pred, "item") else pred,
        "probability": probability,
        "confidence_score": float(bundle.get("confidence_score", 0.0)),
    }
