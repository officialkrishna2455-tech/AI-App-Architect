"""
SQLAlchemy ORM model for evaluation results.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, ForeignKey

from app.database import Base


class EvaluationResult(Base):
    """Stores results from the evaluation framework's test prompts."""

    __tablename__ = "evaluation_results"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("compilation_runs.id"), nullable=True, index=True)
    prompt_id = Column(Integer, nullable=False)
    prompt_type = Column(String, nullable=False)       # "production" or "adversarial"
    prompt_text = Column(Text, nullable=False)
    success = Column(Boolean, nullable=False, default=False)
    validation_pass_rate = Column(Float, default=0.0)
    simulation_pass_rate = Column(Float, default=0.0)
    repair_count = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
