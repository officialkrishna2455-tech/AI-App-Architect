"""
API Request schemas — Pydantic models for incoming HTTP requests.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CompileRequest(BaseModel):
    """POST /compile — Submit natural language requirements for compilation."""
    requirements: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Natural language software requirements to compile.",
        examples=["Build a CRM with login, contacts, dashboard, role-based access, premium plans, payments, and analytics."],
    )
    options: CompileOptions = Field(default_factory=lambda: CompileOptions())


class CompileOptions(BaseModel):
    """Optional configuration for the compilation run."""
    target_stack: str = "nextjs-fastapi"
    include_simulation: bool = True
    include_knowledge_graph: bool = True
    max_repair_iterations: int = 3
    max_simulation_repair_iterations: int = Field(
        default=2, ge=0, le=5,
        description="Max self-healing repair cycles when simulation fails (0 = no auto-repair).",
    )


class ValidateRequest(BaseModel):
    """POST /validate — Re-validate an existing compilation run."""
    run_id: str = Field(..., description="ID of the compilation run to validate.")


class RepairRequest(BaseModel):
    """POST /repair — Run repair on a specific compilation run."""
    run_id: str = Field(..., description="ID of the compilation run to repair.")
    max_iterations: int = Field(default=3, ge=1, le=10)


class SimulateRequest(BaseModel):
    """POST /simulate — Run simulation on a specific compilation run."""
    run_id: str = Field(..., description="ID of the compilation run to simulate.")
    categories: list[str] = Field(
        default_factory=lambda: ["crud", "auth", "authorization", "navigation", "premium", "flow"],
        description="Simulation categories to run.",
    )
    max_repair_iterations: int = Field(
        default=2, ge=0, le=5,
        description="Max self-healing repair cycles when simulation fails.",
    )


class RunListParams(BaseModel):
    """GET /runs — Query parameters for listing compilation runs."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    status: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


class LoginRequest(BaseModel):
    """POST /auth/login — Single-user authentication."""
    username: str
    password: str


class EvalRunRequest(BaseModel):
    """POST /evaluate — Run the evaluation framework."""
    prompt_ids: list[int] = Field(
        default_factory=lambda: list(range(1, 21)),
        description="IDs of evaluation prompts to run (1-20).",
    )
