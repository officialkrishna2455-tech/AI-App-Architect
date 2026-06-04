"""
Requirement AST Models — The Single Source of Truth.

All compiler stages after the Parser consume this AST. Raw user text is NEVER
used after parsing. Every node is strongly typed via Pydantic v2 discriminated
unions for type safety and 10x+ deserialization performance.

AST Hierarchy:
    RequirementAST (root)
    ├── EntityNode[]        — Data entities (User, Contact, Product)
    │   ├── FieldNode[]     — Entity fields with types
    │   └── RelationNode[]  — Inter-entity relationships
    ├── FeatureNode[]       — Application features (Dashboard, Login)
    │   ├── ActionNode[]    — CRUD + custom actions
    │   └── ConstraintNode[]— Access control, gating, validation rules
    ├── RoleNode[]          — User roles (admin, user, manager)
    │   └── PermissionNode[]— Per-role permissions
    ├── PlanNode[]          — Subscription plans (free, premium)
    │   └── PlanFeatureGate[]
    └── IntegrationNode[]   — External integrations (payments, analytics)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any, Literal, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field, computed_field, model_validator


# ═══════════════════════════════════════════════════════════════════
# Token Types — Output of the Lexer
# ═══════════════════════════════════════════════════════════════════

class TokenType(str, Enum):
    """Domain-specific token categories produced by the Lexer."""
    ENTITY = "entity"
    ACTION = "action"
    FEATURE = "feature"
    ROLE = "role"
    CONSTRAINT = "constraint"
    RELATION = "relation"
    MODIFIER = "modifier"
    PLAN = "plan"
    INTEGRATION = "integration"
    FIELD_TYPE = "field_type"
    PUNCTUATION = "punctuation"
    CONNECTOR = "connector"       # "and", "with", "or"
    QUANTIFIER = "quantifier"     # "multiple", "many", "single"
    UNKNOWN = "unknown"


class Token(BaseModel):
    """A single lexical token from the requirement text."""
    type: TokenType
    value: str                     # Normalized form (lowercase, stemmed)
    raw: str                       # Original text fragment
    position: int                  # Character offset in source
    line: int = 1                  # Line number (1-indexed)
    confidence: float = 1.0        # 1.0 for regex, <1.0 for spaCy NER


# ═══════════════════════════════════════════════════════════════════
# Field Types — Used in Entity and DB Schema
# ═══════════════════════════════════════════════════════════════════

class FieldType(str, Enum):
    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    PASSWORD = "password"
    URL = "url"
    PHONE = "phone"
    ENUM = "enum"
    JSON = "json"
    UUID = "uuid"
    MONEY = "money"
    FILE = "file"
    IMAGE = "image"


class RelationType(str, Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


class FeatureType(str, Enum):
    PAGE = "page"
    SERVICE = "service"
    INTEGRATION = "integration"
    WIDGET = "widget"
    REPORT = "report"
    WORKFLOW = "workflow"


class ActionVerb(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    SEARCH = "search"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"
    ASSIGN = "assign"
    NOTIFY = "notify"


class ConstraintType(str, Enum):
    ACCESS_CONTROL = "access_control"
    PAYMENT_GATE = "payment_gate"
    FIELD_VALIDATION = "field_validation"
    RATE_LIMIT = "rate_limit"
    DATA_RETENTION = "data_retention"
    UNIQUENESS = "uniqueness"
    REQUIRED_FIELD = "required_field"
    CONDITIONAL = "conditional"


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# ═══════════════════════════════════════════════════════════════════
# AST Node Definitions
# ═══════════════════════════════════════════════════════════════════

class SourceLocation(BaseModel):
    """Tracks origin in the source requirement text for error reporting."""
    line: int = 1
    column: int = 0
    length: int = 0
    raw_text: str = ""


class FieldNode(BaseModel):
    """A typed field belonging to an entity."""
    node_type: Literal["field"] = "field"
    name: str
    field_type: FieldType
    required: bool = True
    unique: bool = False
    indexed: bool = False
    default: Optional[Any] = None
    enum_values: Optional[list[str]] = None
    description: str = ""
    source: Optional[SourceLocation] = None


class RelationNode(BaseModel):
    """A relationship between two entities."""
    node_type: Literal["relation"] = "relation"
    target_entity: str
    relation_type: RelationType
    foreign_key: Optional[str] = None
    cascade_delete: bool = False
    back_reference: Optional[str] = None
    source: Optional[SourceLocation] = None


class PermissionNode(BaseModel):
    """A single permission grant on an entity/action pair."""
    node_type: Literal["permission"] = "permission"
    resource: str             # Entity or feature name
    actions: list[ActionVerb]
    conditions: Optional[dict[str, Any]] = None  # e.g., {"own_only": true}
    source: Optional[SourceLocation] = None


class ActionNode(BaseModel):
    """An action that can be performed on an entity."""
    node_type: Literal["action"] = "action"
    verb: ActionVerb
    target_entity: str
    required_roles: list[str] = Field(default_factory=list)
    required_plan: Optional[str] = None
    custom_logic: Optional[str] = None
    source: Optional[SourceLocation] = None


class ConstraintNode(BaseModel):
    """A constraint applied to a feature or entity."""
    node_type: Literal["constraint"] = "constraint"
    constraint_type: ConstraintType
    target: str               # Entity or feature name
    parameters: dict[str, Any] = Field(default_factory=dict)
    description: str = ""
    source: Optional[SourceLocation] = None


class PlanFeatureGate(BaseModel):
    """Maps a subscription plan to gated features."""
    feature: str
    limit: Optional[int] = None      # e.g., max 100 contacts on free
    enabled: bool = True


class PlanNode(BaseModel):
    """A subscription/pricing plan."""
    node_type: Literal["plan"] = "plan"
    name: str
    tier: int = 0                    # 0=free, 1=basic, 2=premium, 3=enterprise
    price: Optional[float] = None
    features: list[PlanFeatureGate] = Field(default_factory=list)
    source: Optional[SourceLocation] = None


class IntegrationNode(BaseModel):
    """An external service integration."""
    node_type: Literal["integration"] = "integration"
    name: str
    integration_type: str           # "payment", "analytics", "email", etc.
    provider: Optional[str] = None  # "stripe", "google_analytics", etc.
    config: dict[str, Any] = Field(default_factory=dict)
    source: Optional[SourceLocation] = None


class EntityNode(BaseModel):
    """A data entity — the core building block of the domain model."""
    node_type: Literal["entity"] = "entity"
    name: str
    fields: list[FieldNode] = Field(default_factory=list)
    relations: list[RelationNode] = Field(default_factory=list)
    is_auth_entity: bool = False     # True for User-like entities
    soft_delete: bool = False
    timestamps: bool = True          # Include created_at, updated_at
    description: str = ""
    source: Optional[SourceLocation] = None


class FeatureNode(BaseModel):
    """An application feature — pages, services, workflows."""
    node_type: Literal["feature"] = "feature"
    name: str
    feature_type: FeatureType
    entities: list[str] = Field(default_factory=list)      # Referenced entity names
    actions: list[ActionNode] = Field(default_factory=list)
    constraints: list[ConstraintNode] = Field(default_factory=list)
    auth_required: bool = True
    required_roles: list[str] = Field(default_factory=list)
    required_plan: Optional[str] = None
    sub_features: list[str] = Field(default_factory=list)   # Child feature names
    description: str = ""
    source: Optional[SourceLocation] = None


class RoleNode(BaseModel):
    """A user role with associated permissions."""
    node_type: Literal["role"] = "role"
    name: str
    is_default: bool = False
    parent_role: Optional[str] = None    # Role inheritance
    permissions: list[PermissionNode] = Field(default_factory=list)
    description: str = ""
    source: Optional[SourceLocation] = None


# ═══════════════════════════════════════════════════════════════════
# AST Metadata
# ═══════════════════════════════════════════════════════════════════

class ASTMetadata(BaseModel):
    """Metadata about the compilation process."""
    version: str = "1.0.0"
    source_hash: str = ""              # SHA-256 of original requirement text
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    token_count: int = 0
    node_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    enrichments: list[str] = Field(default_factory=list)   # Tracks what the semantic analyzer added


# ═══════════════════════════════════════════════════════════════════
# RequirementAST — The Root Node (Single Source of Truth)
# ═══════════════════════════════════════════════════════════════════

class RequirementAST(BaseModel):
    """
    Root of the Requirement AST.

    This is THE canonical data structure consumed by all pipeline stages
    after the Parser. Raw user text must NEVER be used after this is constructed.
    """
    entities: list[EntityNode] = Field(default_factory=list)
    features: list[FeatureNode] = Field(default_factory=list)
    roles: list[RoleNode] = Field(default_factory=list)
    plans: list[PlanNode] = Field(default_factory=list)
    integrations: list[IntegrationNode] = Field(default_factory=list)
    constraints: list[ConstraintNode] = Field(default_factory=list)
    metadata: ASTMetadata = Field(default_factory=ASTMetadata)

    @computed_field
    @property
    def total_nodes(self) -> int:
        count = len(self.entities) + len(self.features) + len(self.roles)
        count += len(self.plans) + len(self.integrations) + len(self.constraints)
        for entity in self.entities:
            count += len(entity.fields) + len(entity.relations)
        for feature in self.features:
            count += len(feature.actions) + len(feature.constraints)
        for role in self.roles:
            count += len(role.permissions)
        return count

    def get_entity(self, name: str) -> Optional[EntityNode]:
        """Look up an entity by name (case-insensitive)."""
        name_lower = name.lower()
        for entity in self.entities:
            if entity.name.lower() == name_lower:
                return entity
        return None

    def get_role(self, name: str) -> Optional[RoleNode]:
        """Look up a role by name (case-insensitive)."""
        name_lower = name.lower()
        for role in self.roles:
            if role.name.lower() == name_lower:
                return role
        return None

    def get_feature(self, name: str) -> Optional[FeatureNode]:
        """Look up a feature by name (case-insensitive)."""
        name_lower = name.lower()
        for feature in self.features:
            if feature.name.lower() == name_lower:
                return feature
        return None

    def entity_names(self) -> list[str]:
        return [e.name for e in self.entities]

    def role_names(self) -> list[str]:
        return [r.name for r in self.roles]

    def feature_names(self) -> list[str]:
        return [f.name for f in self.features]


# ═══════════════════════════════════════════════════════════════════
# Generated Schema Types — Output of the Schema Generator
# ═══════════════════════════════════════════════════════════════════

# ── UI Schema ────────────────────────────────────────────────────

class ComponentRef(BaseModel):
    name: str
    props: dict[str, Any] = Field(default_factory=dict)


class PageDefinition(BaseModel):
    route: str
    title: str
    layout: str = "default"
    components: list[ComponentRef] = Field(default_factory=list)
    auth_required: bool = True
    required_roles: list[str] = Field(default_factory=list)
    required_plan: Optional[str] = None
    data_sources: list[str] = Field(default_factory=list)  # API endpoints this page calls


class ComponentDefinition(BaseModel):
    name: str
    component_type: str              # "form", "table", "chart", "card", "modal"
    entity: Optional[str] = None     # Bound entity
    fields: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)


class NavigationItem(BaseModel):
    label: str
    route: str
    icon: Optional[str] = None
    children: list[NavigationItem] = Field(default_factory=list)
    required_roles: list[str] = Field(default_factory=list)
    required_plan: Optional[str] = None

NavigationItem.model_rebuild()


class UISchema(BaseModel):
    pages: list[PageDefinition] = Field(default_factory=list)
    components: list[ComponentDefinition] = Field(default_factory=list)
    navigation: list[NavigationItem] = Field(default_factory=list)
    theme: dict[str, Any] = Field(default_factory=dict)


# ── API Schema ───────────────────────────────────────────────────

class EndpointParam(BaseModel):
    name: str
    param_type: str        # "path", "query", "header"
    data_type: str
    required: bool = True


class EndpointDefinition(BaseModel):
    method: str                               # GET, POST, PUT, DELETE, PATCH
    path: str
    summary: str = ""
    request_body: Optional[dict[str, Any]] = None
    response_body: dict[str, Any] = Field(default_factory=dict)
    parameters: list[EndpointParam] = Field(default_factory=list)
    auth_required: bool = True
    required_roles: list[str] = Field(default_factory=list)
    required_plan: Optional[str] = None
    rate_limit: Optional[str] = None
    entity: Optional[str] = None              # Bound entity


class MiddlewareDefinition(BaseModel):
    name: str
    middleware_type: str     # "auth", "cors", "rate_limit", "logging"
    config: dict[str, Any] = Field(default_factory=dict)


class APISchema(BaseModel):
    base_path: str = "/api/v1"
    endpoints: list[EndpointDefinition] = Field(default_factory=list)
    middleware: list[MiddlewareDefinition] = Field(default_factory=list)
    error_codes: dict[str, str] = Field(default_factory=dict)


# ── DB Schema ────────────────────────────────────────────────────

class ColumnDefinition(BaseModel):
    name: str
    data_type: str           # "VARCHAR(255)", "INTEGER", "BOOLEAN", etc.
    nullable: bool = False
    primary_key: bool = False
    unique: bool = False
    indexed: bool = False
    default: Optional[str] = None
    foreign_key: Optional[str] = None    # "table.column"


class IndexDefinition(BaseModel):
    name: str
    table: str
    columns: list[str]
    unique: bool = False


class DBRelation(BaseModel):
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    on_delete: str = "CASCADE"


class MigrationStep(BaseModel):
    step: int
    description: str
    sql_up: str
    sql_down: str


class TableDefinition(BaseModel):
    name: str
    columns: list[ColumnDefinition] = Field(default_factory=list)
    primary_key: str = "id"
    unique_constraints: list[list[str]] = Field(default_factory=list)
    indexes: list[str] = Field(default_factory=list)


class DBSchema(BaseModel):
    tables: list[TableDefinition] = Field(default_factory=list)
    indexes: list[IndexDefinition] = Field(default_factory=list)
    relations: list[DBRelation] = Field(default_factory=list)
    migrations: list[MigrationStep] = Field(default_factory=list)


# ── Auth Schema ──────────────────────────────────────────────────

class RoleDefinition(BaseModel):
    name: str
    description: str = ""
    is_default: bool = False
    parent: Optional[str] = None


class PermissionDefinition(BaseModel):
    role: str
    resource: str
    actions: list[str]
    conditions: dict[str, Any] = Field(default_factory=dict)


class PolicyDefinition(BaseModel):
    name: str
    description: str = ""
    effect: str = "allow"              # "allow" or "deny"
    roles: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    conditions: dict[str, Any] = Field(default_factory=dict)


class TokenConfig(BaseModel):
    algorithm: str = "HS256"
    expire_minutes: int = 1440
    refresh_enabled: bool = True
    refresh_expire_days: int = 7


class AuthSchema(BaseModel):
    provider: str = "jwt"
    roles: list[RoleDefinition] = Field(default_factory=list)
    permissions: list[PermissionDefinition] = Field(default_factory=list)
    policies: list[PolicyDefinition] = Field(default_factory=list)
    token_config: TokenConfig = Field(default_factory=TokenConfig)


# ── Business Logic Schema ────────────────────────────────────────

class WorkflowStep(BaseModel):
    step: int
    action: str
    entity: Optional[str] = None
    conditions: dict[str, Any] = Field(default_factory=dict)
    on_success: Optional[str] = None
    on_failure: Optional[str] = None


class WorkflowDefinition(BaseModel):
    name: str
    trigger: str                    # "on_create", "on_update", "scheduled", "manual"
    entity: Optional[str] = None
    steps: list[WorkflowStep] = Field(default_factory=list)


class BusinessRule(BaseModel):
    name: str
    entity: str
    rule_type: str                  # "validation", "computation", "trigger"
    condition: str                  # Human-readable condition
    action: str                     # What to do when condition is met
    parameters: dict[str, Any] = Field(default_factory=dict)


class EventDefinition(BaseModel):
    name: str
    trigger_entity: str
    trigger_action: str
    payload_fields: list[str] = Field(default_factory=list)
    subscribers: list[str] = Field(default_factory=list)


class IntegrationDefinition(BaseModel):
    name: str
    service_type: str               # "payment", "email", "analytics", "storage"
    provider: str
    endpoints: list[str] = Field(default_factory=list)
    webhooks: list[str] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)


class BusinessLogicSchema(BaseModel):
    workflows: list[WorkflowDefinition] = Field(default_factory=list)
    rules: list[BusinessRule] = Field(default_factory=list)
    events: list[EventDefinition] = Field(default_factory=list)
    integrations: list[IntegrationDefinition] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════
# Compiled Output — The Final Executable Specification
# ═══════════════════════════════════════════════════════════════════

class CompiledSpecification(BaseModel):
    """The final output of the full compiler pipeline."""
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    requirement_text: str = ""
    ast: RequirementAST = Field(default_factory=RequirementAST)
    ui_schema: UISchema = Field(default_factory=UISchema)
    api_schema: APISchema = Field(default_factory=APISchema)
    db_schema: DBSchema = Field(default_factory=DBSchema)
    auth_schema: AuthSchema = Field(default_factory=AuthSchema)
    business_logic: BusinessLogicSchema = Field(default_factory=BusinessLogicSchema)


# ═══════════════════════════════════════════════════════════════════
# Validation & Repair Reports
# ═══════════════════════════════════════════════════════════════════

class ValidationIssue(BaseModel):
    """A single validation issue found during schema validation."""
    rule_id: str                     # e.g., "V001", "V004"
    severity: Severity
    layer: str                       # "structural", "type", "cross_layer", "semantic"
    message: str
    affected_schema: str             # "ui", "api", "db", "auth", "business_logic"
    affected_path: str = ""          # JSON path within the schema
    suggestion: str = ""


class ValidationReport(BaseModel):
    """Complete validation report across all layers."""
    total_issues: int = 0
    errors: int = 0
    warnings: int = 0
    infos: int = 0
    issues: list[ValidationIssue] = Field(default_factory=list)
    passed: bool = True
    validation_time_ms: int = 0

    @model_validator(mode="after")
    def compute_counts(self) -> "ValidationReport":
        self.total_issues = len(self.issues)
        self.errors = sum(1 for i in self.issues if i.severity == Severity.ERROR)
        self.warnings = sum(1 for i in self.issues if i.severity == Severity.WARNING)
        self.infos = sum(1 for i in self.issues if i.severity == Severity.INFO)
        self.passed = self.errors == 0
        return self


class RepairAction(BaseModel):
    """A single repair action taken by the Repair Engine."""
    issue_rule_id: str
    action_type: str                 # "add", "modify", "remove", "link", "dedupe"
    target_schema: str
    target_path: str
    description: str
    before_value: Optional[Any] = None
    after_value: Optional[Any] = None
    changes: list[dict[str, Any]] = Field(default_factory=list)  # Structured change log


class RepairReport(BaseModel):
    """Report of all repairs applied."""
    repair_id: str = Field(default_factory=lambda: str(uuid4()))
    total_repairs: int = 0
    repairs: list[RepairAction] = Field(default_factory=list)
    unresolvable: list[ValidationIssue] = Field(default_factory=list)
    affected_layers: list[str] = Field(default_factory=list)
    revalidation_passed: bool = False
    iterations_used: int = 0
    repair_time_ms: int = 0

    @model_validator(mode="after")
    def compute_count(self) -> "RepairReport":
        self.total_repairs = len(self.repairs)
        # Deduce affected layers from repairs
        if self.repairs and not self.affected_layers:
            self.affected_layers = list({r.target_schema for r in self.repairs})
        return self


# ═══════════════════════════════════════════════════════════════════
# Runtime Simulation Report
# ═══════════════════════════════════════════════════════════════════

class SimulationScenario(BaseModel):
    """A single simulation test scenario."""
    scenario_id: str
    category: str                    # "crud", "auth", "permission", "navigation", "premium", "analytics"
    description: str
    steps: list[str] = Field(default_factory=list)
    expected_result: str = "pass"
    actual_result: str = ""          # "pass" or "fail"
    passed: bool = True
    error_message: str = ""


class SimulationReport(BaseModel):
    """Complete report of the runtime digital twin simulation."""
    total_scenarios: int = 0
    passed_count: int = 0
    failed_count: int = 0
    scenarios: list[SimulationScenario] = Field(default_factory=list)
    simulation_time_ms: int = 0

    @computed_field
    @property
    def pass_rate(self) -> float:
        return self.passed_count / max(self.total_scenarios, 1)

    @model_validator(mode="after")
    def compute_counts(self) -> "SimulationReport":
        self.total_scenarios = len(self.scenarios)
        self.passed_count = sum(1 for s in self.scenarios if s.passed)
        self.failed_count = self.total_scenarios - self.passed_count
        return self


# ═══════════════════════════════════════════════════════════════════
# Architecture Plan — Output of the Architecture Planner
# ═══════════════════════════════════════════════════════════════════

class ArchitecturePlan(BaseModel):
    """Architectural decisions made by the Architecture Planner."""
    db_strategy: str = "normalized"               # "normalized" or "denormalized"
    api_pattern: str = "rest"                      # "rest" or "graphql"
    auth_strategy: str = "jwt"                     # "jwt", "session", "oauth"
    caching_strategy: str = "none"                 # "none", "redis", "in_memory"
    file_storage: str = "local"                    # "local", "s3", "gcs"
    search_strategy: str = "sql_like"              # "sql_like", "elasticsearch", "meilisearch"
    realtime_strategy: str = "polling"             # "polling", "websocket", "sse"
    recommendations: list[str] = Field(default_factory=list)
    estimated_complexity: str = "medium"            # "simple", "medium", "complex", "enterprise"
