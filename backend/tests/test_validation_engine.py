"""
Phase 3 — Unit tests for ValidationEngine.

Tests every validation rule (V001–V025) with minimal, focused fixtures.
"""
import pytest
from app.schemas.ast_models import (
    RequirementAST, EntityNode, FieldNode, FieldType, RelationNode, RelationType,
    FeatureNode, FeatureType, RoleNode, PermissionNode, ActionVerb,
    UISchema, APISchema, DBSchema, AuthSchema, BusinessLogicSchema,
    PageDefinition, ComponentDefinition, NavigationItem,
    EndpointDefinition, EndpointParam, MiddlewareDefinition,
    TableDefinition, ColumnDefinition,
    RoleDefinition, PermissionDefinition,
    WorkflowDefinition, WorkflowStep, BusinessRule, EventDefinition,
    ValidationIssue, Severity,
)
from app.compiler.validation_engine import ValidationEngine


# ─── Helpers ─────────────────────────────────────────────────────

def _make_entity(name="User", fields=None, timestamps=True):
    if fields is None:
        fields = [
            FieldNode(name="id", field_type=FieldType.UUID, required=True, unique=True, indexed=True),
            FieldNode(name="email", field_type=FieldType.EMAIL, required=True),
        ]
    return EntityNode(name=name, fields=fields, timestamps=timestamps)


def _make_ast(entities=None, roles=None, features=None):
    return RequirementAST(
        entities=entities or [],
        roles=roles or [],
        features=features or [],
    )


def _make_ui(pages=None, components=None, navigation=None):
    return UISchema(
        pages=pages or [],
        components=components or [],
        navigation=navigation or [],
    )


def _make_api(endpoints=None, middleware=None):
    return APISchema(
        endpoints=endpoints or [],
        middleware=middleware or [],
    )


def _make_db(tables=None):
    return DBSchema(tables=tables or [])


def _make_auth(roles=None, permissions=None):
    return AuthSchema(
        roles=roles or [],
        permissions=permissions or [],
    )


def _make_bl(workflows=None, rules=None, events=None):
    return BusinessLogicSchema(
        workflows=workflows or [],
        rules=rules or [],
        events=events or [],
    )


def _clean_spec():
    """Build a fully consistent, issue-free specification."""
    entity = _make_entity("User", fields=[
        FieldNode(name="id", field_type=FieldType.UUID, required=True, unique=True, indexed=True),
        FieldNode(name="email", field_type=FieldType.EMAIL, required=True),
        FieldNode(name="created_at", field_type=FieldType.DATETIME, required=True),
        FieldNode(name="updated_at", field_type=FieldType.DATETIME, required=True),
    ])
    ast = _make_ast(entities=[entity])
    ui = _make_ui(
        pages=[
            PageDefinition(route="/", title="Home", auth_required=False),
            PageDefinition(route="/login", title="Login", layout="auth", auth_required=False),
            PageDefinition(route="/Users", title="Users", data_sources=["/api/v1/Users"]),
        ],
        navigation=[
            NavigationItem(label="Home", route="/"),
            NavigationItem(label="Users", route="/Users"),
        ],
    )
    api = _make_api(
        endpoints=[
            EndpointDefinition(method="GET", path="/api/v1/Users", entity="User"),
            EndpointDefinition(method="POST", path="/api/v1/Users", entity="User"),
            EndpointDefinition(method="GET", path="/api/v1/Users/{id}", entity="User"),
            EndpointDefinition(method="PUT", path="/api/v1/Users/{id}", entity="User"),
            EndpointDefinition(method="DELETE", path="/api/v1/Users/{id}", entity="User"),
        ],
        middleware=[MiddlewareDefinition(name="jwt", middleware_type="auth")],
    )
    db = _make_db(tables=[
        TableDefinition(name="Users", columns=[
            ColumnDefinition(name="id", data_type="UUID", primary_key=True),
            ColumnDefinition(name="email", data_type="VARCHAR(255)"),
            ColumnDefinition(name="created_at", data_type="TIMESTAMP"),
            ColumnDefinition(name="updated_at", data_type="TIMESTAMP"),
        ]),
    ])
    auth = _make_auth(
        roles=[RoleDefinition(name="admin")],
        permissions=[PermissionDefinition(role="admin", resource="User", actions=["read", "create"])],
    )
    bl = _make_bl()
    return ast, ui, api, db, auth, bl


