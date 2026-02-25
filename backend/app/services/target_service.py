import pandas as pd


TARGET_HINTS = [
    "target",
    "label",
    "class",
    "churn",
    "price",
    "salary",
    "outcome",
    "status",
    "y",
]

ID_HINTS = ["id", "uuid", "index", "customer_id", "user_id"]


def _is_id_column(col: str, series: pd.Series) -> bool:
    lower = col.lower()
    if any(hint in lower for hint in ID_HINTS):
        return True
    unique_ratio = series.nunique(dropna=False) / max(len(series), 1)
    return unique_ratio > 0.95 and lower.endswith("id")


def detect_target_column(df: pd.DataFrame) -> tuple[str | None, str | None, list[str], str]:
    if df.empty or df.shape[1] < 2:
        return None, None, [], "Dataset is too small to detect target."

    candidate_cols = [col for col in df.columns if not _is_id_column(col, df[col])]
    if not candidate_cols:
        return None, None, [], "No suitable candidate columns found."

    for col in candidate_cols:
        if any(hint in col.lower() for hint in TARGET_HINTS):
            series = df[col].dropna()
            if series.nunique() == 2:
                return col, "classification", candidate_cols, "Matched target hint and binary values."
            if pd.api.types.is_numeric_dtype(series) and series.nunique() > 10:
                return col, "regression", candidate_cols, "Matched target hint and continuous numeric values."

    # Fallback: choose right-most non-id column.
    fallback = candidate_cols[-1]
    series = df[fallback].dropna()
    if series.nunique() == 2:
        return fallback, "classification", candidate_cols, "Fallback binary target detection."
    if pd.api.types.is_numeric_dtype(series) and series.nunique() > 10:
        return fallback, "regression", candidate_cols, "Fallback continuous numeric target detection."
    return fallback, "classification", candidate_cols, "Fallback categorical target detection."
