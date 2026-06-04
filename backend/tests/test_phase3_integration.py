"""
Phase 3 — Integration tests.

End-to-end: broken spec → validate → repair → revalidate → assert clean.
"""
import pytest
from app.schemas.ast_models import (
    RequirementAST, EntityNode, FieldNode, FieldType,
    UISchema, APISchema, DBSchema, AuthSchema, BusinessLogicSchema,
    CompiledSpecification,
    PageDefinition, NavigationItem, ComponentDefinition,
    EndpointDefinition, EndpointParam, MiddlewareDefinition,
    TableDefinition, ColumnDefinition,
    RoleDefinition, PermissionDefinition,
    WorkflowDefinition, WorkflowStep, BusinessRule, EventDefinition,
    Severity,
)
from app.compiler.validation_engine import ValidationEngine
from app.compiler.repair_engine import RepairEngine


@pytest.fixture
def validator():
    return ValidationEngine()


@pytest.fixture
def repairer():
    return RepairEngine()


def _broken_spec() -> CompiledSpecification:
    """
    Build a spec with multiple defects across every layer:
    - Entity missing PK (V008)
    - Entity missing timestamps (V009)
    - Missing DB table (V006)
    - Missing CRUD endpoints (V010)
    - Missing login page with auth (V011)
    - Business rule referencing non-existent entity (V015)
    - Workflow referencing non-existent entity (V020)
    - Navigation pointing to missing route (V016)
    - Permission referencing non-existent entity (V007)
    - Duplicate page route (V019)
    """
    entity = EntityNode(
        name="Product",
        fields=[
            FieldNode(name="name", field_type=FieldType.STRING, required=True),
            FieldNode(name="price", field_type=FieldType.MONEY, required=True),
        ],
        timestamps=True,  # but no created_at/updated_at → V009
        # no id field → V008
    )

    return CompiledSpecification(
        ast=RequirementAST(entities=[entity]),
        ui_schema=UISchema(
            pages=[
                PageDefinition(route="/", title="Home", auth_required=False),
                PageDefinition(route="/products", title="Products"),
                PageDefinition(route="/products", title="Products Dup"),  # V019 duplicate
            ],
            navigation=[
                NavigationItem(label="Home", route="/"),
                NavigationItem(label="Settings", route="/settings"),  # V016 — /settings doesn't exist
            ],
        ),
        api_schema=APISchema(
            endpoints=[],  # V010 — no CRUD endpoints
            middleware=[MiddlewareDefinition(name="jwt", middleware_type="auth")],  # V011 — no login page
        ),
        db_schema=DBSchema(tables=[]),  # V006 — no tables
        auth_schema=AuthSchema(
            roles=[RoleDefinition(name="admin")],
            permissions=[
                PermissionDefinition(role="admin", resource="Ghost", actions=["read"]),  # V007
            ],
        ),
        business_logic=BusinessLogicSchema(
            rules=[BusinessRule(name="ghost_check", entity="Ghost", rule_type="validation", condition="x>0", action="reject")],  # V015
            workflows=[WorkflowDefinition(name="wf_ghost", trigger="on_create", entity="Ghost")],  # V020
            events=[EventDefinition(name="ev_ghost", trigger_entity="Ghost", trigger_action="create")],  # V021
        ),
    )


# ═══════════════════════════════════════════════════════════════════
# End-to-End: Broken → Validate → Repair → Clean
# ═══════════════════════════════════════════════════════════════════

