from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class NodeType(str, Enum):
    ENTITY = "entity"
    FIELD = "field"
    ROLE = "role"
    PAGE = "page"
    ENDPOINT = "endpoint"
    PERMISSION = "permission"
    PLAN = "plan"
    TABLE = "table"
    COLUMN = "column"
    WORKFLOW = "workflow"

class EdgeType(str, Enum):
    HAS_FIELD = "has_field"
    REFERENCES = "references"
    REQUIRES_ROLE = "requires_role"
    DISPLAYS = "displays"
    CALLS = "calls"
    GRANTS = "grants"
    GATES = "gates"
    MAPS_TO = "maps_to"
    TRIGGERS = "triggers"
    CONTAINS = "contains"

class GraphNode(BaseModel):
    id: str
    node_type: NodeType
    label: str
    properties: dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    source: str
    target: str
    edge_type: EdgeType
    properties: dict[str, Any] = Field(default_factory=dict)