@pytest.fixture
def engine():
    return ValidationEngine()


# ═══════════════════════════════════════════════════════════════════
# Layer 1 — Structural (V001–V003)
# ═══════════════════════════════════════════════════════════════════

class TestStructuralValidation:

    def test_v001_valid_schemas_pass(self, engine):
        ast, ui, api, db, auth, bl = _clean_spec()
        report = engine.validate(ast, ui, api, db, auth, bl)
        v001 = [i for i in report.issues if i.rule_id == "V001"]
        assert len(v001) == 0

    def test_v002_entity_no_fields(self, engine):
        entity = EntityNode(name="Empty", fields=[], timestamps=False)
        ast = _make_ast(entities=[entity])
        report = engine.validate(ast, _make_ui(), _make_api(), _make_db(), _make_auth(), _make_bl())
        v002 = [i for i in report.issues if i.rule_id == "V002"]
        assert len(v002) == 1
        assert "Empty" in v002[0].message

    def test_v002_entity_with_fields_passes(self, engine):
        entity = _make_entity("Good", timestamps=False)
        ast = _make_ast(entities=[entity])
        db = _make_db(tables=[TableDefinition(name="Goods", columns=[ColumnDefinition(name="id", data_type="UUID", primary_key=True)])])
        api = _make_api(endpoints=[EndpointDefinition(method="GET", path="/api/v1/Goods", entity="Good")])
        report = engine.validate(ast, _make_ui(), api, db, _make_auth(), _make_bl())
        v002 = [i for i in report.issues if i.rule_id == "V002"]
        assert len(v002) == 0


# ═══════════════════════════════════════════════════════════════════
# Layer 2 — Schema (V017–V019)
# ═══════════════════════════════════════════════════════════════════

class TestSchemaValidation:

    def test_v017_duplicate_entity_names(self, engine):
        e1 = _make_entity("User", timestamps=False)
        e2 = _make_entity("User", timestamps=False)
        ast = _make_ast(entities=[e1, e2])
        report = engine.validate(ast, _make_ui(), _make_api(), _make_db(), _make_auth(), _make_bl())
        v017 = [i for i in report.issues if i.rule_id == "V017"]
        assert len(v017) == 1
        assert v017[0].severity == Severity.ERROR

    def test_v018_duplicate_endpoints(self, engine):
        ep = EndpointDefinition(method="GET", path="/api/v1/users", entity="User")
        api = _make_api(endpoints=[ep, ep])
        report = engine.validate(_make_ast(), _make_ui(), api, _make_db(), _make_auth(), _make_bl())
        v018 = [i for i in report.issues if i.rule_id == "V018"]
        assert len(v018) == 1

    def test_v019_duplicate_page_routes(self, engine):
        p1 = PageDefinition(route="/home", title="Home1")
        p2 = PageDefinition(route="/home", title="Home2")
        ui = _make_ui(pages=[p1, p2])
        report = engine.validate(_make_ast(), ui, _make_api(), _make_db(), _make_auth(), _make_bl())
        v019 = [i for i in report.issues if i.rule_id == "V019"]
        assert len(v019) == 1


# ═══════════════════════════════════════════════════════════════════
# Layer 3 — Cross-layer (V004–V007, V012–V014, V023–V025)
# ═══════════════════════════════════════════════════════════════════

