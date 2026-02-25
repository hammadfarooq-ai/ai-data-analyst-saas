import uuid
from pathlib import Path

import pandas as pd
from fastapi import HTTPException, UploadFile

from app.core.config import settings


def ensure_storage_dirs() -> None:
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.model_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.report_dir).mkdir(parents=True, exist_ok=True)


def save_csv_file(file: UploadFile) -> tuple[str, str]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    ensure_storage_dirs()
    file_id = str(uuid.uuid4())
    stored_filename = f"{file_id}.csv"
    path = Path(settings.upload_dir) / stored_filename

    content = file.file.read()
    path.write_bytes(content)
    return str(path), stored_filename


def read_csv(path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to parse CSV: {exc}") from exc
