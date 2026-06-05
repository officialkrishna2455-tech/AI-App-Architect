"""
Phase 4 — Runtime Digital Twin.

Simulates the compiled specification as a running application to validate
end-to-end correctness across six categories:

    1. Authentication   — login/register flow, JWT config, auth entity
    2. Authorization    — RBAC permissions, role definitions, endpoint guards
    3. CRUD             — entity endpoint completeness, DB table backing
    4. Premium Gating   — plan definitions, feature gates, page/endpoint guards
    5. Route Access     — page reachability, navigation integrity, data sources
    6. UI → API → DB    — full-stack data-flow tracing

Each category produces ``SimulationScenario`` objects with detailed execution
traces.  Failed scenarios can be converted to ``ValidationIssue`` objects and
fed back into the Repair Engine for self-healing.
"""

import time
from typing import Any

from app.schemas.ast_models import (
    RequirementAST,
    CompiledSpecification,
    SimulationReport,
    SimulationScenario,
    SimulationTraceStep,
    ValidationIssue,
    Severity,
)


class RuntimeSimulator:
    """
    Digital twin simulation of the generated application.
    Validates Auth, Authorization, CRUD, Premium, Navigation, and
    UI → API → DB flows.
    """

    CATEGORY_HANDLERS: dict[str, str] = {
        "auth": "_simulate_auth",
        "authorization": "_simulate_authorization",
        "crud": "_simulate_crud",
        "premium": "_simulate_premium",
        "navigation": "_simulate_navigation",
        "flow": "_simulate_flow",
    }

    # ──────────────────────────────────────────────────────────────
    # Public entry point
    # ──────────────────────────────────────────────────────────────

    def simulate(
        self,
        ast: RequirementAST,
        spec: CompiledSpecification,
        categories: list[str],
    ) -> SimulationReport:
        """Run all requested simulation categories and return a report."""

        start_time = time.time()
        report = SimulationReport()
        categories_run: list[str] = []

        for category in categories:
            handler_name = self.CATEGORY_HANDLERS.get(category)
            if handler_name is None:
                continue
            handler = getattr(self, handler_name)
            scenarios = handler(ast, spec)
            report.scenarios.extend(scenarios)
            categories_run.append(category)

        report.categories_run = categories_run
        
        # Explicitly compute counts since pydantic doesn't re-trigger on list extend
        report.total_scenarios = len(report.scenarios)
        report.passed_count = sum(1 for s in report.scenarios if s.passed)
        report.failed_count = report.total_scenarios - report.passed_count
        
        report.simulation_time_ms = int((time.time() - start_time) * 1000)
        report.simulation_status = "passed" if report.failed_count == 0 else "failed"
        report.failures = [
            {
                "scenario_id": s.scenario_id,
                "category": s.category,
                "error": s.error_message,
            }
            for s in report.scenarios
            if not s.passed and s.actual_result != "skip"
        ]
        return report

    # ──────────────────────────────────────────────────────────────
    # 1. Authentication Simulation
    # ──────────────────────────────────────────────────────────────

    def _simulate_auth(
        self, ast: RequirementAST, spec: CompiledSpecification
    ) -> list[SimulationScenario]:
        scenarios: list[SimulationScenario] = []

        has_auth_middleware = any(
            m.middleware_type == "auth" for m in spec.api_schema.middleware
        )

        if not has_auth_middleware and spec.auth_schema.provider != "jwt":
            scenarios.append(
                SimulationScenario(
                    scenario_id="auth_no_config",
                    category="auth",
                    description="No authentication configured — skipping",
                    steps=["Check auth middleware", "Check auth provider"],
                    actual_result="skip",
                    passed=True,
                    trace=[
                        SimulationTraceStep(
                            layer="auth",
                            component="middleware",
                            action="check_config",
                            status="skip",
                            detail="No auth middleware configured",
                        )
                    ],
                )
            )
            return scenarios

        # 1a. Login endpoint exists
        login_eps = [
            ep
            for ep in spec.api_schema.endpoints
            if "login" in ep.path.lower() and ep.method == "POST"
        ]
        login_ok = len(login_eps) > 0
        scenarios.append(
            self._scenario(
                "auth_login_endpoint",
                "auth",
                "Verify login API endpoint exists",
                ["Find POST */auth/login endpoint in API schema"],
                login_ok,
                "" if login_ok else "Missing POST /api/v1/auth/login endpoint",
                [
                    SimulationTraceStep(
                        layer="api",
                        component="POST /api/v1/auth/login",
                        action="find_endpoint",
                        status="ok" if login_ok else "fail",
                        detail=(
                            f"Found {len(login_eps)} login endpoint(s)"
                            if login_ok
                            else "No login endpoint found"
                        ),
                    )
                ],
            )
        )

        # 1b. Register endpoint exists
        reg_eps = [
            ep
            for ep in spec.api_schema.endpoints
            if "register" in ep.path.lower() and ep.method == "POST"
        ]
        reg_ok = len(reg_eps) > 0
        scenarios.append(
            self._scenario(
                "auth_register_endpoint",
                "auth",
                "Verify register API endpoint exists",
                ["Find POST */auth/register endpoint"],
                reg_ok,
                "" if reg_ok else "Missing POST /api/v1/auth/register endpoint",
                [
                    SimulationTraceStep(
                        layer="api",
                        component="POST /api/v1/auth/register",
                        action="find_endpoint",
                        status="ok" if reg_ok else "fail",
                        detail=(
                            f"Found {len(reg_eps)} register endpoint(s)"
                            if reg_ok
                            else "No register endpoint found"
                        ),
                    )
                ],
            )
        )

        # 1c. JWT token config
        tc = spec.auth_schema.token_config
        valid_algos = {"HS256", "HS384", "HS512", "RS256", "RS384", "RS512"}
        jwt_ok = tc.algorithm in valid_algos and tc.expire_minutes > 0
        scenarios.append(
            self._scenario(
                "auth_jwt_config",
                "auth",
                "Verify JWT token configuration is valid",
                ["Check algorithm is supported", "Check expiration > 0"],
                jwt_ok,
                (
                    ""
                    if jwt_ok
                    else f"Invalid JWT config: algo={tc.algorithm}, expire={tc.expire_minutes}"
                ),
                [
                    SimulationTraceStep(
                        layer="auth",
                        component="token_config",
                        action="validate_jwt_config",
                        status="ok" if jwt_ok else "fail",
                        detail=f"Algorithm={tc.algorithm}, Expire={tc.expire_minutes}min",
                    )
                ],
            )
        )

        # 1d. Auth entity with email + password
        auth_entity = self._find_auth_entity(ast)
        entity_ok = auth_entity is not None
        field_names = (
            [f.name.lower() for f in auth_entity.fields] if auth_entity else []
        )
        has_email = "email" in field_names
        has_password = "password" in field_names or "password_hash" in field_names
        auth_entity_ok = entity_ok and has_email and has_password
        scenarios.append(
            self._scenario(
                "auth_entity_check",
                "auth",
                "Verify auth entity exists with email and password fields",
                [
                    "Find auth entity or User entity",
                    "Check for email field",
                    "Check for password field",
                ],
                auth_entity_ok,
                (
                    ""
                    if auth_entity_ok
                    else (
                        f"Auth entity {'found but missing fields' if entity_ok else 'not found'}: "
                        f"email={'yes' if has_email else 'no'}, password={'yes' if has_password else 'no'}"
                    )
                ),
                [
                    SimulationTraceStep(
                        layer="db",
                        component=f"{auth_entity.name if auth_entity else 'N/A'} entity",
                        action="find_auth_entity",
                        status="ok" if entity_ok else "fail",
                        detail=(
                            f"Entity: {auth_entity.name}"
                            if auth_entity
                            else "No auth/User entity found"
                        ),
                    ),
                    SimulationTraceStep(
                        layer="db",
                        component="auth_fields",
                        action="check_credentials_fields",
                        status="ok" if auth_entity_ok else "fail",
                        detail=f"email={'found' if has_email else 'missing'}, password={'found' if has_password else 'missing'}",
                    ),
                ],
            )
        )

        # 1e. Login page exists
        login_page = any(p.route == "/login" for p in spec.ui_schema.pages)
        login_page_ok = login_page or not has_auth_middleware
        scenarios.append(
            self._scenario(
                "auth_login_page",
                "auth",
                "Verify login page exists in UI schema",
                ["Find /login page in UI pages"],
                login_page_ok,
                (
                    ""
                    if login_page_ok
                    else "Auth middleware configured but no /login page found"
                ),
                [
                    SimulationTraceStep(
                        layer="ui",
                        component="/login",
                        action="find_login_page",
                        status="ok" if login_page_ok else "fail",
                        detail=(
                            "Login page found"
                            if login_page
                            else "No /login page in UI schema"
                        ),
                    )
                ],
            )
        )

        # 1f. Full login flow: UI → API → DB → JWT
        table_name = f"{auth_entity.name}s" if auth_entity else "users"
        table_exists = any(
            t.name.lower() == table_name.lower() for t in spec.db_schema.tables
        )
        login_flow_ok = (
            login_ok and login_page and auth_entity_ok and jwt_ok and table_exists
        )
        scenarios.append(
            self._scenario(
                "auth_full_login_flow",
                "auth",
                "Simulate complete login flow: UI → API → DB → JWT",
                [
                    "Navigate to /login page",
                    "Submit credentials to POST /api/v1/auth/login",
                    f"Query {table_name} table for user",
                    "Generate JWT token",
                ],
                login_flow_ok,
                "" if login_flow_ok else "Broken login flow — see trace",
                [
                    SimulationTraceStep(
                        layer="ui",
                        component="/login",
                        action="route_to",
                        status="ok" if login_page else "fail",
                        detail="Navigate to login page",
                    ),
                    SimulationTraceStep(
                        layer="api",
                        component="POST /api/v1/auth/login",
                        action="call_endpoint",
                        status="ok" if login_ok else "fail",
                        detail="Submit credentials",
                    ),
                    SimulationTraceStep(
                        layer="db",
                        component=f"{table_name} table",
                        action="query_table",
                        status="ok" if table_exists else "fail",
                        detail="Lookup user by email",
                    ),
                    SimulationTraceStep(
                        layer="auth",
                        component="JWT",
                        action="generate_token",
                        status="ok" if jwt_ok else "fail",
                        detail=f"Generate JWT with {tc.algorithm}",
                    ),
                ],
            )
        )

        # 1g. Google Login Flow
        google_ep = any(ep.path == "/api/v1/auth/google" for ep in spec.api_schema.endpoints)
        scenarios.append(
            self._scenario(
                "auth_google_login",
                "auth",
                "Simulate Google Login flow",
                ["Navigate to /login", "Submit Google ID token", "Generate JWT"],
                google_ep,
                "" if google_ep else "Missing Google OAuth endpoint",
                [
                    SimulationTraceStep(layer="api", component="POST /api/v1/auth/google", action="verify_endpoint", status="ok" if google_ep else "fail", detail="Google auth endpoint")
                ]
            )
        )

        # 1h. Token Refresh Flow
        refresh_ep = any(ep.path == "/api/v1/auth/refresh" for ep in spec.api_schema.endpoints)
        scenarios.append(
            self._scenario(
                "auth_token_refresh",
                "auth",
                "Simulate Token Refresh flow",
                ["Submit refresh token", "Validate token", "Generate new access token"],
                refresh_ep,
                "" if refresh_ep else "Missing Token Refresh endpoint",
                [
                    SimulationTraceStep(layer="api", component="POST /api/v1/auth/refresh", action="verify_endpoint", status="ok" if refresh_ep else "fail", detail="Refresh endpoint")
                ]
            )
        )

        # 1i. Logout Flow
        logout_ep = any(ep.path == "/api/v1/auth/logout" for ep in spec.api_schema.endpoints)
        scenarios.append(
            self._scenario(
                "auth_logout_flow",
                "auth",
                "Simulate Logout flow",
                ["Call logout endpoint", "Invalidate session"],
                logout_ep,
                "" if logout_ep else "Missing Logout endpoint",
                [
                    SimulationTraceStep(layer="api", component="POST /api/v1/auth/logout", action="verify_endpoint", status="ok" if logout_ep else "fail", detail="Logout endpoint")
                ]
            )
        )

        # 1j. Role Assignment
        # Check if auth roles exist and default role is assigned
        roles_defined = len(spec.auth_schema.roles) > 0
        scenarios.append(
            self._scenario(
                "auth_role_assignment",
                "auth",
                "Simulate Role Assignment on Registration",
                ["Register new user", "Assign default role"],
                roles_defined,
                "" if roles_defined else "No roles defined in auth schema",
                [
                    SimulationTraceStep(layer="auth", component="roles", action="verify_assignment", status="ok" if roles_defined else "fail", detail="Roles configuration exists")
                ]
            )
        )

        # 1k. Protected Route Access
        protected_routes = [ep for ep in spec.api_schema.endpoints if ep.required_roles]
        has_protected = len(protected_routes) > 0
        scenarios.append(
            self._scenario(
                "auth_protected_route_access",
                "auth",
                "Simulate Protected Route Access",
                ["Access protected endpoint without token (Fail)", "Access with valid token (Success)"],
                has_protected,
                "" if has_protected else "No protected routes configured to test",
                [
                    SimulationTraceStep(layer="api", component="protected_routes", action="verify_guards", status="ok" if has_protected else "fail", detail=f"{len(protected_routes)} protected routes found")
                ]
            )
        )

        return scenarios

    # ──────────────────────────────────────────────────────────────
    # 2. Authorization Simulation
    # ──────────────────────────────────────────────────────────────

    def _simulate_authorization(
        self, ast: RequirementAST, spec: CompiledSpecification
    ) -> list[SimulationScenario]:
        scenarios: list[SimulationScenario] = []
        entity_names_lower = {e.name.lower() for e in ast.entities}
        defined_roles = {r.name.lower() for r in spec.auth_schema.roles}

        if not spec.auth_schema.roles and not spec.auth_schema.permissions:
            scenarios.append(
                self._scenario(
                    "authz_no_config",
                    "authorization",
                    "No authorization configured — skipping",
                    ["Check roles", "Check permissions"],
                    True,
                    "",
                    [
                        SimulationTraceStep(
                            layer="auth",
                            component="rbac",
                            action="check_config",
                            status="skip",
                            detail="No roles or permissions defined",
                        )
                    ],
                    actual="skip",
                )
            )
            return scenarios

        # 2a. Role definitions cover all permission roles
        perm_roles = {p.role.lower() for p in spec.auth_schema.permissions}
        orphaned = perm_roles - defined_roles
        roles_ok = len(orphaned) == 0
        scenarios.append(
            self._scenario(
                "authz_role_definitions",
                "authorization",
                "Verify all permission roles have RoleDefinitions",
                [f"Check role '{r}' has definition" for r in sorted(perm_roles)]
                or ["No permissions to check"],
                roles_ok,
                (
                    ""
                    if roles_ok
                    else f"Orphaned roles without definitions: {sorted(orphaned)}"
                ),
                [
                    SimulationTraceStep(
                        layer="auth",
                        component="roles",
                        action="verify_role_definitions",
                        status="ok" if roles_ok else "fail",
                        detail=f"Defined: {sorted(defined_roles)}, Referenced: {sorted(perm_roles)}",
                    )
                ],
            )
        )

        # 2b. Permissions reference real entities
        bad_resources: list[str] = []
        for perm in spec.auth_schema.permissions:
            if perm.resource.lower() not in entity_names_lower:
                bad_resources.append(f"{perm.role}→{perm.resource}")
        res_ok = len(bad_resources) == 0
        scenarios.append(
            self._scenario(
                "authz_permission_resources",
                "authorization",
                "Verify permission resources reference valid entities",
                [
                    f"Check resource '{p.resource}' exists"
                    for p in spec.auth_schema.permissions
                ]
                or ["No permissions to check"],
                res_ok,
                (
                    ""
                    if res_ok
                    else f"Invalid permission resources: {bad_resources}"
                ),
                [
                    SimulationTraceStep(
                        layer="auth",
                        component="permissions",
                        action="verify_resources",
                        status="ok" if res_ok else "fail",
                        detail=f"Entities: {sorted(entity_names_lower)}, Invalid: {bad_resources}",
                    )
                ],
            )
        )

        # 2c. Endpoint required_roles match defined roles
        bad_ep_roles: list[str] = []
        for ep in spec.api_schema.endpoints:
            for role in ep.required_roles:
                if role.lower() not in defined_roles:
                    bad_ep_roles.append(f"{ep.method} {ep.path}→{role}")
        ep_roles_ok = len(bad_ep_roles) == 0
        scenarios.append(
            self._scenario(
                "authz_endpoint_roles",
                "authorization",
                "Verify endpoint required_roles match defined roles",
                ["Check each endpoint's required_roles against defined roles"],
                ep_roles_ok,
                (
                    ""
                    if ep_roles_ok
                    else f"Endpoints with undefined roles: {bad_ep_roles}"
                ),
                [
                    SimulationTraceStep(
                        layer="api",
                        component="endpoint_guards",
                        action="verify_role_guards",
                        status="ok" if ep_roles_ok else "fail",
                        detail=(
                            f"Invalid: {bad_ep_roles}"
                            if bad_ep_roles
                            else "All endpoint roles valid"
                        ),
                    )
                ],
            )
        )

        # 2d. Simulate RBAC access check per role
        for role_def in spec.auth_schema.roles:
            role_perms = [
                p
                for p in spec.auth_schema.permissions
                if p.role.lower() == role_def.name.lower()
            ]
            allowed = {p.resource.lower() for p in role_perms}
            accessible = [
                f"{ep.method} {ep.path}"
                for ep in spec.api_schema.endpoints
                if ep.entity and ep.entity.lower() in allowed
            ]
            blocked = [
                f"{ep.method} {ep.path}"
                for ep in spec.api_schema.endpoints
                if ep.entity
                and ep.entity.lower() not in allowed
                and ep.required_roles
                and role_def.name.lower()
                not in [r.lower() for r in ep.required_roles]
            ]
            scenarios.append(
                self._scenario(
                    f"authz_rbac_{role_def.name}",
                    "authorization",
                    f"Simulate RBAC access for role '{role_def.name}'",
                    [
                        f"User with role='{role_def.name}'",
                        f"Accessible resources: {sorted(allowed) or 'none'}",
                        f"Accessible endpoints: {len(accessible)}",
                    ],
                    True,
                    "",
                    [
                        SimulationTraceStep(
                            layer="auth",
                            component=f"role:{role_def.name}",
                            action="check_permission",
                            status="ok",
                            detail=f"Resources: {sorted(allowed)}",
                        ),
                        SimulationTraceStep(
                            layer="api",
                            component="endpoints",
                            action="access_check",
                            status="ok",
                            detail=f"Accessible: {len(accessible)}, Blocked: {len(blocked)}",
                        ),
                    ],
                )
            )

        return scenarios

    # ──────────────────────────────────────────────────────────────
    # 3. CRUD Simulation
    # ──────────────────────────────────────────────────────────────

    def _simulate_crud(
        self, ast: RequirementAST, spec: CompiledSpecification
    ) -> list[SimulationScenario]:
        scenarios: list[SimulationScenario] = []
        table_names_lower = {t.name.lower() for t in spec.db_schema.tables}

        for entity in ast.entities:
            base = f"/api/v1/{entity.name}s"
            expected = [
                ("GET", base),
                ("POST", base),
                ("GET", f"{base}/{{id}}"),
                ("PUT", f"{base}/{{id}}"),
                ("DELETE", f"{base}/{{id}}"),
            ]
            existing = {(ep.method, ep.path) for ep in spec.api_schema.endpoints}
            missing = [f"{m} {p}" for m, p in expected if (m, p) not in existing]
            present = [f"{m} {p}" for m, p in expected if (m, p) in existing]

            # 3a. CRUD endpoint completeness
            crud_ok = len(missing) == 0
            scenarios.append(
                self._scenario(
                    f"crud_{entity.name}_endpoints",
                    "crud",
                    f"Verify CRUD endpoints exist for entity '{entity.name}'",
                    [f"Check {m} {p}" for m, p in expected],
                    crud_ok,
                    "" if crud_ok else f"Missing endpoints: {missing}",
                    [
                        SimulationTraceStep(
                            layer="api",
                            component=f"{entity.name} CRUD",
                            action="check_endpoints",
                            status="ok" if crud_ok else "fail",
                            detail=(
                                f"Present: {len(present)}/5, Missing: {missing}"
                                if missing
                                else "All 5 CRUD endpoints present"
                            ),
                        )
                    ],
                )
            )

            # 3b. DB table backing with column coverage
            exp_table = f"{entity.name}s".lower()
            table_exists = exp_table in table_names_lower
            table_obj = (
                next(
                    (
                        t
                        for t in spec.db_schema.tables
                        if t.name.lower() == exp_table
                    ),
                    None,
                )
                if table_exists
                else None
            )
            table_cols = (
                {c.name.lower() for c in table_obj.columns} if table_obj else set()
            )
            entity_fields = {f.name.lower() for f in entity.fields}
            missing_cols = entity_fields - table_cols
            col_ok = table_exists and len(missing_cols) == 0

            scenarios.append(
                self._scenario(
                    f"crud_{entity.name}_db_table",
                    "crud",
                    f"Verify DB table for entity '{entity.name}' with matching columns",
                    [f"Find table '{entity.name}s'", "Check columns match entity fields"],
                    col_ok,
                    (
                        ""
                        if col_ok
                        else (
                            f"Table '{entity.name}s' not found"
                            if not table_exists
                            else f"Missing columns: {sorted(missing_cols)}"
                        )
                    ),
                    [
                        SimulationTraceStep(
                            layer="db",
                            component=f"{entity.name}s table",
                            action="find_table",
                            status="ok" if table_exists else "fail",
                            detail=f"Table {'found' if table_exists else 'not found'}",
                        ),
                        SimulationTraceStep(
                            layer="db",
                            component=f"{entity.name}s columns",
                            action="check_columns",
                            status="ok" if col_ok else "fail",
                            detail=(
                                f"Missing: {sorted(missing_cols)}"
                                if missing_cols
                                else "All columns present"
                            ),
                        ),
                    ],
                )
            )

            # 3c. Create flow
            create_ep = ("POST", base) in existing
            create_ok = create_ep and table_exists
            scenarios.append(
                self._scenario(
                    f"crud_{entity.name}_create_flow",
                    "crud",
                    f"Simulate CREATE flow for '{entity.name}'",
                    [
                        f"POST {base} with entity fields",
                        f"Validate request body against {entity.name} schema",
                        f"INSERT INTO {entity.name}s table",
                        "Return 201 Created",
                    ],
                    create_ok,
                    "" if create_ok else "Broken create flow",
                    [
                        SimulationTraceStep(
                            layer="api",
                            component=f"POST {base}",
                            action="call_endpoint",
                            status="ok" if create_ep else "fail",
                            detail="Submit new entity",
                        ),
                        SimulationTraceStep(
                            layer="db",
                            component=f"{entity.name}s",
                            action="insert_record",
                            status="ok" if table_exists else "fail",
                            detail=f"INSERT into {entity.name}s",
                        ),
                    ],
                )
            )

            # 3d. Read flow
            read_ep = ("GET", f"{base}/{{id}}") in existing
            read_ok = read_ep and table_exists
            scenarios.append(
                self._scenario(
                    f"crud_{entity.name}_read_flow",
                    "crud",
                    f"Simulate READ flow for '{entity.name}'",
                    [
                        f"GET {base}/{{id}}",
                        f"SELECT FROM {entity.name}s WHERE id=?",
                        "Return entity data",
                    ],
                    read_ok,
                    "" if read_ok else "Broken read flow",
                    [
                        SimulationTraceStep(
                            layer="api",
                            component=f"GET {base}/{{id}}",
                            action="call_endpoint",
                            status="ok" if read_ep else "fail",
                            detail="Request entity by ID",
                        ),
                        SimulationTraceStep(
                            layer="db",
                            component=f"{entity.name}s",
                            action="query_table",
                            status="ok" if table_exists else "fail",
                            detail=f"SELECT from {entity.name}s",
                        ),
                    ],
                )
            )

        return scenarios

    # ──────────────────────────────────────────────────────────────
    # 4. Premium Gating Simulation
    # ──────────────────────────────────────────────────────────────

    def _simulate_premium(
        self, ast: RequirementAST, spec: CompiledSpecification
    ) -> list[SimulationScenario]:
        scenarios: list[SimulationScenario] = []
        plan_names = {p.name.lower() for p in ast.plans}

        if not ast.plans:
            scenarios.append(
                self._scenario(
                    "premium_no_plans",
                    "premium",
                    "No subscription plans defined — skipping",
                    ["Check for plan definitions in AST"],
                    True,
                    "",
                    [
                        SimulationTraceStep(
                            layer="auth",
                            component="plans",
                            action="check_plans",
                            status="skip",
                            detail="No plans defined",
                        )
                    ],
                    actual="skip",
                )
            )
            return scenarios

        # 4a. Feature gates reference valid features
        all_features = {f.name.lower() for f in ast.features}
        bad_gates: list[str] = []
        for plan in ast.plans:
            for gate in plan.features:
                if gate.feature.lower() not in all_features:
                    bad_gates.append(f"{plan.name}→{gate.feature}")
        gates_ok = len(bad_gates) == 0
        scenarios.append(
            self._scenario(
                "premium_feature_gates",
                "premium",
                "Verify plan feature gates reference valid features",
                [
                    f"Check gate '{p.name}:{fg.feature}'"
                    for p in ast.plans
                    for fg in p.features
                ]
                or ["No gates to check"],
                gates_ok,
                "" if gates_ok else f"Invalid feature gates: {bad_gates}",
                [
                    SimulationTraceStep(
                        layer="auth",
                        component="feature_gates",
                        action="verify_gates",
                        status="ok" if gates_ok else "fail",
                        detail=(
                            f"Invalid: {bad_gates}"
                            if bad_gates
                            else "All gates valid"
                        ),
                    )
                ],
            )
        )

        # 4b. Pages with required_plan reference valid plans
        bad_page_plans: list[str] = []
        for page in spec.ui_schema.pages:
            if page.required_plan and page.required_plan.lower() not in plan_names:
                bad_page_plans.append(f"{page.route}→{page.required_plan}")
        pp_ok = len(bad_page_plans) == 0
        scenarios.append(
            self._scenario(
                "premium_page_plans",
                "premium",
                "Verify pages with required_plan reference valid plans",
                ["Check all page plan requirements"],
                pp_ok,
                "" if pp_ok else f"Pages with invalid plans: {bad_page_plans}",
                [
                    SimulationTraceStep(
                        layer="ui",
                        component="page_plans",
                        action="verify_page_plans",
                        status="ok" if pp_ok else "fail",
                        detail=(
                            f"Invalid: {bad_page_plans}"
                            if bad_page_plans
                            else "All page plans valid"
                        ),
                    )
                ],
            )
        )

        # 4c. Endpoints with required_plan reference valid plans
        bad_ep_plans: list[str] = []
        for ep in spec.api_schema.endpoints:
            if ep.required_plan and ep.required_plan.lower() not in plan_names:
                bad_ep_plans.append(f"{ep.method} {ep.path}→{ep.required_plan}")
        ep_ok = len(bad_ep_plans) == 0
        scenarios.append(
            self._scenario(
                "premium_endpoint_plans",
                "premium",
                "Verify endpoints with required_plan reference valid plans",
                ["Check all endpoint plan requirements"],
                ep_ok,
                "" if ep_ok else f"Endpoints with invalid plans: {bad_ep_plans}",
                [
                    SimulationTraceStep(
                        layer="api",
                        component="endpoint_plans",
                        action="verify_endpoint_plans",
                        status="ok" if ep_ok else "fail",
                        detail=(
                            f"Invalid: {bad_ep_plans}"
                            if bad_ep_plans
                            else "All endpoint plans valid"
                        ),
                    )
                ],
            )
        )

        # 4d. Simulate gating: free user → premium page → blocked
        premium_pages = [p for p in spec.ui_schema.pages if p.required_plan]
        free_plan = next((p for p in ast.plans if p.tier == 0), None)

        if premium_pages and free_plan:
            for page in premium_pages:
                gate_blocks = page.required_plan.lower() != free_plan.name.lower()
                scenarios.append(
                    self._scenario(
                        f"premium_gate_{page.route.strip('/').replace('/', '_') or 'root'}",
                        "premium",
                        f"Simulate free user accessing premium page '{page.route}'",
                        [
                            f"User with plan='{free_plan.name}'",
                            f"Access page '{page.route}' (requires plan='{page.required_plan}')",
                            "Check plan gate",
                        ],
                        True,
                        "",
                        [
                            SimulationTraceStep(
                                layer="auth",
                                component=f"plan:{free_plan.name}",
                                action="check_plan_gate",
                                status="ok",
                                detail=f"Gate {'blocks' if gate_blocks else 'allows'} access",
                            ),
                            SimulationTraceStep(
                                layer="ui",
                                component=page.route,
                                action="access_page",
                                status="ok",
                                detail=f"Access {'blocked' if gate_blocks else 'allowed'} — correct behavior",
                            ),
                        ],
                    )
                )

        return scenarios

    # ──────────────────────────────────────────────────────────────
    # 5. Route Access (Navigation) Simulation
    # ──────────────────────────────────────────────────────────────

    def _simulate_navigation(
        self, ast: RequirementAST, spec: CompiledSpecification
    ) -> list[SimulationScenario]:
        scenarios: list[SimulationScenario] = []
        page_routes = {p.route for p in spec.ui_schema.pages}
        api_get_paths = {
            ep.path for ep in spec.api_schema.endpoints if ep.method == "GET"
        }

        # 5a. Navigation items → existing routes
        broken_nav: list[str] = []
        for nav in spec.ui_schema.navigation:
            if nav.route not in page_routes:
                broken_nav.append(f"{nav.label}→{nav.route}")
        nav_ok = len(broken_nav) == 0
        scenarios.append(
            self._scenario(
                "nav_integrity",
                "navigation",
                "Verify all navigation items point to existing page routes",
                [
                    f"Check nav '{n.label}' → '{n.route}'"
                    for n in spec.ui_schema.navigation
                ]
                or ["No navigation items"],
                nav_ok,
                "" if nav_ok else f"Broken navigation items: {broken_nav}",
                [
                    SimulationTraceStep(
                        layer="ui",
                        component="navigation",
                        action="verify_nav_links",
                        status="ok" if nav_ok else "fail",
                        detail=(
                            f"Broken: {broken_nav}"
                            if broken_nav
                            else "All nav items valid"
                        ),
                    )
                ],
            )
        )

        # 5b. Page data_sources → existing GET endpoints
        broken_ds: list[str] = []
        for page in spec.ui_schema.pages:
            for ds in page.data_sources:
                if ds not in api_get_paths:
                    broken_ds.append(f"{page.route}→{ds}")
        ds_ok = len(broken_ds) == 0
        scenarios.append(
            self._scenario(
                "nav_data_sources",
                "navigation",
                "Verify page data_sources reference existing GET endpoints",
                ["Check each page's data_sources against API GET endpoints"],
                ds_ok,
                "" if ds_ok else f"Broken data sources: {broken_ds}",
                [
                    SimulationTraceStep(
                        layer="ui",
                        component="data_sources",
                        action="verify_data_sources",
                        status="ok" if ds_ok else "fail",
                        detail=(
                            f"Broken: {broken_ds}"
                            if broken_ds
                            else "All data sources valid"
                        ),
                    )
                ],
            )
        )

        # 5c. Simulate navigation per page
        for page in spec.ui_schema.pages:
            auth_ok = True
            if page.auth_required:
                auth_ok = any(
                    m.middleware_type == "auth"
                    for m in spec.api_schema.middleware
                )
            ds_page_ok = all(ds in api_get_paths for ds in page.data_sources)
            page_ok = auth_ok and ds_page_ok

            trace: list[SimulationTraceStep] = [
                SimulationTraceStep(
                    layer="ui",
                    component=page.route,
                    action="route_to",
                    status="ok",
                    detail=f"Navigate to {page.route}",
                ),
            ]
            if page.auth_required:
                trace.append(
                    SimulationTraceStep(
                        layer="auth",
                        component="middleware",
                        action="check_auth",
                        status="ok" if auth_ok else "fail",
                        detail=f"Auth required: {page.auth_required}",
                    )
                )
            for ds in page.data_sources:
                ds_exists = ds in api_get_paths
                trace.append(
                    SimulationTraceStep(
                        layer="api",
                        component=ds,
                        action="load_data",
                        status="ok" if ds_exists else "fail",
                        detail=f"Load data from {ds}",
                    )
                )
            trace.append(
                SimulationTraceStep(
                    layer="ui",
                    component=page.route,
                    action="render_page",
                    status="ok" if page_ok else "fail",
                    detail="Render page content",
                )
            )

            slug = page.route.replace("/", "_").strip("_") or "home"
            scenarios.append(
                self._scenario(
                    f"nav_page_{slug}",
                    "navigation",
                    f"Simulate navigating to '{page.route}'",
                    [
                        f"Route to {page.route}",
                        f"Auth check: {'required' if page.auth_required else 'none'}",
                        f"Load data sources: {page.data_sources or 'none'}",
                        "Render page",
                    ],
                    page_ok,
                    (
                        ""
                        if page_ok
                        else f"Page navigation failed for {page.route}"
                    ),
                    trace,
                )
            )

        return scenarios

    # ──────────────────────────────────────────────────────────────
    # 6. UI → API → DB Flow Simulation
    # ──────────────────────────────────────────────────────────────

    def _simulate_flow(
        self, ast: RequirementAST, spec: CompiledSpecification
    ) -> list[SimulationScenario]:
        scenarios: list[SimulationScenario] = []
        table_names_lower = {t.name.lower() for t in spec.db_schema.tables}
        api_get = {ep.path for ep in spec.api_schema.endpoints if ep.method == "GET"}
        api_post = {ep.path for ep in spec.api_schema.endpoints if ep.method == "POST"}

        for entity in ast.entities:
            base = f"/api/v1/{entity.name}s"
            exp_table = f"{entity.name}s".lower()

            # 6a. Read flow: UI page → GET endpoint → DB table
            entity_pages = [
                p for p in spec.ui_schema.pages if base in p.data_sources
            ]
            has_ui = len(entity_pages) > 0
            has_get = base in api_get
            has_table = exp_table in table_names_lower

            read_ok = has_ui and has_get and has_table
            scenarios.append(
                self._scenario(
                    f"flow_{entity.name}_read",
                    "flow",
                    f"Trace READ flow for '{entity.name}': UI → API → DB",
                    [
                        f"UI page loads data from {base}",
                        f"API GET {base} fetches data",
                        f"DB queries {entity.name}s table",
                    ],
                    read_ok,
                    (
                        ""
                        if read_ok
                        else (
                            f"Broken read flow: UI={'ok' if has_ui else 'missing'}, "
                            f"API={'ok' if has_get else 'missing'}, "
                            f"DB={'ok' if has_table else 'missing'}"
                        )
                    ),
                    [
                        SimulationTraceStep(
                            layer="ui",
                            component=(
                                entity_pages[0].route if entity_pages else "N/A"
                            ),
                            action="load_page",
                            status="ok" if has_ui else "fail",
                            detail=f"Page with data_source={base}",
                        ),
                        SimulationTraceStep(
                            layer="api",
                            component=f"GET {base}",
                            action="call_endpoint",
                            status="ok" if has_get else "fail",
                            detail=f"Fetch {entity.name} list",
                        ),
                        SimulationTraceStep(
                            layer="db",
                            component=f"{entity.name}s table",
                            action="query_table",
                            status="ok" if has_table else "fail",
                            detail=f"SELECT FROM {entity.name}s",
                        ),
                    ],
                )
            )

            # 6b. Write flow: UI form → POST endpoint → DB table
            forms = [
                c
                for c in spec.ui_schema.components
                if c.entity
                and c.entity.lower() == entity.name.lower()
                and c.component_type == "form"
            ]
            has_form = len(forms) > 0
            has_post = base in api_post

            write_ok = has_form and has_post and has_table
            scenarios.append(
                self._scenario(
                    f"flow_{entity.name}_write",
                    "flow",
                    f"Trace WRITE flow for '{entity.name}': UI Form → API → DB",
                    [
                        f"Submit {entity.name} form",
                        f"API POST {base} creates record",
                        f"DB inserts into {entity.name}s table",
                    ],
                    write_ok,
                    (
                        ""
                        if write_ok
                        else (
                            f"Broken write flow: Form={'ok' if has_form else 'missing'}, "
                            f"API={'ok' if has_post else 'missing'}, "
                            f"DB={'ok' if has_table else 'missing'}"
                        )
                    ),
                    [
                        SimulationTraceStep(
                            layer="ui",
                            component=(
                                forms[0].name if forms else "N/A"
                            ),
                            action="submit_form",
                            status="ok" if has_form else "fail",
                            detail=f"Form for {entity.name}",
                        ),
                        SimulationTraceStep(
                            layer="api",
                            component=f"POST {base}",
                            action="call_endpoint",
                            status="ok" if has_post else "fail",
                            detail=f"Create {entity.name}",
                        ),
                        SimulationTraceStep(
                            layer="db",
                            component=f"{entity.name}s table",
                            action="insert_record",
                            status="ok" if has_table else "fail",
                            detail=f"INSERT INTO {entity.name}s",
                        ),
                    ],
                )
            )

            # 6c. Field / column compatibility
            if has_table:
                table_obj = next(
                    (
                        t
                        for t in spec.db_schema.tables
                        if t.name.lower() == exp_table
                    ),
                    None,
                )
                if table_obj:
                    t_cols = {c.name.lower() for c in table_obj.columns}
                    e_fields = {f.name.lower() for f in entity.fields}
                    miss = e_fields - t_cols
                    compat_ok = len(miss) == 0
                    scenarios.append(
                        self._scenario(
                            f"flow_{entity.name}_compat",
                            "flow",
                            f"Check field/column compatibility for '{entity.name}'",
                            ["Compare entity fields with table columns"],
                            compat_ok,
                            (
                                ""
                                if compat_ok
                                else f"Fields missing in DB: {sorted(miss)}"
                            ),
                            [
                                SimulationTraceStep(
                                    layer="db",
                                    component=f"{entity.name}s",
                                    action="check_compatibility",
                                    status="ok" if compat_ok else "fail",
                                    detail=(
                                        f"Missing: {sorted(miss)}"
                                        if miss
                                        else "All fields have matching columns"
                                    ),
                                )
                            ],
                        )
                    )

        return scenarios

    # ──────────────────────────────────────────────────────────────
    # Failure → ValidationIssue conversion (for self-healing)
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def failures_to_issues(report: SimulationReport) -> list[ValidationIssue]:
        """Convert failed simulation scenarios into ValidationIssues for the Repair Engine."""

        category_to_schema: dict[str, str] = {
            "auth": "api",
            "authorization": "auth",
            "crud": "api",
            "premium": "auth",
            "navigation": "ui",
            "flow": "api",
        }

        issues: list[ValidationIssue] = []
        for scenario in report.scenarios:
            if not scenario.passed and scenario.actual_result != "skip":
                affected = category_to_schema.get(scenario.category, "api")

                # Refine from trace
                if scenario.trace:
                    failed = [t for t in scenario.trace if t.status == "fail"]
                    if failed and failed[0].layer in ("ui", "api", "db", "auth"):
                        affected = failed[0].layer

                rule_id = _map_scenario_to_rule_id(scenario)

                issues.append(
                    ValidationIssue(
                        rule_id=rule_id,
                        severity=Severity.ERROR,
                        layer="simulation",
                        message=(
                            scenario.error_message
                            or f"Simulation failed: {scenario.description}"
                        ),
                        affected_schema=affected,
                        affected_path=f"simulation.{scenario.scenario_id}",
                        suggestion=f"Fix {scenario.category} simulation failure: {scenario.description}",
                    )
                )
        return issues

    # ──────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _find_auth_entity(ast: RequirementAST):
        """Find the auth entity in the AST (is_auth_entity or named User/Account)."""
        for entity in ast.entities:
            if entity.is_auth_entity:
                return entity
        for entity in ast.entities:
            if entity.name.lower() in ("user", "users", "account", "accounts"):
                return entity
        return None

    @staticmethod
    def _scenario(
        sid: str,
        category: str,
        desc: str,
        steps: list[str],
        passed: bool,
        error: str,
        trace: list[SimulationTraceStep],
        *,
        actual: str | None = None,
    ) -> SimulationScenario:
        """Shorthand factory for SimulationScenario."""
        return SimulationScenario(
            scenario_id=sid,
            category=category,
            description=desc,
            steps=steps,
            actual_result=actual if actual else ("pass" if passed else "fail"),
            passed=passed,
            error_message=error,
            trace=trace,
        )


