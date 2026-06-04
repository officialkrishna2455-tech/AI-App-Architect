"""
API Response schemas — Pydantic models for outgoing HTTP responses.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, computed_field

from app.schemas.ast_models import (
    APISchema,
    AuthSchema,
    BusinessLogicSchema,
    DBSchema,
    RepairReport,
    RequirementAST,
    SimulationReport,
    UISchema,
    ValidationReport,
)


class StageLatency(BaseModel):
    """Latency for a single pipeline stage."""
    stage: str
    latency_ms: int
    status: str = "completed"  # "completed", "failed", "skipped"


class CompileMetrics(BaseModel):
    """Metrics from a compilation run."""
    total_latency_ms: int = 0
    stage_latencies: list[StageLatency] = Field(default_factory=list)
    token_count: int = 0
    node_count: int = 0
    validation_pass_rate: float = 0.0
    repair_count: int = 0
    simulation_pass_rate: float = 0.0


class SchemaOutput(BaseModel):
    """All five generated schemas bundled together."""
    ui_schema: UISchema = Field(default_factory=UISchema)
    api_schema: APISchema = Field(default_factory=APISchema)
    db_schema: DBSchema = Field(default_factory=DBSchema)
    auth_schema: AuthSchema = Field(default_factory=AuthSchema)
    business_logic_schema: BusinessLogicSchema = Field(default_factory=BusinessLogicSchema)


class KnowledgeGraphOutput(BaseModel):
    """Serializable knowledge graph for API responses."""
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0


class CompileResponse(BaseModel):
    """POST /compile — Full compilation result."""
    run_id: str
    status: str
    ast: RequirementAST = Field(default_factory=RequirementAST)
    schemas: SchemaOutput = Field(default_factory=SchemaOutput)
    validation_report: ValidationReport = Field(default_factory=ValidationReport)
    repair_report: RepairReport = Field(default_factory=RepairReport)
    simulation_report: SimulationReport = Field(default_factory=SimulationReport)
    knowledge_graph: KnowledgeGraphOutput = Field(default_factory=KnowledgeGraphOutput)
    metrics: CompileMetrics = Field(default_factory=CompileMetrics)


class RunSummary(BaseModel):
    """Summary of a compilation run for list views."""
    run_id: str
    status: str
    requirements_preview: str = ""     # First 200 chars
    total_latency_ms: int = 0
    validation_pass_rate: float = 0.0
    simulation_pass_rate: float = 0.0
    entity_count: int = 0
    feature_count: int = 0
    created_at: str = ""
    updated_at: str = ""


class RunListResponse(BaseModel):
    """GET /runs — Paginated list of compilation runs."""
    runs: list[RunSummary] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class MetricsResponse(BaseModel):
    """GET /metrics — Aggregate evaluation metrics."""
    total_runs: int = 0
    success_rate: float = 0.0
    average_latency_ms: float = 0.0
    average_repair_rate: float = 0.0
    average_validation_pass_rate: float = 0.0
    average_simulation_pass_rate: float = 0.0
    p50_latency_ms: int = 0
    p95_latency_ms: int = 0
    p99_latency_ms: int = 0


class TokenResponse(BaseModel):
    """POST /auth/login — JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1440


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: str = "INTERNAL_ERROR"
    status_code: int = 500


class EvalPromptResult(BaseModel):
    """Result of a single evaluation prompt."""
    prompt_id: int
    prompt_type: str            # "production" or "adversarial"
    prompt_text: str
    success: bool
    validation_pass_rate: float = 0.0
    simulation_pass_rate: float = 0.0
    repair_count: int = 0
    latency_ms: int = 0
    error_message: str = ""


class EvalRunResponse(BaseModel):
    """POST /evaluate — Evaluation run results."""
    total_prompts: int = 0
    success_count: int = 0
    success_rate: float = 0.0
    results: list[EvalPromptResult] = Field(default_factory=list)
    aggregate_metrics: MetricsResponse = Field(default_factory=MetricsResponse)