class TestEndToEnd:

    def test_broken_spec_has_errors(self, validator):
        spec = _broken_spec()
        report = validator.validate(
            spec.ast, spec.ui_schema, spec.api_schema,
            spec.db_schema, spec.auth_schema, spec.business_logic,
        )
        assert not report.passed
        assert report.errors > 0
        assert report.total_issues > 0

    def test_repair_fixes_broken_spec(self, validator, repairer):
        spec = _broken_spec()
        # First validate
        report = validator.validate(
            spec.ast, spec.ui_schema, spec.api_schema,
            spec.db_schema, spec.auth_schema, spec.business_logic,
        )
        assert not report.passed

        # Repair
        repaired, repair_report = repairer.repair(spec, report, max_iterations=3)

        # Verify repairs happened
        assert repair_report.total_repairs > 0
        assert repair_report.repair_id  # UUID present
        assert len(repair_report.affected_layers) > 0
        assert repair_report.iterations_used >= 1

        # Revalidate the repaired spec
        final_report = validator.validate(
            repaired.ast, repaired.ui_schema, repaired.api_schema,
            repaired.db_schema, repaired.auth_schema, repaired.business_logic,
        )
        errors = [i for i in final_report.issues if i.severity == Severity.ERROR]
        assert len(errors) == 0, f"Remaining errors after repair: {[e.message for e in errors]}"

    def test_repair_report_structure(self, validator, repairer):
        spec = _broken_spec()
        report = validator.validate(
            spec.ast, spec.ui_schema, spec.api_schema,
            spec.db_schema, spec.auth_schema, spec.business_logic,
        )
        _, repair_report = repairer.repair(spec, report)

        # Check report format matches the spec
        data = repair_report.model_dump()
        assert "repair_id" in data
        assert "affected_layers" in data
        assert "repairs" in data
        assert "unresolvable" in data
        assert "iterations_used" in data
        assert "revalidation_passed" in data

        # Each repair action has structured changes
        for action in repair_report.repairs:
            assert action.issue_rule_id
            assert action.action_type
            assert action.target_schema
            assert action.description


# ═══════════════════════════════════════════════════════════════════
# Multi-Iteration Convergence
# ═══════════════════════════════════════════════════════════════════

class TestConvergence:

    def test_multi_iteration_repair_converges(self, validator, repairer):
        """Repairing an AST defect may trigger follow-on DB/API issues that need another pass."""
        spec = _broken_spec()
        report = validator.validate(
            spec.ast, spec.ui_schema, spec.api_schema,
            spec.db_schema, spec.auth_schema, spec.business_logic,
        )
        repaired, repair_report = repairer.repair(spec, report, max_iterations=5)
        # Should converge within 5 iterations
        assert repair_report.iterations_used <= 5
        assert repair_report.total_repairs > 0


# ═══════════════════════════════════════════════════════════════════
# Idempotency: Clean Spec → Repair → Zero Changes
# ═══════════════════════════════════════════════════════════════════

class TestIdempotency:

    def test_clean_spec_repair_is_noop(self, validator, repairer):
        """Repairing an already-clean spec should produce zero repairs."""
        entity = EntityNode(name="User", fields=[
            FieldNode(name="id", field_type=FieldType.UUID, required=True, unique=True, indexed=True),
            FieldNode(name="email", field_type=FieldType.EMAIL, required=True),
            FieldNode(name="created_at", field_type=FieldType.DATETIME, required=True),
            FieldNode(name="updated_at", field_type=FieldType.DATETIME, required=True),
        ], timestamps=True)
        spec = CompiledSpecification(
            ast=RequirementAST(entities=[entity]),
            ui_schema=UISchema(
                pages=[
                    PageDefinition(route="/", title="Home", auth_required=False),
                    PageDefinition(route="/login", title="Login", layout="auth", auth_required=False),
                    PageDefinition(route="/Users", title="Users", data_sources=["/api/v1/Users"]),
                ],
                navigation=[
                    NavigationItem(label="Home", route="/"),
                    NavigationItem(label="Users", route="/Users"),
                ],
            ),
            api_schema=APISchema(
                endpoints=[
                    EndpointDefinition(method="GET", path="/api/v1/Users", entity="User"),
                    EndpointDefinition(method="POST", path="/api/v1/Users", entity="User"),
                    EndpointDefinition(method="GET", path="/api/v1/Users/{id}", entity="User"),
                    EndpointDefinition(method="PUT", path="/api/v1/Users/{id}", entity="User"),
                    EndpointDefinition(method="DELETE", path="/api/v1/Users/{id}", entity="User"),
                ],
                middleware=[MiddlewareDefinition(name="jwt", middleware_type="auth")],
            ),
            db_schema=DBSchema(tables=[
                TableDefinition(name="Users", columns=[
                    ColumnDefinition(name="id", data_type="UUID", primary_key=True),
                    ColumnDefinition(name="email", data_type="VARCHAR(255)"),
                    ColumnDefinition(name="created_at", data_type="TIMESTAMP"),
                    ColumnDefinition(name="updated_at", data_type="TIMESTAMP"),
                ]),
            ]),
            auth_schema=AuthSchema(
                roles=[RoleDefinition(name="admin")],
                permissions=[PermissionDefinition(role="admin", resource="User", actions=["read"])],
            ),
            business_logic=BusinessLogicSchema(),
        )

        report = validator.validate(
            spec.ast, spec.ui_schema, spec.api_schema,
            spec.db_schema, spec.auth_schema, spec.business_logic,
        )
        assert report.passed, f"Clean spec should pass: {[i.message for i in report.issues if i.severity == Severity.ERROR]}"

        repaired, repair_report = repairer.repair(spec, report)
        assert repair_report.total_repairs == 0


