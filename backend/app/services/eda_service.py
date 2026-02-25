import json

import numpy as np
import pandas as pd
import plotly.express as px


def _fig_json(fig) -> dict:
    return json.loads(fig.to_json())


def build_eda_payload(df: pd.DataFrame) -> dict:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    overview = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "memory_usage_mb": float(df.memory_usage(deep=True).sum() / (1024 * 1024)),
        "columns_list": df.columns.tolist(),
    }

    missing = {col: int(val) for col, val in df.isna().sum().items()}

    corr_matrix = {}
    corr_plot = {}
    if numeric_cols:
        corr = df[numeric_cols].corr(numeric_only=True).fillna(0)
        corr_matrix = corr.to_dict()
        fig_corr = px.imshow(corr, text_auto=True, title="Correlation Matrix")
        corr_plot = _fig_json(fig_corr)

    numeric_distributions = []
    for col in numeric_cols[:12]:
        fig = px.histogram(df, x=col, nbins=30, title=f"Distribution of {col}")
        numeric_distributions.append({"column": col, "plot": _fig_json(fig)})

    categorical_counts = []
    for col in categorical_cols[:12]:
        top_values = df[col].astype(str).value_counts().head(20)
        fig = px.bar(
            x=top_values.index.tolist(),
            y=top_values.values.tolist(),
            title=f"Top Values for {col}",
            labels={"x": col, "y": "count"},
        )
        categorical_counts.append({"column": col, "plot": _fig_json(fig)})

    outliers = {}
    skewness = {}
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers[col] = int(((df[col] < lower) | (df[col] > upper)).sum())
        skewness[col] = float(df[col].skew()) if df[col].notna().sum() > 2 else 0.0

    return {
        "dataset_overview": overview,
        "missing_values": missing,
        "correlation_matrix": {"matrix": corr_matrix, "plot": corr_plot},
        "numerical_distributions": numeric_distributions,
        "categorical_value_counts": categorical_counts,
        "outliers": outliers,
        "skewness": skewness,
    }