class TestCrossLayerValidation:

    def test_v004_endpoint_references_invalid_entity(self, engine):
        ep = EndpointDefinition(method="GET", path="/api/v1/ghosts", entity="Ghost")
        api = _make_api(endpoints=[ep])
        report = engine.validate(_make_ast(), _make_ui(), api, _make_db(), _make_auth(), _make_bl())
        v004 = [i for i in report.issues if i.rule_id == "V004"]
        assert len(v004) == 1
        assert "Ghost" in v004[0].message

    def test_v005_page_data_source_missing_endpoint(self, engine):
        page = PageDefinition(route="/dash", title="Dash", data_sources=["/api/v1/missing"])
        ui = _make_ui(pages=[page])
        report = engine.validate(_make_ast(), ui, _make_api(), _make_db(), _make_auth(), _make_bl())
        v005 = [i for i in report.issues if i.rule_id == "V005"]
        assert len(v005) >= 1

    def test_v006_missing_db_table_for_entity(self, engine):
        entity = _make_entity("Product", timestamps=False)
        ast = _make_ast(entities=[entity])
        api = _make_api(endpoints=[EndpointDefinition(method="GET", path="/api/v1/Products", entity="Product")])
        report = engine.validate(ast, _make_ui(), api, _make_db(), _make_auth(), _make_bl())
        v006 = [i for i in report.issues if i.rule_id == "V006"]
        assert len(v006) == 1

    def test_v007_permission_references_invalid_entity(self, engine):
        auth = _make_auth(
            roles=[RoleDefinition(name="admin")],
            permissions=[PermissionDefinition(role="admin", resource="Ghost", actions=["read"])],
        )
        report = engine.validate(_make_ast(), _make_ui(), _make_api(), _make_db(), auth, _make_bl())
        v007 = [i for i in report.issues if i.rule_id == "V007"]
        assert len(v007) == 1

    def test_v023_permission_role_has_no_definition(self, engine):
        auth = _make_auth(
            roles=[],  # no role definitions
            permissions=[PermissionDefinition(role="phantom", resource="User", actions=["read"])],
        )
        entity = _make_entity("User", timestamps=False)
        ast = _make_ast(entities=[entity])
        db = _make_db(tables=[TableDefinition(name="Users", columns=[ColumnDefinition(name="id", data_type="UUID", primary_key=True)])])
        api = _make_api(endpoints=[EndpointDefinition(method="GET", path="/api/v1/Users", entity="User")])
        report = engine.validate(ast, _make_ui(), api, db, auth, _make_bl())
        v023 = [i for i in report.issues if i.rule_id == "V023"]
        assert len(v023) == 1
        assert "phantom" in v023[0].message

    def test_v024_fk_references_missing_table(self, engine):
        table = TableDefinition(name="Orders", columns=[
            ColumnDefinition(name="id", data_type="UUID", primary_key=True),
            ColumnDefinition(name="customer_id", data_type="UUID", foreign_key="Customers.id"),
        ])
        db = _make_db(tables=[table])
        report = engine.validate(_make_ast(), _make_ui(), _make_api(), db, _make_auth(), _make_bl())
        v024 = [i for i in report.issues if i.rule_id == "V024"]
        assert len(v024) == 1

    def test_v025_endpoint_requires_undefined_role(self, engine):
        ep = EndpointDefinition(method="GET", path="/api/v1/secret", required_roles=["superadmin"])
        api = _make_api(endpoints=[ep])
        report = engine.validate(_make_ast(), _make_ui(), api, _make_db(), _make_auth(), _make_bl())
        v025 = [i for i in report.issues if i.rule_id == "V025"]
        assert len(v025) == 1


# ═══════════════════════════════════════════════════════════════════
# Layer 4 — Semantic (V008–V011, V015–V016, V020–V022)
# ═══════════════════════════════════════════════════════════════════

