"""
Phase 3 — Unit tests for RepairEngine.

Tests each layer-specific repair method and the revalidation loop.
"""
import pytest
from app.schemas.ast_models import (
    RequirementAST, EntityNode, FieldNode, FieldType,
    UISchema, APISchema, DBSchema, AuthSchema, BusinessLogicSchema,
    CompiledSpecification,
    PageDefinition, NavigationItem, ComponentDefinition,
    EndpointDefinition, MiddlewareDefinition,
    TableDefinition, ColumnDefinition,
    RoleDefinition, PermissionDefinition,
    WorkflowDefinition, WorkflowStep, BusinessRule, EventDefinition,
    ValidationReport, ValidationIssue, Severity,
)
from app.compiler.repair_engine import RepairEngine
from app.compiler.validation_engine import ValidationEngine


# ─── Helpers ─────────────────────────────────────────────────────

def _make_spec(**overrides) -> CompiledSpecification:
    return CompiledSpecification(**overrides)


def _make_entity(name="User", fields=None, timestamps=False):
    if fields is None:
        fields = [
            FieldNode(name="id", field_type=FieldType.UUID, required=True, unique=True, indexed=True),
            FieldNode(name="email", field_type=FieldType.EMAIL, required=True),
        ]
    return EntityNode(name=name, fields=fields, timestamps=timestamps)


@pytest.fixture
def repair_engine():
    return RepairEngine()


@pytest.fixture
def validation_engine():
    return ValidationEngine()


# ═══════════════════════════════════════════════════════════════════
# repair_ast() — V002, V008, V009
# ═══════════════════════════════════════════════════════════════════

class TestRepairAST:

    def test_repair_v008_adds_primary_key(self, repair_engine):
        entity = EntityNode(name="NoPK", fields=[
            FieldNode(name="email", field_type=FieldType.EMAIL),
        ], timestamps=False)
        spec = _make_spec(ast=RequirementAST(entities=[entity]))
        issues = [ValidationIssue(
            rule_id="V008", severity=Severity.ERROR, layer="semantic",
            message="Entity 'NoPK' is missing a primary key (id)", affected_schema="ast",
        )]
        actions = repair_engine.repair_ast(spec, issues)
        assert len(actions) == 1
        assert actions[0].action_type == "add"
        assert spec.ast.entities[0].fields[0].name == "id"

    def test_repair_v009_adds_timestamps(self, repair_engine):
        entity = EntityNode(name="Timed", fields=[
            FieldNode(name="id", field_type=FieldType.UUID, required=True),
        ], timestamps=True)
        spec = _make_spec(ast=RequirementAST(entities=[entity]))
        issues = [ValidationIssue(
            rule_id="V009", severity=Severity.WARNING, layer="semantic",
            message="Entity 'Timed' has timestamps=True but is missing timestamp fields",
            affected_schema="ast",
        )]
        actions = repair_engine.repair_ast(spec, issues)
        assert len(actions) == 1
        field_names = [f.name for f in spec.ast.entities[0].fields]
        assert "created_at" in field_names
        assert "updated_at" in field_names

    def test_repair_v002_adds_field_to_empty_entity(self, repair_engine):
        entity = EntityNode(name="Empty", fields=[], timestamps=False)
        spec = _make_spec(ast=RequirementAST(entities=[entity]))
        issues = [ValidationIssue(
            rule_id="V002", severity=Severity.ERROR, layer="structural",
            message="Entity 'Empty' has no fields defined", affected_schema="ast",
        )]
        actions = repair_engine.repair_ast(spec, issues)
        assert len(actions) == 1
        assert spec.ast.entities[0].fields[0].name == "id"


# ═══════════════════════════════════════════════════════════════════
# repair_ui() — V011, V016, V019
# ═══════════════════════════════════════════════════════════════════