# ──────────────────────────────────────────────────────────────────
# Scenario → Rule-ID mapping (for self-healing repair)
# ──────────────────────────────────────────────────────────────────


def _map_scenario_to_rule_id(scenario: SimulationScenario) -> str:
    """Map a simulation failure to a known validation rule ID so the Repair Engine
    can apply a targeted fix."""
    sid = scenario.scenario_id
    msg = (scenario.error_message or "").lower()

    # Auth
    if "login_endpoint" in sid or "register_endpoint" in sid:
        return "V010"
    if "login_page" in sid:
        return "V011"
    if "auth_entity" in sid:
        return "V008"

    # Authorization
    if "role_definitions" in sid:
        return "V023"
    if "permission_resources" in sid:
        return "V007"
    if "endpoint_roles" in sid:
        return "V025"

    # CRUD
    if "crud_" in sid and "endpoints" in sid:
        return "V010"
    if "crud_" in sid and "db_table" in sid:
        return "V006"

    # Navigation
    if "nav_integrity" in sid:
        return "V016"
    if "nav_data_sources" in sid:
        return "V005"

    # Flow
    if "flow_" in sid:
        if "db" in msg or "table" in msg:
            return "V006"
        if "api" in msg or "endpoint" in msg:
            return "V010"

    return "SIM001"