# ═══════════════════════════════════════════════════════════════════
# Failure Scenarios: Unresolvable Issues
# ═══════════════════════════════════════════════════════════════════

class TestFailureScenarios:

    def test_unrepairable_issues_in_unresolvable(self, validator, repairer):
        """Issues from the graph layer (affected_schema='graph') have no repair handler."""
        from app.schemas.ast_models import ValidationIssue, ValidationReport
        spec = CompiledSpecification()
        report = ValidationReport(issues=[
            ValidationIssue(
                rule_id="G001",
                severity=Severity.ERROR,
                layer="cross_layer",
                message="Edge source missing: entity:phantom",
                affected_schema="graph",
            ),
        ])
        _, repair_report = repairer.repair(spec, report)
        assert len(repair_report.unresolvable) >= 1
        assert any(u.rule_id == "G001" for u in repair_report.unresolvable)

    def test_original_spec_not_mutated(self, validator, repairer):
        """The original spec should be deep-copied, not mutated."""
        spec = _broken_spec()
        original_entity_field_count = len(spec.ast.entities[0].fields)
        original_page_count = len(spec.ui_schema.pages)

        report = validator.validate(
            spec.ast, spec.ui_schema, spec.api_schema,
            spec.db_schema, spec.auth_schema, spec.business_logic,
        )
        repaired, _ = repairer.repair(spec, report)

        # Original should be unchanged
        assert len(spec.ast.entities[0].fields) == original_entity_field_count
        assert len(spec.ui_schema.pages) == original_page_count
        # Repaired should be different
        assert len(repaired.ast.entities[0].fields) != original_entity_field_count or \
               len(repaired.ui_schema.pages) != original_page_count


# ═══════════════════════════════════════════════════════════════════
# Validation Report Format
# ═══════════════════════════════════════════════════════════════════

class TestValidationReportFormat:

    def test_validation_report_json_structure(self, validator):
        spec = _broken_spec()
        report = validator.validate(
            spec.ast, spec.ui_schema, spec.api_schema,
            spec.db_schema, spec.auth_schema, spec.business_logic,
        )
        data = report.model_dump()
        # Matches the spec: {"valid": false, "errors": [...]}
        assert "passed" in data  # "valid" equivalent
        assert "issues" in data  # "errors" equivalent
        assert data["passed"] is False
        assert isinstance(data["issues"], list)
        assert len(data["issues"]) > 0

        # Each issue has required fields
        for issue in data["issues"]:
            assert "rule_id" in issue
            assert "severity" in issue
            assert "layer" in issue
            assert "message" in issue
            assert "affected_schema" in issue