class TestRepairUI:

    def test_repair_v011_adds_login_page(self, repair_engine):
        spec = _make_spec(
            ui_schema=UISchema(pages=[PageDefinition(route="/", title="Home", auth_required=False)]),
            api_schema=APISchema(middleware=[MiddlewareDefinition(name="jwt", middleware_type="auth")]),
        )
        issues = [ValidationIssue(
            rule_id="V011", severity=Severity.ERROR, layer="semantic",
            message="Login page is missing but auth middleware is configured", affected_schema="ui",
        )]
        actions = repair_engine.repair_ui(spec, issues)
        assert len(actions) == 1
        assert any(p.route == "/login" for p in spec.ui_schema.pages)

    def test_repair_v016_removes_broken_nav(self, repair_engine):
        spec = _make_spec(
            ui_schema=UISchema(
                pages=[PageDefinition(route="/", title="Home", auth_required=False)],
                navigation=[
                    NavigationItem(label="Home", route="/"),
                    NavigationItem(label="Ghost", route="/nonexistent"),
                ],
            ),
        )
        issues = [ValidationIssue(
            rule_id="V016", severity=Severity.WARNING, layer="semantic",
            message="Navigation item 'Ghost' points to non-existent route '/nonexistent'",
            affected_schema="ui",
        )]
        actions = repair_engine.repair_ui(spec, issues)
        assert len(actions) == 1
        assert not any(n.label == "Ghost" for n in spec.ui_schema.navigation)
        assert any(n.label == "Home" for n in spec.ui_schema.navigation)

    def test_repair_v019_dedupes_page_routes(self, repair_engine):
        spec = _make_spec(
            ui_schema=UISchema(pages=[
                PageDefinition(route="/home", title="Home1"),
                PageDefinition(route="/home", title="Home2"),
                PageDefinition(route="/about", title="About"),
            ]),
        )
        issues = [ValidationIssue(
            rule_id="V019", severity=Severity.ERROR, layer="schema",
            message="Duplicate page route '/home' found 2 times", affected_schema="ui",
        )]
        actions = repair_engine.repair_ui(spec, issues)
        assert len(actions) == 1
        routes = [p.route for p in spec.ui_schema.pages]
        assert routes.count("/home") == 1
        assert "/about" in routes

    def test_repair_ui_preserves_unaffected_schemas(self, repair_engine):
        spec = _make_spec(
            ast=RequirementAST(entities=[_make_entity("User")]),
            ui_schema=UISchema(pages=[PageDefinition(route="/", title="Home", auth_required=False)]),
            api_schema=APISchema(middleware=[MiddlewareDefinition(name="jwt", middleware_type="auth")]),
            db_schema=DBSchema(tables=[TableDefinition(name="Users", columns=[ColumnDefinition(name="id", data_type="UUID", primary_key=True)])]),
        )
        original_db_tables = len(spec.db_schema.tables)
        original_ast_entities = len(spec.ast.entities)
        issues = [ValidationIssue(
            rule_id="V011", severity=Severity.ERROR, layer="semantic",
            message="Login page is missing but auth middleware is configured", affected_schema="ui",
        )]
        repair_engine.repair_ui(spec, issues)
        assert len(spec.db_schema.tables) == original_db_tables
        assert len(spec.ast.entities) == original_ast_entities


# ═══════════════════════════════════════════════════════════════════
# repair_api() — V010, V018
# ═══════════════════════════════════════════════════════════════════

class TestRepairAPI:

    def test_repair_v010_adds_crud_endpoints(self, repair_engine):
        entity = _make_entity("Product", timestamps=False)
        spec = _make_spec(
            ast=RequirementAST(entities=[entity]),
            api_schema=APISchema(endpoints=[]),
        )
        issues = [ValidationIssue(
            rule_id="V010", severity=Severity.WARNING, layer="semantic",
            message="Entity 'Product' has no CRUD API endpoints", affected_schema="api",
        )]
        actions = repair_engine.repair_api(spec, issues)
        assert len(actions) == 1
        methods = {ep.method for ep in spec.api_schema.endpoints}
        assert {"GET", "POST", "PUT", "DELETE"}.issubset(methods)

    def test_repair_v018_dedupes_endpoints(self, repair_engine):
        ep = EndpointDefinition(method="GET", path="/api/v1/users", entity="User")
        spec = _make_spec(api_schema=APISchema(endpoints=[ep, ep, ep]))
        issues = [ValidationIssue(
            rule_id="V018", severity=Severity.ERROR, layer="schema",
            message="Duplicate API endpoint 'GET:/api/v1/users' found 3 times", affected_schema="api",
        )]
        actions = repair_engine.repair_api(spec, issues)
        assert len(actions) == 1
        assert len(spec.api_schema.endpoints) == 1


# ═══════════════════════════════════════════════════════════════════
# repair_db() — V006, V008, V013, V024
# ═══════════════════════════════════════════════════════════════════

class TestRepairDB:

    def test_repair_v006_adds_missing_table(self, repair_engine):
        entity = _make_entity("Order", timestamps=False)
        spec = _make_spec(
            ast=RequirementAST(entities=[entity]),
            db_schema=DBSchema(tables=[]),
        )
        issues = [ValidationIssue(
            rule_id="V006", severity=Severity.ERROR, layer="cross_layer",
            message="Entity 'Order' has no corresponding DB table (expected 'Orders')",
            affected_schema="db",
        )]
        actions = repair_engine.repair_db(spec, issues)
        assert len(actions) == 1
        assert any(t.name == "Orders" for t in spec.db_schema.tables)

    def test_repair_v024_removes_dangling_fk(self, repair_engine):
        table = TableDefinition(name="Orders", columns=[
            ColumnDefinition(name="id", data_type="UUID", primary_key=True),
            ColumnDefinition(name="customer_id", data_type="UUID", foreign_key="Customers.id"),
        ])
        spec = _make_spec(db_schema=DBSchema(tables=[table]))
        issues = [ValidationIssue(
            rule_id="V024", severity=Severity.WARNING, layer="cross_layer",
            message="Column 'Orders.customer_id' has FK to non-existent table 'customers'",
            affected_schema="db",
        )]
        actions = repair_engine.repair_db(spec, issues)
        assert len(actions) == 1
        col = next(c for c in spec.db_schema.tables[0].columns if c.name == "customer_id")
        assert col.foreign_key is None


# ═══════════════════════════════════════════════════════════════════
# repair_auth() — V023, V007, V025
# ═══════════════════════════════════════════════════════════════════

