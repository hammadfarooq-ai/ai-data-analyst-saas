import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ModelArtifact(Base):
    __tablename__ = "model_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=False)
    target_column: Mapped[str] = mapped_column(String(255), nullable=False)
    problem_type: Mapped[str] = mapped_column(String(32), nullable=False)
    best_model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    all_metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    best_metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    feature_importance: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    shap_summary: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
