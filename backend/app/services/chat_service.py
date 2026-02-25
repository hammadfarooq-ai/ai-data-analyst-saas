import re

import pandas as pd


def answer_question(df: pd.DataFrame, question: str, shap_summary: dict | None = None) -> dict:
    q = question.lower().strip()
    columns_lower = {col.lower(): col for col in df.columns}

    if "average" in q or "mean" in q:
        for key, original in columns_lower.items():
            if key in q and pd.api.types.is_numeric_dtype(df[original]):
                value = float(df[original].mean())
                return {
                    "answer": f"The average of {original} is {value:.4f}.",
                    "query_used": f"df['{original}'].mean()",
                }

    if "sum" in q or "total" in q:
        for key, original in columns_lower.items():
            if key in q and pd.api.types.is_numeric_dtype(df[original]):
                value = float(df[original].sum())
                return {
                    "answer": f"The total of {original} is {value:.4f}.",
                    "query_used": f"df['{original}'].sum()",
                }

    if ("impact" in q or "important" in q) and shap_summary:
        top = shap_summary.get("top_features", [])
        if top:
            best = top[0]
            return {
                "answer": f"The most impactful feature is {best['feature']} with SHAP importance {best['mean_abs_shap']:.4f}.",
                "query_used": "shap_summary['top_features'][0]",
            }

    # Lightweight filter parsing: "count where age > 30"
    match = re.search(r"count where ([a-zA-Z0-9_]+)\s*(==|=|>|<|>=|<=)\s*([a-zA-Z0-9_.-]+)", q)
    if match:
        col, op, raw_val = match.groups()
        if col.lower() in columns_lower:
            real_col = columns_lower[col.lower()]
            op = "==" if op == "=" else op
            try:
                val = float(raw_val)
                expr = f"`{real_col}` {op} {val}"
            except ValueError:
                expr = f"`{real_col}` {op} '{raw_val}'"
            count = int(df.query(expr).shape[0])
            return {"answer": f"The count is {count}.", "query_used": f"df.query(\"{expr}\").shape[0]"}

    return {
        "answer": "I could not map this question to a safe analytical query yet. Try asking about average, total, count filters, or feature importance.",
        "query_used": None,
    }