class TestRepairAuth:

    def test_repair_v023_adds_missing_role_definition(self, repair_engine):
        spec = _make_spec(
            auth_schema=AuthSchema(
                roles=[],
                permissions=[PermissionDefinition(role="phantom", resource="User", actions=["read"])],
            ),
        )
        issues = [ValidationIssue(
            rule_id="V023", severity=Severity.ERROR, layer="cross_layer",
            message="Permission references role 'phantom' which has no RoleDefinition",
            affected_schema="auth",
        )]
        actions = repair_engine.repair_auth(spec, issues)
        assert len(actions) == 1
        assert any(r.name == "phantom" for r in spec.auth_schema.roles)

    def test_repair_v007_removes_orphaned_permission(self, repair_engine):
        spec = _make_spec(
            auth_schema=AuthSchema(
                roles=[RoleDefinition(name="admin")],
                permissions=[PermissionDefinition(role="admin", resource="Ghost", actions=["read"])],
            ),
        )
        issues = [ValidationIssue(
            rule_id="V007", severity=Severity.ERROR, layer="cross_layer",
            message="Permission for role 'admin' references non-existent entity 'Ghost'",
            affected_schema="auth",
        )]
        actions = repair_engine.repair_auth(spec, issues)
        assert len(actions) == 1
        assert len(spec.auth_schema.permissions) == 0


# ═══════════════════════════════════════════════════════════════════
# repair_business_logic() — V015, V020, V021
# ═══════════════════════════════════════════════════════════════════

class TestRepairBusinessLogic:

    def test_repair_v015_removes_invalid_rule(self, repair_engine):
        spec = _make_spec(
            business_logic=BusinessLogicSchema(
                rules=[BusinessRule(name="ghost_rule", entity="Ghost", rule_type="validation", condition="x", action="y")],
            ),
        )
        issues = [ValidationIssue(
            rule_id="V015", severity=Severity.WARNING, layer="semantic",
            message="Business rule 'ghost_rule' references non-existent entity 'Ghost'",
            affected_schema="business_logic",
        )]
        actions = repair_engine.repair_business_logic(spec, issues)
        assert len(actions) == 1
        assert len(spec.business_logic.rules) == 0

    def test_repair_v020_removes_invalid_workflow(self, repair_engine):
        spec = _make_spec(
            business_logic=BusinessLogicSchema(
                workflows=[WorkflowDefinition(name="wf_ghost", trigger="on_create", entity="Ghost")],
            ),
        )
        issues = [ValidationIssue(
            rule_id="V020", severity=Severity.WARNING, layer="semantic",
            message="Workflow 'wf_ghost' references non-existent entity 'Ghost'",
            affected_schema="business_logic",
        )]
        actions = repair_engine.repair_business_logic(spec, issues)
        assert len(actions) == 1
        assert len(spec.business_logic.workflows) == 0

    def test_repair_v021_removes_invalid_event(self, repair_engine):
        spec = _make_spec(
            business_logic=BusinessLogicSchema(
                events=[EventDefinition(name="ev_ghost", trigger_entity="Ghost", trigger_action="create")],
            ),
        )
        issues = [ValidationIssue(
            rule_id="V021", severity=Severity.WARNING, layer="semantic",
            message="Event 'ev_ghost' trigger entity 'Ghost' does not exist",
            affected_schema="business_logic",
        )]
        actions = repair_engine.repair_business_logic(spec, issues)
        assert len(actions) == 1
        assert len(spec.business_logic.events) == 0


# ═══════════════════════════════════════════════════════════════════
# Repair report structure
# ═══════════════════════════════════════════════════════════════════

class TestRepairReport:

    def test_repair_report_has_repair_id(self, repair_engine, validation_engine):
        spec = _make_spec()
        report = validation_engine.validate(
            spec.ast, spec.ui_schema, spec.api_schema,
            spec.db_schema, spec.auth_schema, spec.business_logic,
        )
        _, repair_report = repair_engine.repair(spec, report)
        assert repair_report.repair_id  # non-empty UUID string
        assert isinstance(repair_report.affected_layers, list)
        assert isinstance(repair_report.iterations_used, int)

    def test_repair_report_affected_layers_populated(self, repair_engine):
        entity = EntityNode(name="NoPK", fields=[
            FieldNode(name="email", field_type=FieldType.EMAIL),
        ], timestamps=False)
        spec = _make_spec(
            ast=RequirementAST(entities=[entity]),
            db_schema=DBSchema(tables=[TableDefinition(name="NoPKs", columns=[ColumnDefinition(name="email", data_type="VARCHAR(255)")])]),
            api_schema=APISchema(endpoints=[EndpointDefinition(method="GET", path="/api/v1/NoPKs", entity="NoPK")]),
        )
        validator = ValidationEngine()
        report = validator.validate(
            spec.ast, spec.ui_schema, spec.api_schema,
            spec.db_schema, spec.auth_schema, spec.business_logic,
        )
        _, repair_report = repair_engine.repair(spec, report)
        assert repair_report.total_repairs > 0
        assert len(repair_report.affected_layers) > 0
