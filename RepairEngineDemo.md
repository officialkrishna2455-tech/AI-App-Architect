# Repair Engine Demonstration

This document demonstrates the cyclic auto-healing capabilities of the Repair Engine.

## 1. Initial Validation Errors

The following intentional errors were injected:

- **V006 (error)**: Entity 'user' has no corresponding DB table (expected 'users')
- **V007 (error)**: Permission for role 'admin' references non-existent entity 'invalid_entity'
- **V023 (error)**: Permission references role 'admin' which has no RoleDefinition
- **V008 (error)**: Entity 'user' is missing a primary key (id)
  - *Suggestion*: Add a UUID 'id' field as the first field
- **V009 (warning)**: Entity 'user' has timestamps=True but is missing timestamp fields
  - *Suggestion*: Add 'created_at' and 'updated_at' DATETIME fields
- **V010 (warning)**: Entity 'user' has no CRUD API endpoints
  - *Suggestion*: Add GET/POST/PUT/DELETE endpoints for /api/v1/users
- **V016 (warning)**: Navigation item 'Dashboard' points to non-existent route '/dashboard'

## 2. Repair Actions Taken

- **Fixed V008** (add in ast): Added primary key 'id' to entity 'user'
  - *Changes*: `[{'field': 'id', 'type': 'UUID', 'position': 0}]`
- **Fixed V009** (add in ast): Added timestamp fields to entity 'user'
  - *Changes*: `[{'fields_added': ['created_at', 'updated_at']}]`
- **Fixed V016** (remove in ui): Removed navigation item 'Dashboard' pointing to non-existent route
  - *Changes*: `[{'removed_nav': 'Dashboard'}]`
- **Fixed V010** (add in api): Added CRUD endpoints for entity 'user'
  - *Changes*: `[{'endpoints_added': ['GET /api/v1/users', 'POST /api/v1/users', 'GET /api/v1/users/{id}', 'PUT /api/v1/users/{id}', 'DELETE /api/v1/users/{id}']}]`
- **Fixed V006** (add in db): Added DB table 'users' for entity 'user'
  - *Changes*: `[{'table': 'users', 'columns': ['id', 'email', 'created_at', 'updated_at']}]`
- **Fixed V007** (remove in auth): Removed orphaned permission for role 'admin' on 'invalid_entity'
  - *Changes*: `[{'removed_role': 'admin', 'removed_resource': 'invalid_entity'}]`
- **Fixed V023** (add in auth): Added missing RoleDefinition for 'admin'
  - *Changes*: `[{'role': 'admin'}]`

## 3. Revalidation Result

- **Validation Passed**: True
- **Iterations Used**: 1
- **Repair Time**: 0ms

## 4. Final Corrected Schemas Snippets

### AST (User Entity Fixed)
```json
{
  "entities": [
    {
      "node_type": "entity",
      "name": "user",
      "fields": [
        {
          "node_type": "field",
          "name": "id",
          "field_type": "uuid",
          "required": true,
          "unique": true,
          "indexed": true,
          "default": null,
          "enum_values": null,
          "description": "",
          "source": null
        },
        {
          "node_type": "field",
          "name": "email",
          "field_type": "email",
          "required": true,
          "unique": false,
          "indexed": false,
          "default": null,
          "enum_values": null,
          "description": "",
          "source": null
        },
        {
          "node_type": "field",
          "name": "created_at",
          "field_type": "datetime",
          "required": true,
          "unique": false,
          "indexed": false,
          "default": null,
          "enum_values": null,
          "description": "",
          "source": null
        },
        {
          "node_type": "field",
          "name": "updated_at",
          "field_type": "datetime",
          "required": true,
          "unique": false,
          "indexed": false,
          "default": null,
          "enum_values": null,
          "description": "",
          "source": null
        }
      ],
      "relations": [],
      "is_auth_entity": false,
      "soft_delete": false,
      "timestamps": true,
      "description": "",
      "source": null
    }
  ],
  "features": [],
  "roles": [],
  "plans": [],
  "integrations": [],
  "constraints": [],
  "metadata": {
    "version": "1.0.0",
    "source_hash": "",
    "created_at": "2026-06-04T13:31:25.716740+00:00",
    "token_count": 0,
    "node_count": 0,
    "warnings": [],
    "enrichments": []
  },
  "total_nodes": 5
}
```

