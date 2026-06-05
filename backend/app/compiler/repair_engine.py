"""
Phase 3 — Intelligent Repair Engine.

Invariants:
    1. Never regenerate the entire configuration.
    2. Repair only the affected layer.
    3. Preserve unaffected schemas (deep-copy before mutation).
    4. Revalidate after every repair iteration.

Each ``repair_*()`` method receives the *mutable* spec and the subset of
issues whose ``affected_schema`` matches that layer, applies targeted fixes,
and returns a list of ``RepairAction`` records.
"""
import time
from uuid import uuid4

from app.schemas.ast_models import (
    CompiledSpecification,
    ValidationReport,
    ValidationIssue,
    RepairReport,
    RepairAction,
    Severity,
    EndpointDefinition,
    EndpointParam,
    PageDefinition,
    FieldNode,
    FieldType,
    ColumnDefinition,
    TableDefinition,
    RoleDefinition,
    EntityNode,
)


class RepairEngine:
    """
    Targeted repair of validation issues without regenerating everything.
    """

    # ──────────────────────────────────────────────────────────────
    # Public entry point
    # ──────────────────────────────────────────────────────────────

    def repair(
        self,
        spec: CompiledSpecification,
        validation_report: ValidationReport,
        max_iterations: int = 3,
    ) -> tuple[CompiledSpecification, RepairReport]:

        start_time = time.time()
        repair_report = RepairReport(repair_id=str(uuid4()))

        # Deep copy so the original is never mutated
        repaired_spec = spec.model_copy(deep=True)

        current_report = validation_report
        iteration = 0

        for iteration in range(1, max_iterations + 1):
            actionable = [
                i for i in current_report.issues
                if i.severity != Severity.INFO
            ]
            if not actionable:
                break

            # Route issues to layer-specific repair functions
            ui_issues = [i for i in actionable if i.affected_schema == "ui"]
            api_issues = [i for i in actionable if i.affected_schema == "api"]
            db_issues = [i for i in actionable if i.affected_schema == "db"]
            auth_issues = [i for i in actionable if i.affected_schema == "auth"]
            bl_issues = [i for i in actionable if i.affected_schema == "business_logic"]
            ast_issues = [i for i in actionable if i.affected_schema == "ast"]
            graph_issues = [i for i in actionable if i.affected_schema == "graph"]

            iter_actions: list[RepairAction] = []

            if ast_issues:
                iter_actions.extend(self.repair_ast(repaired_spec, ast_issues))
            if ui_issues:
                iter_actions.extend(self.repair_ui(repaired_spec, ui_issues))
            if api_issues:
                iter_actions.extend(self.repair_api(repaired_spec, api_issues))
            if db_issues:
                iter_actions.extend(self.repair_db(repaired_spec, db_issues))
            if auth_issues:
                iter_actions.extend(self.repair_auth(repaired_spec, auth_issues))
            if bl_issues:
                iter_actions.extend(self.repair_business_logic(repaired_spec, bl_issues))
            if graph_issues:
                iter_actions.extend(self.repair_graph(repaired_spec, graph_issues))

            if not iter_actions:
                # Nothing could be repaired — remaining issues are unresolvable
                repair_report.unresolvable.extend(actionable)
                break

            repair_report.repairs.extend(iter_actions)

            # Revalidate after repairs
            from app.compiler.validation_engine import ValidationEngine
            validator = ValidationEngine()
            current_report = validator.validate(
                repaired_spec.ast,
                repaired_spec.ui_schema,
                repaired_spec.api_schema,
                repaired_spec.db_schema,
                repaired_spec.auth_schema,
                repaired_spec.business_logic,
            )

            if current_report.passed:
                break

        # Mark any remaining issues as unresolvable
        if current_report and not current_report.passed:
            remaining = [
                i for i in current_report.issues
                if i.severity != Severity.INFO
                and i not in repair_report.unresolvable
            ]
            repair_report.unresolvable.extend(remaining)

        repair_report.total_repairs = len(repair_report.repairs)
        if repair_report.repairs and not repair_report.affected_layers:
            repair_report.affected_layers = list({r.target_schema for r in repair_report.repairs})
            
        repair_report.iterations_used = iteration
        repair_report.revalidation_passed = current_report.passed if current_report else False
        repair_report.repair_time_ms = int((time.time() - start_time) * 1000)
        return repaired_spec, repair_report

    # ──────────────────────────────────────────────────────────────
    # Layer: AST (entities, fields)
    # ──────────────────────────────────────────────────────────────

    def repair_ast(
        self,
        spec: CompiledSpecification,
        issues: list[ValidationIssue],
    ) -> list[RepairAction]:
        actions: list[RepairAction] = []

        for issue in issues:
            action = None

            if issue.rule_id == "V008":
                # Missing primary key — add id field
                entity_name = self._extract_entity_name(issue.message)
                entity = spec.ast.get_entity(entity_name)
                if entity and not any(f.name == "id" for f in entity.fields):
                    id_field = FieldNode(
                        name="id", field_type=FieldType.UUID,
                        required=True, unique=True, indexed=True,
                    )
                    entity.fields.insert(0, id_field)
                    action = RepairAction(
                        issue_rule_id="V008",
                        action_type="add",
                        target_schema="ast",
                        target_path=f"entities.[name='{entity_name}'].fields",
                        description=f"Added primary key 'id' to entity '{entity_name}'",
                        changes=[{"field": "id", "type": "UUID", "position": 0}],
                    )

            elif issue.rule_id == "V009":
                # Missing timestamp fields
                entity_name = self._extract_entity_name(issue.message)
                entity = spec.ast.get_entity(entity_name)
                if entity:
                    added = []
                    field_names = [f.name for f in entity.fields]
                    if "created_at" not in field_names:
                        entity.fields.append(FieldNode(name="created_at", field_type=FieldType.DATETIME, required=True))
                        added.append("created_at")
                    if "updated_at" not in field_names:
                        entity.fields.append(FieldNode(name="updated_at", field_type=FieldType.DATETIME, required=True))
                        added.append("updated_at")
                    if added:
                        action = RepairAction(
                            issue_rule_id="V009",
                            action_type="add",
                            target_schema="ast",
                            target_path=f"entities.[name='{entity_name}'].fields",
                            description=f"Added timestamp fields to entity '{entity_name}'",
                            changes=[{"fields_added": added}],
                        )

            elif issue.rule_id == "V002":
                # Entity has no fields — add a minimal id field
                entity_name = self._extract_entity_name(issue.message)
                entity = spec.ast.get_entity(entity_name)
                if entity and not entity.fields:
                    entity.fields.append(FieldNode(
                        name="id", field_type=FieldType.UUID,
                        required=True, unique=True, indexed=True,
                    ))
                    action = RepairAction(
                        issue_rule_id="V002",
                        action_type="add",
                        target_schema="ast",
                        target_path=f"entities.[name='{entity_name}'].fields",
                        description=f"Added default 'id' field to empty entity '{entity_name}'",
                        changes=[{"field": "id", "type": "UUID"}],
                    )

            if action:
                actions.append(action)

        return actions

    # ──────────────────────────────────────────────────────────────
    # Layer: UI
    # ──────────────────────────────────────────────────────────────

    def repair_ui(
        self,
        spec: CompiledSpecification,
        issues: list[ValidationIssue],
    ) -> list[RepairAction]:
        actions: list[RepairAction] = []

        for issue in issues:
            action = None

            if issue.rule_id == "V011":
                # Missing login page
                if not any(p.route == "/login" for p in spec.ui_schema.pages):
                    spec.ui_schema.pages.append(PageDefinition(
                        route="/login",
                        title="Login",
                        layout="auth",
                        auth_required=False,
                    ))
                    action = RepairAction(
                        issue_rule_id="V011",
                        action_type="add",
                        target_schema="ui",
                        target_path="pages",
                        description="Added login page due to auth middleware requirement",
                        changes=[{"route": "/login", "title": "Login"}],
                    )

            elif issue.rule_id == "V016":
                # Nav item points to missing route — remove the broken nav item
                label = self._extract_quoted(issue.message, "Navigation item '", "'")
                if label:
                    before_count = len(spec.ui_schema.navigation)
                    spec.ui_schema.navigation = [
                        n for n in spec.ui_schema.navigation
                        if n.label != label
                    ]
                    if len(spec.ui_schema.navigation) < before_count:
                        action = RepairAction(
                            issue_rule_id="V016",
                            action_type="remove",
                            target_schema="ui",
                            target_path=f"navigation.[label='{label}']",
                            description=f"Removed navigation item '{label}' pointing to non-existent route",
                            changes=[{"removed_nav": label}],
                        )

            elif issue.rule_id == "V019":
                # Duplicate page routes — deduplicate, keep first occurrence
                route = self._extract_quoted(issue.message, "Duplicate page route '", "'")
                if route:
                    seen = False
                    deduped = []
                    for page in spec.ui_schema.pages:
                        if page.route == route:
                            if not seen:
                                seen = True
                                deduped.append(page)
                            # skip duplicates
                        else:
                            deduped.append(page)
                    spec.ui_schema.pages = deduped
                    action = RepairAction(
                        issue_rule_id="V019",
                        action_type="dedupe",
                        target_schema="ui",
                        target_path="pages",
                        description=f"Deduplicated page route '{route}'",
                        changes=[{"deduped_route": route}],
                    )

            if action:
                actions.append(action)

        return actions

    # ──────────────────────────────────────────────────────────────
    # Layer: API
    # ──────────────────────────────────────────────────────────────

    def repair_api(
        self,
        spec: CompiledSpecification,
        issues: list[ValidationIssue],
    ) -> list[RepairAction]:
        actions: list[RepairAction] = []

        for issue in issues:
            action = None

            if issue.rule_id == "V010":
                # Missing CRUD endpoints for entity
                entity_name = self._extract_entity_name(issue.message)
                entity = spec.ast.get_entity(entity_name)
                if entity:
                    base_path = f"/api/v1/{entity_name}s"
                    existing_paths = {(ep.method, ep.path) for ep in spec.api_schema.endpoints}
                    added = []

                    crud_endpoints = [
                        ("GET", base_path, f"List {entity_name}s"),
                        ("POST", base_path, f"Create {entity_name}"),
                        ("GET", f"{base_path}/{{id}}", f"Get {entity_name}"),
                        ("PUT", f"{base_path}/{{id}}", f"Update {entity_name}"),
                        ("DELETE", f"{base_path}/{{id}}", f"Delete {entity_name}"),
                    ]

                    for method, path, summary in crud_endpoints:
                        if (method, path) not in existing_paths:
                            ep = EndpointDefinition(
                                method=method,
                                path=path,
                                summary=summary,
                                auth_required=True,
                                entity=entity_name,
                            )
                            if method in ("GET",) and "{id}" in path:
                                ep.parameters = [EndpointParam(name="id", param_type="path", data_type="uuid")]
                            if method in ("PUT", "DELETE"):
                                ep.parameters = [EndpointParam(name="id", param_type="path", data_type="uuid")]
                            spec.api_schema.endpoints.append(ep)
                            added.append(f"{method} {path}")

                    if added:
                        action = RepairAction(
                            issue_rule_id="V010",
                            action_type="add",
                            target_schema="api",
                            target_path="endpoints",
                            description=f"Added CRUD endpoints for entity '{entity_name}'",
                            changes=[{"endpoints_added": added}],
                        )

            elif issue.rule_id == "V018":
                # Duplicate endpoints — deduplicate
                key = self._extract_quoted(issue.message, "Duplicate API endpoint '", "'")
                if key:
                    method, path = key.split(":", 1)
                    seen = False
                    deduped = []
                    for ep in spec.api_schema.endpoints:
                        if ep.method == method and ep.path == path:
                            if not seen:
                                seen = True
                                deduped.append(ep)
                        else:
                            deduped.append(ep)
                    spec.api_schema.endpoints = deduped
                    action = RepairAction(
                        issue_rule_id="V018",
                        action_type="dedupe",
                        target_schema="api",
                        target_path="endpoints",
                        description=f"Deduplicated endpoint '{key}'",
                        changes=[{"deduped_endpoint": key}],
                    )

            if action:
                actions.append(action)

        return actions

    # ──────────────────────────────────────────────────────────────
    # Layer: DB
    # ──────────────────────────────────────────────────────────────

    def repair_db(
        self,
        spec: CompiledSpecification,
        issues: list[ValidationIssue],
    ) -> list[RepairAction]:
        actions: list[RepairAction] = []

        for issue in issues:
            action = None

            if issue.rule_id in ("V006", "V013"):
                # Missing DB table for entity
                entity_name = self._extract_entity_name(issue.message)
                table_name = f"{entity_name}s"
                existing_tables = {t.name.lower() for t in spec.db_schema.tables}

                if table_name.lower() not in existing_tables:
                    entity = spec.ast.get_entity(entity_name)
                    columns = [ColumnDefinition(name="id", data_type="UUID", primary_key=True)]
                    if entity:
                        for field in entity.fields:
                            if field.name == "id":
                                continue
                            columns.append(ColumnDefinition(
                                name=field.name,
                                data_type=self._map_field_type(field.field_type),
                                nullable=not field.required,
                                unique=field.unique,
                            ))

                    table = TableDefinition(name=table_name, columns=columns)
                    spec.db_schema.tables.append(table)
                    action = RepairAction(
                        issue_rule_id=issue.rule_id,
                        action_type="add",
                        target_schema="db",
                        target_path="tables",
                        description=f"Added DB table '{table_name}' for entity '{entity_name}'",
                        changes=[{"table": table_name, "columns": [c.name for c in columns]}],
                    )

            elif issue.rule_id == "V008":
                # Missing PK in DB table (complements AST repair)
                entity_name = self._extract_entity_name(issue.message)
                table_name = f"{entity_name}s"
                for table in spec.db_schema.tables:
                    if table.name.lower() == table_name.lower():
                        if not any(c.name == "id" for c in table.columns):
                            table.columns.insert(0, ColumnDefinition(
                                name="id", data_type="UUID", primary_key=True,
                            ))
                            action = RepairAction(
                                issue_rule_id="V008",
                                action_type="add",
                                target_schema="db",
                                target_path=f"tables.[name='{table_name}'].columns",
                                description=f"Added PK column 'id' to table '{table_name}'",
                                changes=[{"column": "id", "type": "UUID"}],
                            )
                        break

            elif issue.rule_id == "V024":
                # FK references non-existent table — remove the FK constraint
                # (we can't create arbitrary tables, so we remove the dangling FK)
                table_col = self._extract_quoted(issue.message, "Column '", "'")
                if table_col and "." in table_col:
                    tbl, col = table_col.split(".", 1)
                    for table in spec.db_schema.tables:
                        if table.name == tbl:
                            for column in table.columns:
                                if column.name == col:
                                    old_fk = column.foreign_key
                                    column.foreign_key = None
                                    action = RepairAction(
                                        issue_rule_id="V024",
                                        action_type="remove",
                                        target_schema="db",
                                        target_path=f"tables.[name='{tbl}'].columns.[name='{col}'].foreign_key",
                                        description=f"Removed dangling FK from '{tbl}.{col}'",
                                        before_value=old_fk,
                                        after_value=None,
                                        changes=[{"removed_fk": old_fk}],
                                    )
                                    break
                            break

            if action:
                actions.append(action)

        return actions

    # ──────────────────────────────────────────────────────────────
    # Layer: Auth
    # ──────────────────────────────────────────────────────────────

    def repair_auth(
        self,
        spec: CompiledSpecification,
        issues: list[ValidationIssue],
    ) -> list[RepairAction]:
        actions: list[RepairAction] = []

        for issue in issues:
            action = None

            if issue.rule_id == "V023":
                # Permission references role with no RoleDefinition — add role
                role_name = self._extract_quoted(issue.message, "references role '", "'")
                if role_name:
                    existing = {r.name.lower() for r in spec.auth_schema.roles}
                    if role_name.lower() not in existing:
                        spec.auth_schema.roles.append(RoleDefinition(
                            name=role_name,
                            description=f"Auto-generated role definition for '{role_name}'",
                        ))
                        action = RepairAction(
                            issue_rule_id="V023",
                            action_type="add",
                            target_schema="auth",
                            target_path="roles",
                            description=f"Added missing RoleDefinition for '{role_name}'",
                            changes=[{"role": role_name}],
                        )

            elif issue.rule_id in ("V007", "V014"):
                # Permission references non-existent entity — remove the permission
                role_name = self._extract_quoted(issue.message, "role '", "'")
                resource = self._extract_quoted(issue.message, "entity '", "'")
                if not resource:
                    resource = self._extract_quoted(issue.message, "resource '", "'")
                if role_name and resource:
                    before_count = len(spec.auth_schema.permissions)
                    spec.auth_schema.permissions = [
                        p for p in spec.auth_schema.permissions
                        if not (p.role.lower() == role_name.lower() and p.resource.lower() == resource.lower())
                    ]
                    if len(spec.auth_schema.permissions) < before_count:
                        action = RepairAction(
                            issue_rule_id=issue.rule_id,
                            action_type="remove",
                            target_schema="auth",
                            target_path=f"permissions.[role='{role_name}']",
                            description=f"Removed orphaned permission for role '{role_name}' on '{resource}'",
                            changes=[{"removed_role": role_name, "removed_resource": resource}],
                        )

            elif issue.rule_id == "V025":
                # Endpoint requires undefined role — add role definition
                role_name = self._extract_quoted(issue.message, "role '", "'")
                if role_name:
                    existing = {r.name.lower() for r in spec.auth_schema.roles}
                    if role_name.lower() not in existing:
                        spec.auth_schema.roles.append(RoleDefinition(
                            name=role_name,
                            description=f"Auto-generated role for API endpoint requirement",
                        ))
                        action = RepairAction(
                            issue_rule_id="V025",
                            action_type="add",
                            target_schema="auth",
                            target_path="roles",
                            description=f"Added missing RoleDefinition for endpoint-required role '{role_name}'",
                            changes=[{"role": role_name}],
                        )

            if action:
                actions.append(action)

        return actions

    # ──────────────────────────────────────────────────────────────
    # Layer: Business Logic
    # ──────────────────────────────────────────────────────────────

    def repair_business_logic(
        self,
        spec: CompiledSpecification,
        issues: list[ValidationIssue],
    ) -> list[RepairAction]:
        actions: list[RepairAction] = []

        for issue in issues:
            action = None

            if issue.rule_id == "V015":
                # Business rule references non-existent entity — remove the rule
                rule_name = self._extract_quoted(issue.message, "rule '", "'")
                if rule_name:
                    before_count = len(spec.business_logic.rules)
                    spec.business_logic.rules = [
                        r for r in spec.business_logic.rules
                        if r.name != rule_name
                    ]
                    if len(spec.business_logic.rules) < before_count:
                        action = RepairAction(
                            issue_rule_id="V015",
                            action_type="remove",
                            target_schema="business_logic",
                            target_path=f"rules.[name='{rule_name}']",
                            description=f"Removed business rule '{rule_name}' referencing non-existent entity",
                            changes=[{"removed_rule": rule_name}],
                        )

            elif issue.rule_id == "V020":
                # Workflow references non-existent entity — remove the workflow
                wf_name = self._extract_quoted(issue.message, "Workflow '", "'")
                if wf_name:
                    before_count = len(spec.business_logic.workflows)
                    spec.business_logic.workflows = [
                        w for w in spec.business_logic.workflows
                        if w.name != wf_name
                    ]
                    if len(spec.business_logic.workflows) < before_count:
                        action = RepairAction(
                            issue_rule_id="V020",
                            action_type="remove",
                            target_schema="business_logic",
                            target_path=f"workflows.[name='{wf_name}']",
                            description=f"Removed workflow '{wf_name}' referencing non-existent entity",
                            changes=[{"removed_workflow": wf_name}],
                        )

            elif issue.rule_id == "V021":
                # Event trigger entity doesn't exist — remove the event
                event_name = self._extract_quoted(issue.message, "Event '", "'")
                if event_name:
                    before_count = len(spec.business_logic.events)
                    spec.business_logic.events = [
                        e for e in spec.business_logic.events
                        if e.name != event_name
                    ]
                    if len(spec.business_logic.events) < before_count:
                        action = RepairAction(
                            issue_rule_id="V021",
                            action_type="remove",
                            target_schema="business_logic",
                            target_path=f"events.[name='{event_name}']",
                            description=f"Removed event '{event_name}' with non-existent trigger entity",
                            changes=[{"removed_event": event_name}],
                        )

            if action:
                actions.append(action)

        return actions

    # ──────────────────────────────────────────────────────────────
    # Layer: Graph (Cross-Layer Consistency)
    # ──────────────────────────────────────────────────────────────

    def repair_graph(
        self,
        spec: CompiledSpecification,
        issues: list[ValidationIssue],
    ) -> list[RepairAction]:
        actions: list[RepairAction] = []

        for issue in issues:
            action = None

            if issue.rule_id == "G001":
                # Edge target missing: endpoint:GET:/api/v1/user
                if "Edge target missing: endpoint:" in issue.message:
                    # Extract the missing endpoint
                    endpoint_str = issue.message.split("endpoint:")[1].strip()
                    if ":" in endpoint_str:
                        method, path = endpoint_str.split(":", 1)
                        # Check if it already exists
                        existing = any(ep.method == method and ep.path == path for ep in spec.api_schema.endpoints)
                        if not existing:
                            # Infer an entity name from the path if possible
                            parts = [p for p in path.split("/") if p and not p.startswith("{")]
                            inferred_entity = parts[-1].rstrip('s') if parts else "unknown"
                            
                            ep = EndpointDefinition(
                                method=method,
                                path=path,
                                summary=f"Auto-generated endpoint {method} {path} to resolve graph dependency",
                                auth_required=False,
                                entity=inferred_entity
                            )
                            spec.api_schema.endpoints.append(ep)
                            
                            action = RepairAction(
                                issue_rule_id="G001",
                                action_type="add",
                                target_schema="api",
                                target_path="endpoints",
                                description=f"Injected missing API endpoint {method} {path} to resolve cross-layer graph dependency",
                                changes=[{"endpoint_added": f"{method} {path}"}]
                            )

            if action:
                actions.append(action)

        return actions

    # ──────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_entity_name(message: str) -> str:
        """Extract entity name from messages like 'Entity 'Foo' is missing...' or 'Entity Foo has...'"""
        # Try quoted form first: Entity 'Foo'
        if "'" in message:
            parts = message.split("'")
            if len(parts) >= 2:
                return parts[1]
        # Fallback: 'Entity Foo is ...'
        words = message.split()
        for i, w in enumerate(words):
            if w.lower() == "entity" and i + 1 < len(words):
                return words[i + 1].strip("'\"")
        return ""

    @staticmethod
    def _extract_quoted(message: str, prefix: str, suffix: str) -> str:
        """Extract text between prefix and suffix markers."""
        start = message.find(prefix)
        if start == -1:
            return ""
        start += len(prefix)
        end = message.find(suffix, start)
        if end == -1:
            return ""
        return message[start:end]

    @staticmethod
    def _map_field_type(field_type: FieldType) -> str:
        mapping = {
            FieldType.STRING: "VARCHAR(255)",
            FieldType.TEXT: "TEXT",
            FieldType.INTEGER: "INTEGER",
            FieldType.FLOAT: "FLOAT",
            FieldType.BOOLEAN: "BOOLEAN",
            FieldType.DATE: "DATE",
            FieldType.DATETIME: "TIMESTAMP",
            FieldType.EMAIL: "VARCHAR(255)",
            FieldType.PASSWORD: "VARCHAR(255)",
            FieldType.URL: "VARCHAR(255)",
            FieldType.PHONE: "VARCHAR(50)",
            FieldType.JSON: "JSON",
            FieldType.UUID: "UUID",
            FieldType.MONEY: "DECIMAL(10,2)",
            FieldType.FILE: "VARCHAR(255)",
            FieldType.IMAGE: "VARCHAR(255)",
        }
        return mapping.get(field_type, "VARCHAR(255)")
