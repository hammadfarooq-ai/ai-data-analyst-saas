from pydantic import BaseModel


class EDAResponse(BaseModel):
    dataset_overview: dict
    missing_values: dict
    correlation_matrix: dict
    numerical_distributions: list[dict]
    categorical_value_counts: list[dict]
    outliers: dict
    skewness: dict