class TestSemanticValidation:

    def test_v008_entity_missing_pk(self, engine):
        entity = EntityNode(name="NoPK", fields=[
            FieldNode(name="email", field_type=FieldType.EMAIL),
        ], timestamps=False)
        ast = _make_ast(entities=[entity])
        db = _make_db(tables=[TableDefinition(name="NoPKs", columns=[ColumnDefinition(name="email", data_type="VARCHAR(255)")])])
        api = _make_api(endpoints=[EndpointDefinition(method="GET", path="/api/v1/NoPKs", entity="NoPK")])
        report = engine.validate(ast, _make_ui(), api, db, _make_auth(), _make_bl())
        v008 = [i for i in report.issues if i.rule_id == "V008"]
        assert len(v008) == 1

    def test_v009_entity_missing_timestamps(self, engine):
        entity = EntityNode(name="Timed", fields=[
            FieldNode(name="id", field_type=FieldType.UUID, required=True),
        ], timestamps=True)  # timestamps=True but no created_at/updated_at
        ast = _make_ast(entities=[entity])
        db = _make_db(tables=[TableDefinition(name="Timeds", columns=[ColumnDefinition(name="id", data_type="UUID", primary_key=True)])])
        api = _make_api(endpoints=[EndpointDefinition(method="GET", path="/api/v1/Timeds", entity="Timed")])
        report = engine.validate(ast, _make_ui(), api, db, _make_auth(), _make_bl())
        v009 = [i for i in report.issues if i.rule_id == "V009"]
        assert len(v009) == 1

    def test_v010_entity_missing_crud_endpoints(self, engine):
        entity = _make_entity("Orphan", timestamps=False)
        ast = _make_ast(entities=[entity])
        db = _make_db(tables=[TableDefinition(name="Orphans", columns=[ColumnDefinition(name="id", data_type="UUID", primary_key=True)])])
        report = engine.validate(ast, _make_ui(), _make_api(), db, _make_auth(), _make_bl())
        v010 = [i for i in report.issues if i.rule_id == "V010"]
        assert len(v010) == 1

    def test_v011_missing_login_page_with_auth(self, engine):
        api = _make_api(
            middleware=[MiddlewareDefinition(name="jwt", middleware_type="auth")],
        )
        ui = _make_ui(pages=[PageDefinition(route="/", title="Home", auth_required=False)])
        report = engine.validate(_make_ast(), ui, api, _make_db(), _make_auth(), _make_bl())
        v011 = [i for i in report.issues if i.rule_id == "V011"]
        assert len(v011) == 1

    def test_v015_business_rule_invalid_entity(self, engine):
        bl = _make_bl(rules=[BusinessRule(name="ghost_rule", entity="Ghost", rule_type="validation", condition="x", action="y")])
        report = engine.validate(_make_ast(), _make_ui(), _make_api(), _make_db(), _make_auth(), bl)
        v015 = [i for i in report.issues if i.rule_id == "V015"]
        assert len(v015) == 1

    def test_v016_nav_item_missing_route(self, engine):
        ui = _make_ui(
            pages=[PageDefinition(route="/", title="Home", auth_required=False)],
            navigation=[NavigationItem(label="Ghost", route="/nonexistent")],
        )
        report = engine.validate(_make_ast(), ui, _make_api(), _make_db(), _make_auth(), _make_bl())
        v016 = [i for i in report.issues if i.rule_id == "V016"]
        assert len(v016) == 1

    def test_v020_workflow_invalid_entity(self, engine):
        bl = _make_bl(workflows=[WorkflowDefinition(name="wf1", trigger="on_create", entity="Ghost")])
        report = engine.validate(_make_ast(), _make_ui(), _make_api(), _make_db(), _make_auth(), bl)
        v020 = [i for i in report.issues if i.rule_id == "V020"]
        assert len(v020) == 1

    def test_v021_event_trigger_invalid_entity(self, engine):
        bl = _make_bl(events=[EventDefinition(name="ev1", trigger_entity="Ghost", trigger_action="create")])
        report = engine.validate(_make_ast(), _make_ui(), _make_api(), _make_db(), _make_auth(), bl)
        v021 = [i for i in report.issues if i.rule_id == "V021"]
        assert len(v021) == 1

    def test_v022_component_invalid_entity(self, engine):
        ui = _make_ui(components=[ComponentDefinition(name="GhostList", component_type="table", entity="Ghost")])
        report = engine.validate(_make_ast(), ui, _make_api(), _make_db(), _make_auth(), _make_bl())
        v022 = [i for i in report.issues if i.rule_id == "V022"]
        assert len(v022) == 1


# ═══════════════════════════════════════════════════════════════════
# Clean spec should pass all validations
# ═══════════════════════════════════════════════════════════════════

class TestCleanSpec:

    def test_clean_spec_has_no_errors(self, engine):
        ast, ui, api, db, auth, bl = _clean_spec()
        report = engine.validate(ast, ui, api, db, auth, bl)
        errors = [i for i in report.issues if i.severity == Severity.ERROR]
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"
        assert report.passed is True

    def test_validation_report_structure(self, engine):
        ast, ui, api, db, auth, bl = _clean_spec()
        report = engine.validate(ast, ui, api, db, auth, bl)
        assert report.total_issues >= 0
        assert report.validation_time_ms >= 0
        assert isinstance(report.issues, list)
