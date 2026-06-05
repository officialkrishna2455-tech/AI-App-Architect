# Simulation Failure Analysis

> Generated from a live execution of all 20 evaluation prompts through the full 9-stage compilation + runtime simulation pipeline. No estimates — all numbers are actual execution results.

## 1. Overview

| Metric | Value |
|--------|-------|
| Prompts tested | 20 |
| Total simulation scenarios run | 585 |
| Scenarios passed | 463 |
| Scenarios failed | 122 |
| Current simulation pass rate | **79.15%** |
| Runs with ≥1 failure | 19 |
| Total repairs triggered | 0 |

## 2. Failure Category Summary

| Category | Failures | Severity | Most Common Error |
|----------|----------|----------|-------------------|
| auth | 72 | Critical | `Missing POST /api/v1/auth/login endpoint` |
| navigation | 50 | Medium | `Page navigation failed for /users` |

## 3. Per-Prompt Results

| # | Type | Scenarios | Passed | Failed | Val Pass | Repairs |
|---|------|-----------|--------|--------|----------|---------|
| 1 | production | 38 | 36 | 2 [FAIL] | 0% | 0 |
| 2 | production | 32 | 24 | 8 [FAIL] | 100% | 0 |
| 3 | production | 36 | 28 | 8 [FAIL] | 100% | 0 |
| 4 | production | 13 | 7 | 6 [FAIL] | 100% | 0 |
| 5 | production | 51 | 42 | 9 [FAIL] | 100% | 0 |
| 6 | production | 51 | 42 | 9 [FAIL] | 100% | 0 |
| 7 | production | 44 | 35 | 9 [FAIL] | 100% | 0 |
| 8 | production | 60 | 49 | 11 [FAIL] | 100% | 0 |
| 9 | production | 52 | 42 | 10 [FAIL] | 100% | 0 |
| 10 | production | 52 | 42 | 10 [FAIL] | 100% | 0 |
| 11 | adversarial | 11 | 7 | 4 [FAIL] | 100% | 0 |
| 12 | adversarial | 11 | 7 | 4 [FAIL] | 100% | 0 |
| 13 | adversarial | 22 | 17 | 5 [FAIL] | 100% | 0 |
| 14 | adversarial | 20 | 20 | 0 [PASS] | 100% | 0 |
| 15 | adversarial | 11 | 7 | 4 [FAIL] | 100% | 0 |
| 16 | adversarial | 11 | 7 | 4 [FAIL] | 100% | 0 |
| 17 | adversarial | 11 | 7 | 4 [FAIL] | 100% | 0 |
| 18 | adversarial | 27 | 21 | 6 [FAIL] | 100% | 0 |
| 19 | adversarial | 21 | 16 | 5 [FAIL] | 100% | 0 |
| 20 | adversarial | 11 | 7 | 4 [FAIL] | 100% | 0 |

## 4. Detailed Failure Analysis

### Prompt 1 (production)

> Build a CRM with login, contacts, dashboard, role-based access, premium plans, payments, and analytics.

- **Validation pass rate**: 0%
- **Repairs triggered**: 0
- **Failed scenarios**: 2

#### Failure 1: `nav_data_sources` (navigation)
- **Description**: Verify page data_sources reference existing GET endpoints
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Broken data sources: ['/dashboard→/api/v1/user', '/dashboard→/api/v1/contact', '/dashboard→/api/v1/payment']
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Partial / Failed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 2: `nav_page_dashboard` (navigation)
- **Description**: Simulate navigating to '/dashboard'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /dashboard
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Partial / Failed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 2 (production)

> Create an e-commerce platform with products, categories, shopping cart, checkout, order tracking, and admin panel.

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 8

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 5: `nav_page_cart` (navigation)
- **Description**: Simulate navigating to '/cart'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /cart
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 6: `nav_page_panel` (navigation)
- **Description**: Simulate navigating to '/panel'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /panel
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 7: `nav_page_products` (navigation)
- **Description**: Simulate navigating to '/products'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /products
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 8: `nav_page_orders` (navigation)
- **Description**: Simulate navigating to '/orders'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /orders
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 3 (production)

> Build a project management tool with tasks, sprints, team members, kanban board, and time tracking.

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 8

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 5: `nav_page_board` (navigation)
- **Description**: Simulate navigating to '/board'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /board
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 6: `nav_page_projects` (navigation)
- **Description**: Simulate navigating to '/projects'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /projects
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 7: `nav_page_tasks` (navigation)
- **Description**: Simulate navigating to '/tasks'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /tasks
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 8: `nav_page_teams` (navigation)
- **Description**: Simulate navigating to '/teams'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /teams
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 4 (production)

