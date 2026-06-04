"""
SQLAlchemy ORM model for compilation runs and stage metrics.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class CompilationRun(Base):
    """Persists a full compilation run with all schemas and reports."""

    __tablename__ = "compilation_runs"

    id = Column(String, primary_key=True)
    requirements = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="queued", index=True)
    # Status values: queued, processing, validating, repairing, simulating, completed, failed

    # Serialized JSON columns for each output
    ast_json = Column(Text, nullable=True)
    ui_schema_json = Column(Text, nullable=True)
    api_schema_json = Column(Text, nullable=True)
    db_schema_json = Column(Text, nullable=True)
    auth_schema_json = Column(Text, nullable=True)
    business_logic_json = Column(Text, nullable=True)
    knowledge_graph_json = Column(Text, nullable=True)
    validation_report_json = Column(Text, nullable=True)
    repair_report_json = Column(Text, nullable=True)
    simulation_report_json = Column(Text, nullable=True)
    metrics_json = Column(Text, nullable=True)
    options_json = Column(Text, nullable=True)

    # Denormalized metrics for fast queries
    total_latency_ms = Column(Integer, default=0)
    validation_pass_rate = Column(Float, default=0.0)
    simulation_pass_rate = Column(Float, default=0.0)
    entity_count = Column(Integer, default=0)
    feature_count = Column(Integer, default=0)
    repair_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    stage_metrics = relationship("StageMetric", back_populates="run", cascade="all, delete-orphan")


class StageMetric(Base):
    """Per-stage latency and error tracking for a compilation run."""

    __tablename__ = "stage_metrics"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("compilation_runs.id"), nullable=False, index=True)
    stage_name = Column(String, nullable=False)
    latency_ms = Column(Integer, nullable=False, default=0)
    status = Column(String, default="completed")  # "completed", "failed", "skipped"
    input_size = Column(Integer, default=0)
    output_size = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    run = relationship("CompilationRun", back_populates="stage_metrics")
