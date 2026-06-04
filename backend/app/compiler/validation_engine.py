"""
Phase 3 — Production Validation Engine.

Five validation layers executed in order:
    1. Structural  — JSON / Pydantic model integrity  (V001-V003)
    2. Schema      — Duplicates, field constraints     (V017-V019)
    3. Cross-layer — UI↔API, API↔DB, Role↔Perm, …     (V004-V007, V012-V014, V023-V025)
    4. Semantic    — Domain rules, missing refs         (V008-V011, V015-V016, V020-V022)

All rules are deterministic and side-effect-free.
"""
import time
from collections import Counter
from typing import Optional

from app.schemas.ast_models import (
    RequirementAST,
    UISchema,
    APISchema,
    DBSchema,
    AuthSchema,
    BusinessLogicSchema,
    ValidationReport,
    ValidationIssue,
    Severity,
)


class ValidationEngine:
    """
    Four-layer validation: Structural, Schema, Cross-layer, Semantic.
    """

    # ──────────────────────────────────────────────────────────────
    # Public entry point
    # ──────────────────────────────────────────────────────────────

    def validate(
        self,
        ast: RequirementAST,
        ui: UISchema,
        api: APISchema,
        db: DBSchema,
        auth: AuthSchema,
        business_logic: BusinessLogicSchema,
        graph_issues: Optional[list[ValidationIssue]] = None,
    ) -> ValidationReport:

        start_time = time.time()
        issues: list[ValidationIssue] = []

        # Include issues from the consistency engine (graph validation)
        if graph_issues:
            issues.extend(graph_issues)

        # Layer 1 — Structural (Pydantic / JSON integrity)
        issues.extend(self._validate_structural(ast, ui, api, db, auth, business_logic))

        # Layer 2 — Schema (duplicates, constraints)
        issues.extend(self._validate_schema(ast, ui, api, db))

        # Layer 3 — Cross-layer consistency
        issues.extend(self._validate_cross_layer(ast, ui, api, db, auth, business_logic))

        # Layer 4 — Semantic (domain rules)
        issues.extend(self._validate_semantic(ast, ui, api, db, auth, business_logic))

        return ValidationReport(
            issues=issues,
            validation_time_ms=int((time.time() - start_time) * 1000)
        )

    # ──────────────────────────────────────────────────────────────
    # Layer 1 — Structural Validation
    # ──────────────────────────────────────────────────────────────

    def _validate_structural(
        self,
        ast: RequirementAST,
        ui: UISchema,
        api: APISchema,
        db: DBSchema,
        auth: AuthSchema,
        bl: BusinessLogicSchema,
    ) -> list[ValidationIssue]:
        """V001-V003: Verify Pydantic models are well-formed."""
        issues: list[ValidationIssue] = []

        # V001: Schemas must be valid (they are if we got here — Pydantic already validated).
        # We still verify serialization round-trips cleanly.
        for label, schema in [("ui", ui), ("api", api), ("db", db), ("auth", auth), ("business_logic", bl)]:
            try:
                schema.model_dump()
            except Exception as exc:
                issues.append(ValidationIssue(
                    rule_id="V001",
                    severity=Severity.ERROR,
                    layer="structural",
                    message=f"{label} schema failed JSON serialization: {exc}",
                    affected_schema=label,
                ))

        # V002: Every entity must have at least one field
        for entity in ast.entities:
            if not entity.fields:
                issues.append(ValidationIssue(
                    rule_id="V002",
                    severity=Severity.ERROR,
                    layer="structural",
                    message=f"Entity '{entity.name}' has no fields defined",
                    affected_schema="ast",
                    affected_path=f"entities.[name='{entity.name}'].fields",
                ))

        # V003: Required fields must not have None as default when required=True
        for entity in ast.entities:
            for field in entity.fields:
                if field.required and field.field_type is None:
                    issues.append(ValidationIssue(
                        rule_id="V003",
                        severity=Severity.ERROR,
                        layer="structural",
                        message=f"Field '{field.name}' on entity '{entity.name}' is required but has null type",
                        affected_schema="ast",
                        affected_path=f"entities.[name='{entity.name}'].fields.[name='{field.name}']",
                    ))

        return issues

    # ──────────────────────────────────────────────────────────────
    # Layer 2 — Schema Validation (duplicates / constraints)
    # ──────────────────────────────────────────────────────────────

    def _validate_schema(
        self,
        ast: RequirementAST,
        ui: UISchema,
        api: APISchema,
        db: DBSchema,
    ) -> list[ValidationIssue]:
        """V017-V019: No duplicate names / paths / routes."""
        issues: list[ValidationIssue] = []

        # V017: No duplicate entity names
        entity_names = [e.name.lower() for e in ast.entities]
        for name, count in Counter(entity_names).items():
            if count > 1:
                issues.append(ValidationIssue(
                    rule_id="V017",
                    severity=Severity.ERROR,
                    layer="schema",
                    message=f"Duplicate entity name '{name}' found {count} times",
                    affected_schema="ast",
                    affected_path="entities",
                ))

        # V018: No duplicate endpoint method+path
        ep_keys = [f"{ep.method}:{ep.path}" for ep in api.endpoints]
        for key, count in Counter(ep_keys).items():
            if count > 1:
                issues.append(ValidationIssue(
                    rule_id="V018",
                    severity=Severity.ERROR,
                    layer="schema",
                    message=f"Duplicate API endpoint '{key}' found {count} times",
                    affected_schema="api",
                    affected_path="endpoints",
                ))

        # V019: No duplicate page routes
        page_routes = [p.route for p in ui.pages]
        for route, count in Counter(page_routes).items():
            if count > 1:
                issues.append(ValidationIssue(
                    rule_id="V019",
                    severity=Severity.ERROR,
                    layer="schema",
                    message=f"Duplicate page route '{route}' found {count} times",
                    affected_schema="ui",
                    affected_path="pages",
                ))

        return issues

    # ──────────────────────────────────────────────────────────────
    # Layer 3 — Cross-layer Consistency
    # ──────────────────────────────────────────────────────────────

    def _validate_cross_layer(
        self,
        ast: RequirementAST,
        ui: UISchema,
        api: APISchema,
        db: DBSchema,
        auth: AuthSchema,
        bl: BusinessLogicSchema,
    ) -> list[ValidationIssue]:
        """V004-V007, V012-V014, V023-V025."""
        issues: list[ValidationIssue] = []
        entity_names_lower = {e.name.lower() for e in ast.entities}
        table_names_lower = {t.name.lower() for t in db.tables}
        auth_role_names = {r.name.lower() for r in auth.roles}
        api_get_paths = {ep.path for ep in api.endpoints if ep.method == "GET"}

        # V004: API endpoints reference valid entities
        for ep in api.endpoints:
            if ep.entity and ep.entity.lower() not in entity_names_lower:
                issues.append(ValidationIssue(
                    rule_id="V004",
                    severity=Severity.ERROR,
                    layer="cross_layer",
                    message=f"API endpoint '{ep.method} {ep.path}' references non-existent entity '{ep.entity}'",
                    affected_schema="api",
                    affected_path=f"endpoints.[path='{ep.path}']",
                ))

        # V005: UI page data_sources reference existing API GET endpoints
        for page in ui.pages:
            for ds in page.data_sources:
                if ds not in api_get_paths:
                    issues.append(ValidationIssue(
                        rule_id="V005",
                        severity=Severity.WARNING,
                        layer="cross_layer",
                        message=f"Page '{page.route}' references data source '{ds}' with no matching GET endpoint",
                        affected_schema="ui",
                        affected_path=f"pages.[route='{page.route}'].data_sources",
                    ))

        # V006: DB tables exist for all entities
        for entity in ast.entities:
            expected_table = f"{entity.name}s".lower()
            if expected_table not in table_names_lower:
                issues.append(ValidationIssue(
                    rule_id="V006",
                    severity=Severity.ERROR,
                    layer="cross_layer",
                    message=f"Entity '{entity.name}' has no corresponding DB table (expected '{entity.name}s')",
                    affected_schema="db",
                    affected_path="tables",
                ))

        # V007: Auth permissions reference valid entities
        for perm in auth.permissions:
            if perm.resource.lower() not in entity_names_lower:
                issues.append(ValidationIssue(
                    rule_id="V007",
                    severity=Severity.ERROR,
                    layer="cross_layer",
                    message=f"Permission for role '{perm.role}' references non-existent entity '{perm.resource}'",
                    affected_schema="auth",
                    affected_path=f"permissions.[role='{perm.role}']",
                ))

        # V012: UI↔API — every page data_source has a matching GET endpoint
        # (already covered by V005 above, but V012 is the cross-layer specific label)
        for page in ui.pages:
            for ds in page.data_sources:
                matching = [ep for ep in api.endpoints if ep.path == ds and ep.method == "GET"]
                if not matching:
                    # Only add if V005 didn't already fire for this
                    existing_v005 = any(
                        i.rule_id == "V005" and ds in i.message
                        for i in issues
                    )
                    if not existing_v005:
                        issues.append(ValidationIssue(
                            rule_id="V012",
                            severity=Severity.WARNING,
                            layer="cross_layer",
                            message=f"UI page '{page.route}' data source '{ds}' has no matching API GET endpoint",
                            affected_schema="ui",
                            affected_path=f"pages.[route='{page.route}'].data_sources",
                        ))

        # V013: API↔DB — every entity with endpoints has a matching DB table
        entities_with_endpoints = {ep.entity.lower() for ep in api.endpoints if ep.entity}
        for ent_name in entities_with_endpoints:
            expected_table = f"{ent_name}s"
            if expected_table not in table_names_lower:
                # Avoid duplicate with V006
                existing_v006 = any(
                    i.rule_id == "V006" and ent_name in i.message.lower()
                    for i in issues
                )
                if not existing_v006:
                    issues.append(ValidationIssue(
                        rule_id="V013",
                        severity=Severity.ERROR,
                        layer="cross_layer",
                        message=f"Entity '{ent_name}' has API endpoints but no DB table",
                        affected_schema="db",
                        affected_path="tables",
                    ))

        # V014: Role↔Permission — every permission resource is a valid entity
        for perm in auth.permissions:
            if perm.resource.lower() not in entity_names_lower:
                existing = any(i.rule_id == "V007" and perm.resource in i.message for i in issues)
                if not existing:
                    issues.append(ValidationIssue(
                        rule_id="V014",
                        severity=Severity.WARNING,
                        layer="cross_layer",
                        message=f"Permission resource '{perm.resource}' for role '{perm.role}' is not a known entity",
                        affected_schema="auth",
                        affected_path=f"permissions.[role='{perm.role}']",
                    ))

        # V023: Auth role definitions cover all roles referenced in permissions
        roles_in_permissions = {p.role.lower() for p in auth.permissions}
        for role_name in roles_in_permissions:
            if role_name not in auth_role_names:
                issues.append(ValidationIssue(
                    rule_id="V023",
                    severity=Severity.ERROR,
                    layer="cross_layer",
                    message=f"Permission references role '{role_name}' which has no RoleDefinition",
                    affected_schema="auth",
                    affected_path=f"permissions.[role='{role_name}']",
                ))

        # V024: Foreign key targets reference existing tables
        for table in db.tables:
            for col in table.columns:
                if col.foreign_key:
                    fk_table = col.foreign_key.split(".")[0].lower()
                    if fk_table not in table_names_lower:
                        issues.append(ValidationIssue(
                            rule_id="V024",
                            severity=Severity.WARNING,
                            layer="cross_layer",
                            message=f"Column '{table.name}.{col.name}' has FK to non-existent table '{fk_table}'",
                            affected_schema="db",
                            affected_path=f"tables.[name='{table.name}'].columns.[name='{col.name}']",
                        ))

        # V025: Endpoint required_roles match defined auth roles
        for ep in api.endpoints:
            for role in ep.required_roles:
                if role.lower() not in auth_role_names:
                    issues.append(ValidationIssue(
                        rule_id="V025",
                        severity=Severity.WARNING,
                        layer="cross_layer",
                        message=f"Endpoint '{ep.method} {ep.path}' requires undefined role '{role}'",
                        affected_schema="api",
                        affected_path=f"endpoints.[path='{ep.path}'].required_roles",
                    ))

        return issues

    # ──────────────────────────────────────────────────────────────
    # Layer 4 — Semantic Validation
    # ──────────────────────────────────────────────────────────────

    def _validate_semantic(
        self,
        ast: RequirementAST,
        ui: UISchema,
        api: APISchema,
        db: DBSchema,
        auth: AuthSchema,
        bl: BusinessLogicSchema,
    ) -> list[ValidationIssue]:
        """V008-V011, V015-V016, V020-V022."""
        issues: list[ValidationIssue] = []
        entity_names_lower = {e.name.lower() for e in ast.entities}
        page_routes = {p.route for p in ui.pages}

        # V008: Every entity must have a primary key (id)
        for entity in ast.entities:
            field_names = [f.name for f in entity.fields]
            if "id" not in field_names:
                issues.append(ValidationIssue(
                    rule_id="V008",
                    severity=Severity.ERROR,
                    layer="semantic",
                    message=f"Entity '{entity.name}' is missing a primary key (id)",
                    affected_schema="ast",
                    affected_path=f"entities.[name='{entity.name}'].fields",
                    suggestion="Add a UUID 'id' field as the first field",
                ))

        # V009: Entities with timestamps=True must have created_at/updated_at
        for entity in ast.entities:
            if entity.timestamps:
                field_names = [f.name for f in entity.fields]
                if "created_at" not in field_names or "updated_at" not in field_names:
                    issues.append(ValidationIssue(
                        rule_id="V009",
                        severity=Severity.WARNING,
                        layer="semantic",
                        message=f"Entity '{entity.name}' has timestamps=True but is missing timestamp fields",
                        affected_schema="ast",
                        affected_path=f"entities.[name='{entity.name}'].fields",
                        suggestion="Add 'created_at' and 'updated_at' DATETIME fields",
                    ))

        # V010: CRUD endpoints must exist for every entity
        for entity in ast.entities:
            entity_paths = [ep.path for ep in api.endpoints if ep.entity and ep.entity.lower() == entity.name.lower()]
            if not entity_paths:
                issues.append(ValidationIssue(
                    rule_id="V010",
                    severity=Severity.WARNING,
                    layer="semantic",
                    message=f"Entity '{entity.name}' has no CRUD API endpoints",
                    affected_schema="api",
                    affected_path="endpoints",
                    suggestion=f"Add GET/POST/PUT/DELETE endpoints for /api/v1/{entity.name}s",
                ))

        # V011: Login page must exist if auth is configured
        if api.middleware and any(m.middleware_type == "auth" for m in api.middleware):
            if not any(p.route == "/login" for p in ui.pages):
                issues.append(ValidationIssue(
                    rule_id="V011",
                    severity=Severity.ERROR,
                    layer="semantic",
                    message="Login page is missing but auth middleware is configured",
                    affected_schema="ui",
                    affected_path="pages",
                    suggestion="Add a PageDefinition with route='/login'",
                ))

        # V015: Business rules reference valid entities
        for rule in bl.rules:
            if rule.entity.lower() not in entity_names_lower:
                issues.append(ValidationIssue(
                    rule_id="V015",
                    severity=Severity.WARNING,
                    layer="semantic",
                    message=f"Business rule '{rule.name}' references non-existent entity '{rule.entity}'",
                    affected_schema="business_logic",
                    affected_path=f"rules.[name='{rule.name}']",
                ))

        # V016: Navigation items reference valid page routes
        for nav in ui.navigation:
            if nav.route not in page_routes:
                issues.append(ValidationIssue(
                    rule_id="V016",
                    severity=Severity.WARNING,
                    layer="semantic",
                    message=f"Navigation item '{nav.label}' points to non-existent route '{nav.route}'",
                    affected_schema="ui",
                    affected_path=f"navigation.[label='{nav.label}']",
                ))

        # V020: Workflow entity references are valid
        for wf in bl.workflows:
            if wf.entity and wf.entity.lower() not in entity_names_lower:
                issues.append(ValidationIssue(
                    rule_id="V020",
                    severity=Severity.WARNING,
                    layer="semantic",
                    message=f"Workflow '{wf.name}' references non-existent entity '{wf.entity}'",
                    affected_schema="business_logic",
                    affected_path=f"workflows.[name='{wf.name}']",
                ))

        # V021: Event trigger entities exist
        for event in bl.events:
            if event.trigger_entity.lower() not in entity_names_lower:
                issues.append(ValidationIssue(
                    rule_id="V021",
                    severity=Severity.WARNING,
                    layer="semantic",
                    message=f"Event '{event.name}' trigger entity '{event.trigger_entity}' does not exist",
                    affected_schema="business_logic",
                    affected_path=f"events.[name='{event.name}']",
                ))

        # V022: Component entity bindings are valid
        for comp in ui.components:
            if comp.entity and comp.entity.lower() not in entity_names_lower:
                issues.append(ValidationIssue(
                    rule_id="V022",
                    severity=Severity.WARNING,
                    layer="semantic",
                    message=f"Component '{comp.name}' is bound to non-existent entity '{comp.entity}'",
                    affected_schema="ui",
                    affected_path=f"components.[name='{comp.name}']",
                ))

        return issues