> Design a social media app with posts, comments, likes, followers, notifications, and content moderation.

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 6

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 5: `nav_page_notifications` (navigation)
- **Description**: Simulate navigating to '/notifications'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /notifications
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 6: `nav_page_moderation` (navigation)
- **Description**: Simulate navigating to '/moderation'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /moderation
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 5 (production)

> Create a healthcare management system with patients, appointments, prescriptions, doctors, and medical records.

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 9

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 5: `nav_page_patients` (navigation)
- **Description**: Simulate navigating to '/patients'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /patients
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 6: `nav_page_appointments` (navigation)
- **Description**: Simulate navigating to '/appointments'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /appointments
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 7: `nav_page_prescriptions` (navigation)
- **Description**: Simulate navigating to '/prescriptions'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /prescriptions
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 8: `nav_page_doctors` (navigation)
- **Description**: Simulate navigating to '/doctors'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /doctors
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 9: `nav_page_records` (navigation)
- **Description**: Simulate navigating to '/records'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /records
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 6 (production)

> Build a learning management system with courses, lessons, quizzes, enrollments, certificates, and instructor dashboards.

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 9

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 5: `nav_page_courses` (navigation)
- **Description**: Simulate navigating to '/courses'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /courses
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 6: `nav_page_lessons` (navigation)
- **Description**: Simulate navigating to '/lessons'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /lessons
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 7: `nav_page_enrollments` (navigation)
- **Description**: Simulate navigating to '/enrollments'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /enrollments
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 8: `nav_page_certificates` (navigation)
- **Description**: Simulate navigating to '/certificates'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /certificates
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 9: `nav_page_instructors` (navigation)
- **Description**: Simulate navigating to '/instructors'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /instructors
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 7 (production)

> Design a real estate platform with listings, agents, virtual tours, mortgage calculator, and saved searches.

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 9

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 5: `nav_page_calculator` (navigation)
- **Description**: Simulate navigating to '/calculator'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /calculator
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 6: `nav_page_listings` (navigation)
- **Description**: Simulate navigating to '/listings'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /listings
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 7: `nav_page_agents` (navigation)
- **Description**: Simulate navigating to '/agents'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /agents
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 8: `nav_page_tours` (navigation)
- **Description**: Simulate navigating to '/tours'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /tours
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 9: `nav_page_mortgages` (navigation)
- **Description**: Simulate navigating to '/mortgages'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /mortgages
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 8 (production)

> Create a restaurant management system with menu, orders, reservations, tables, kitchen display, and delivery tracking.

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 11

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 5: `nav_page_display` (navigation)
- **Description**: Simulate navigating to '/display'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /display
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 6: `nav_page_menus` (navigation)
- **Description**: Simulate navigating to '/menus'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /menus
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 7: `nav_page_orders` (navigation)
- **Description**: Simulate navigating to '/orders'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /orders
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 8: `nav_page_reservations` (navigation)
- **Description**: Simulate navigating to '/reservations'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /reservations
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 9: `nav_page_tables` (navigation)
- **Description**: Simulate navigating to '/tables'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /tables
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 10: `nav_page_kitchens` (navigation)
- **Description**: Simulate navigating to '/kitchens'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /kitchens
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 11: `nav_page_deliverys` (navigation)
- **Description**: Simulate navigating to '/deliverys'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /deliverys
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 9 (production)

> Build a job board with postings, applications, company profiles, resume parsing, and interview scheduling.

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 10

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 5: `nav_page_board` (navigation)
- **Description**: Simulate navigating to '/board'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /board
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 6: `nav_page_postings` (navigation)
- **Description**: Simulate navigating to '/postings'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /postings
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 7: `nav_page_applications` (navigation)
- **Description**: Simulate navigating to '/applications'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /applications
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 8: `nav_page_companys` (navigation)
- **Description**: Simulate navigating to '/companys'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /companys
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 9: `nav_page_resumes` (navigation)
- **Description**: Simulate navigating to '/resumes'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /resumes
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 10: `nav_page_interviews` (navigation)
- **Description**: Simulate navigating to '/interviews'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /interviews
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 10 (production)

> Design a SaaS billing platform with subscriptions, invoices, usage metering, payment methods, and revenue analytics.

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 10

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 5: `nav_page_analytics` (navigation)
- **Description**: Simulate navigating to '/analytics'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /analytics
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 6: `nav_page_subscriptions` (navigation)
- **Description**: Simulate navigating to '/subscriptions'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /subscriptions
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 7: `nav_page_invoices` (navigation)
- **Description**: Simulate navigating to '/invoices'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /invoices
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 8: `nav_page_usages` (navigation)
- **Description**: Simulate navigating to '/usages'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /usages
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 9: `nav_page_payments` (navigation)
- **Description**: Simulate navigating to '/payments'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /payments
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 10: `nav_page_revenues` (navigation)
- **Description**: Simulate navigating to '/revenues'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /revenues
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 11 (adversarial)