### DB Schema (Table & PK Fixed)
```json
{
  "tables": [
    {
      "name": "users",
      "columns": [
        {
          "name": "id",
          "data_type": "UUID",
          "nullable": false,
          "primary_key": true,
          "unique": false,
          "indexed": false,
          "default": null,
          "foreign_key": null
        },
        {
          "name": "email",
          "data_type": "VARCHAR(255)",
          "nullable": false,
          "primary_key": false,
          "unique": false,
          "indexed": false,
          "default": null,
          "foreign_key": null
        },
        {
          "name": "created_at",
          "data_type": "TIMESTAMP",
          "nullable": false,
          "primary_key": false,
          "unique": false,
          "indexed": false,
          "default": null,
          "foreign_key": null
        },
        {
          "name": "updated_at",
          "data_type": "TIMESTAMP",
          "nullable": false,
          "primary_key": false,
          "unique": false,
          "indexed": false,
          "default": null,
          "foreign_key": null
        }
      ],
      "primary_key": "id",
      "unique_constraints": [],
      "indexes": []
    }
  ],
  "indexes": [],
  "relations": [],
  "migrations": []
}
```

### API Schema (Missing Endpoints Fixed)
```json
{
  "base_path": "/api/v1",
  "endpoints": [
    {
      "method": "GET",
      "path": "/api/v1/users",
      "summary": "List users",
      "request_body": null,
      "response_body": {},
      "parameters": [],
      "auth_required": true,
      "required_roles": [],
      "required_plan": null,
      "rate_limit": null,
      "entity": "user"
    },
    {
      "method": "POST",
      "path": "/api/v1/users",
      "summary": "Create user",
      "request_body": null,
      "response_body": {},
      "parameters": [],
      "auth_required": true,
      "required_roles": [],
      "required_plan": null,
      "rate_limit": null,
      "entity": "user"
    },
    {
      "method": "GET",
      "path": "/api/v1/users/{id}",
      "summary": "Get user",
      "request_body": null,
      "response_body": {},
      "parameters": [
        {
          "name": "id",
          "param_type": "path",
          "data_type": "uuid",
          "required": true
        }
      ],
      "auth_required": true,
      "required_roles": [],
      "required_plan": null,
      "rate_limit": null,
      "entity": "user"
    },
    {
      "method": "PUT",
      "path": "/api/v1/users/{id}",
      "summary": "Update user",
      "request_body": null,
      "response_body": {},
      "parameters": [
        {
          "name": "id",
          "param_type": "path",
          "data_type": "uuid",
          "required": true
        }
      ],
      "auth_required": true,
      "required_roles": [],
      "required_plan": null,
      "rate_limit": null,
      "entity": "user"
    },
    {
      "method": "DELETE",
      "path": "/api/v1/users/{id}",
      "summary": "Delete user",
      "request_body": null,
      "response_body": {},
      "parameters": [
        {
          "name": "id",
          "param_type": "path",
          "data_type": "uuid",
          "required": true
        }
      ],
      "auth_required": true,
      "required_roles": [],
      "required_plan": null,
      "rate_limit": null,
      "entity": "user"
    }
  ],
  "middleware": [],
  "error_codes": {}
}
```

### Auth Schema (Roles & Permissions Fixed)
```json
{
  "provider": "jwt",
  "roles": [
    {
      "name": "admin",
      "description": "Auto-generated role definition for 'admin'",
      "is_default": false,
      "parent": null
    }
  ],
  "permissions": [
    {
      "role": "admin",
      "resource": "user",
      "actions": [
        "read"
      ],
      "conditions": {}
    }
  ],
  "policies": [],
  "token_config": {
    "algorithm": "HS256",
    "expire_minutes": 1440,
    "refresh_enabled": true,
    "refresh_expire_days": 7
  }
}
```

### UI Schema (Broken Nav Fixed)
```json
{
  "pages": [
    {
      "route": "/",
      "title": "Home",
      "layout": "default",
      "components": [],
      "auth_required": true,
      "required_roles": [],
      "required_plan": null,
      "data_sources": []
    }
  ],
  "components": [],
  "navigation": [],
  "theme": {}
}
```
