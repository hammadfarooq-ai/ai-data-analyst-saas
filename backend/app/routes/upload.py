from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.dataset import Dataset
from app.schemas.upload import DatasetSummary
from app.services.file_service import read_csv, save_csv_file


router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("", response_model=DatasetSummary)
def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path, stored_filename = save_csv_file(file)
    df = read_csv(file_path)

    summary = Dataset(
        original_filename=file.filename or "unknown.csv",
        stored_filename=stored_filename,
        file_path=file_path,
        rows=int(df.shape[0]),
        columns=int(df.shape[1]),
        column_names=df.columns.tolist(),
        dtypes={col: str(dtype) for col, dtype in df.dtypes.items()},
        missing_values={col: int(v) for col, v in df.isna().sum().items()},
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)

    return DatasetSummary(
        dataset_id=summary.id,
        rows=summary.rows,
        columns=summary.columns,
        column_names=summary.column_names,
        dtypes=summary.dtypes,
        missing_values=summary.missing_values,
    )