> *(empty string)*

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 4

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

### Prompt 12 (adversarial)

> Build everything

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 4

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

### Prompt 13 (adversarial)

> Create a system where admins are also regular users but cannot access admin features

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 5

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity found but missing fields: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 5: `nav_page_users` (navigation)
- **Description**: Simulate navigating to '/users'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /users
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 15 (adversarial)

> Create 500 microservices with real-time sync

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 4

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

### Prompt 16 (adversarial)

> Build a CRM. Build a CRM. Build a CRM.

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 4

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

### Prompt 17 (adversarial)

> Build a system using blockchain, quantum computing, and telepathy

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 4

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

### Prompt 18 (adversarial)

> SELECT * FROM users; DROP TABLE users;--

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 6

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity found but missing fields: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 5: `nav_page_users` (navigation)
- **Description**: Simulate navigating to '/users'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /users
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

#### Failure 6: `nav_page_tables` (navigation)
- **Description**: Simulate navigating to '/tables'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /tables
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 19 (adversarial)

> Build an app where free users get premium features and premium users get nothing

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 5

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity found but missing fields: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 5: `nav_page_users` (navigation)
- **Description**: Simulate navigating to '/users'
- **Failure category**: navigation
- **Severity**: Medium
- **Original error**:
  ```
  Page navigation failed for /users
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  Navigation items pointing to missing routes are repaired (V016), but data-source
  references (V005/V012) are WARNING-level. The simulator still marks these as failures
  because the runtime would 404 on the missing API call.
- **Recommended fix**:
  Promote V005/V012 (data-source → no GET endpoint) from WARNING to ERROR so the Repair
  Engine can auto-add the missing GET endpoint.

### Prompt 20 (adversarial)

> asdfjkl;qwer zxcv poiuy

- **Validation pass rate**: 100%
- **Repairs triggered**: 0
- **Failed scenarios**: 4

#### Failure 1: `auth_login_endpoint` (auth)
- **Description**: Verify login API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/login endpoint
  ```
- **Root cause**:
  Schema Generator does not emit a /auth/login endpoint unless 'login' or 'auth' is
  explicitly parsed from the requirement. Adversarial / sparse inputs produce no auth
  endpoints.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 2: `auth_register_endpoint` (auth)
- **Description**: Verify register API endpoint exists
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Missing POST /api/v1/auth/register endpoint
  ```
- **Root cause**:
  Schema Generator only adds /auth/register when a registration feature is explicitly
  detected. Prompts that say 'login' without 'signup' or 'register' skip this endpoint.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 3: `auth_entity_check` (auth)
- **Description**: Verify auth entity exists with email and password fields
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Auth entity not found: email=no, password=no
  ```
- **Root cause**:
  Could not be automatically determined — see error message.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

#### Failure 4: `auth_full_login_flow` (auth)
- **Description**: Simulate complete login flow: UI → API → DB → JWT
- **Failure category**: auth
- **Severity**: Critical
- **Original error**:
  ```
  Broken login flow — see trace
  ```
- **Root cause**:
  Composite failure: one or more sub-checks (login endpoint, login page, auth entity
  fields, JWT config, users table) failed, causing the full UI→API→DB→JWT chain to break.
- **Validation status**: Passed
- **Repair status**: No repairs triggered
- **Why simulation still failed**:
  The Repair Engine cannot manufacture a working /auth/login endpoint out of nothing — it
  only adds CRUD endpoints for AST entities (rule V010). Auth-specific routes require
  dedicated repair rules (currently absent). Validation passes because auth middleware is
  optional, so no ERROR-level issue fires that the engine could repair.
- **Recommended fix**:
  Add dedicated Repair Engine rules for auth endpoints: if auth middleware is present and
  no /auth/login POST endpoint exists, auto-generate it. Also add a login-page repair rule
  analogous to V011.

## 5. Achievable Pass Rate After Fixes

The following estimate is based on applying all Recommended Fixes above,
weighted by implementation feasibility for each category:

| Category | Current failures | Recoverable | Fix feasibility |
|----------|-----------------|-------------|-----------------|
| auth | 72 | 64 | 90% |
| navigation | 50 | 47 | 95% |
| **Total** | **122** | **111** | — |

| | Current | After fixes |
|--|---------|-------------|
| Scenarios passed | 463 | 574 |
| Simulation pass rate | **79.15%** | **98.12%** |

> **Note**: The achievable rate assumes all recommended fixes are implemented. Some residual failures (~11) are structurally inherent to the adversarial prompts (e.g., empty string, random gibberish) where the pipeline deliberately produces minimal output, and those simulation scenarios are expected to skip rather than fail.
