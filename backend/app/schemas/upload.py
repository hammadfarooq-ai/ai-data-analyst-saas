from pydantic import BaseModel


class DatasetSummary(BaseModel):
    dataset_id: str
    rows: int
    columns: int
    column_names: list[str]
    dtypes: dict[str, str]
    missing_values: dict[str, int]
