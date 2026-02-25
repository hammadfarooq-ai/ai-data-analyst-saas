import uuid
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

from app.core.config import settings


def _build_preprocessor(df: pd.DataFrame, target_column: str) -> tuple[ColumnTransformer, list[str], list[str]]:
    feature_df = df.drop(columns=[target_column])
    numeric_features = feature_df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = feature_df.select_dtypes(exclude=[np.number]).columns.tolist()

    numeric_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    )
    categorical_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ],
        remainder="drop",
    )
    return preprocessor, numeric_features, categorical_features


def _classification_models() -> dict:
    return {
        "LogisticRegression": LogisticRegression(max_iter=2000),
        "RandomForestClassifier": RandomForestClassifier(n_estimators=300, random_state=42),
        "GradientBoostingClassifier": GradientBoostingClassifier(random_state=42),
    }


def _regression_models() -> dict:
    return {
        "LinearRegression": LinearRegression(),
        "RandomForestRegressor": RandomForestRegressor(n_estimators=300, random_state=42),
        "GradientBoostingRegressor": GradientBoostingRegressor(random_state=42),
        "XGBoostRegressor": XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
        ),
    }


def _classification_metrics(y_true, y_pred, y_proba=None) -> dict[str, float]:
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }
    if y_proba is not None and len(np.unique(y_true)) == 2:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba))
    else:
        metrics["roc_auc"] = 0.0
    return metrics


def _regression_metrics(y_true, y_pred) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2_score": float(r2_score(y_true, y_pred)),
    }


def _extract_feature_names(pipeline: Pipeline, numeric_features: list[str]) -> list[str]:
    preprocessor: ColumnTransformer = pipeline.named_steps["preprocessor"]
    try:
        names = preprocessor.get_feature_names_out()
        return [str(name) for name in names]
    except Exception:
        return numeric_features


def _extract_feature_importance(model, feature_names: list[str]) -> list[dict]:
    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
    elif hasattr(model, "coef_"):
        coef = np.ravel(model.coef_)
        values = np.abs(coef[: len(feature_names)])
    else:
        return []

    pairs = [{"feature": feature_names[i], "importance": float(values[i])} for i in range(min(len(values), len(feature_names)))]
    pairs.sort(key=lambda x: x["importance"], reverse=True)
    return pairs[:30]


def _compute_shap_summary(model, x_transformed: np.ndarray, feature_names: list[str]) -> dict:
    if hasattr(x_transformed, "toarray"):
        x_transformed = x_transformed.toarray()
    sample = x_transformed[: min(300, x_transformed.shape[0])]
    try:
        if "Forest" in model.__class__.__name__ or "GradientBoosting" in model.__class__.__name__ or "XGB" in model.__class__.__name__:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(sample)
        else:
            explainer = shap.Explainer(model.predict, sample)
            shap_values = explainer(sample).values

        if isinstance(shap_values, list):
            shap_arr = np.array(shap_values[0])
        else:
            shap_arr = np.array(shap_values)
        mean_abs = np.abs(shap_arr).mean(axis=0)
        pairs = [{"feature": feature_names[i], "mean_abs_shap": float(mean_abs[i])} for i in range(min(len(mean_abs), len(feature_names)))]
        pairs.sort(key=lambda x: x["mean_abs_shap"], reverse=True)
        return {"top_features": pairs[:30]}
    except Exception as exc:
        return {"top_features": [], "note": f"SHAP generation fallback: {exc}"}


def train_and_select_model(df: pd.DataFrame, target_column: str, problem_type: str) -> dict:
    x = df.drop(columns=[target_column])
    y = df[target_column]

    preprocessor, numeric_features, _ = _build_preprocessor(df, target_column)
    models = _classification_models() if problem_type == "classification" else _regression_models()

    try:
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.2, random_state=42, stratify=y if problem_type == "classification" else None
        )
    except ValueError:
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    all_metrics = {}
    best_model_name = None
    best_score = -np.inf
    best_pipeline = None
    best_metrics = {}
    confidence_score = 0.0

    for name, model in models.items():
        pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])
        scoring = "f1_weighted" if problem_type == "classification" else "r2"
        cv_folds = 5 if len(x_train) >= 50 else 3
        try:
            cv_scores = cross_val_score(pipeline, x_train, y_train, cv=cv_folds, scoring=scoring)
        except ValueError:
            cv_scores = np.array([0.0])

        pipeline.fit(x_train, y_train)
        y_pred = pipeline.predict(x_test)

        if problem_type == "classification":
            y_proba = None
            if hasattr(pipeline.named_steps["model"], "predict_proba"):
                y_proba = pipeline.predict_proba(x_test)[:, 1]
            metrics = _classification_metrics(y_test, y_pred, y_proba)
            key_score = metrics["f1_score"]
        else:
            metrics = _regression_metrics(y_test, y_pred)
            key_score = metrics["r2_score"]

        all_metrics[name] = {"cross_validation": float(np.mean(cv_scores)), "test_metrics": metrics}
        if key_score > best_score:
            best_score = key_score
            best_model_name = name
            best_pipeline = pipeline
            best_metrics = metrics
            confidence_score = float(np.mean(cv_scores))

    assert best_pipeline is not None
    feature_names = _extract_feature_names(best_pipeline, numeric_features)
    trained_model = best_pipeline.named_steps["model"]
    transformed_x = best_pipeline.named_steps["preprocessor"].transform(x)

    feature_importance = _extract_feature_importance(trained_model, feature_names)
    shap_summary = _compute_shap_summary(trained_model, transformed_x, feature_names)

    model_id = f"model_{uuid.uuid4().hex[:12]}"
    model_path = Path(settings.model_dir) / f"{model_id}.joblib"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": best_pipeline,
            "target_column": target_column,
            "problem_type": problem_type,
            "best_model_name": best_model_name,
            "feature_names": feature_names,
            "feature_importance": feature_importance,
            "shap_summary": shap_summary,
            "confidence_score": confidence_score,
        },
        model_path,
    )

    return {
        "model_id": model_id,
        "best_model_name": best_model_name,
        "best_metrics": best_metrics,
        "all_metrics": all_metrics,
        "model_path": str(model_path),
        "feature_importance": feature_importance,
        "shap_summary": shap_summary,
        "confidence_score": confidence_score,
    }
