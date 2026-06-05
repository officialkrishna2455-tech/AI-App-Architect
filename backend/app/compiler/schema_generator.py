import uuid
from typing import Optional

from app.schemas.ast_models import (
    RequirementAST,
    ArchitecturePlan,
    CompiledSpecification,
    UISchema,
    APISchema,
    DBSchema,
    AuthSchema,
    BusinessLogicSchema,
    PageDefinition,
    ComponentDefinition,
    ComponentRef,
    NavigationItem,
    EndpointDefinition,
    EndpointParam,
    MiddlewareDefinition,
    TableDefinition,
    ColumnDefinition,
    RoleDefinition,
    PermissionDefinition,
    WorkflowDefinition,
    WorkflowStep,
    FieldType,
    ActionVerb
)

class SchemaGenerator:
    """
    Generates all 5 schemas from AST and ArchitecturePlan.
    """

    def generate_ui_schema(self, ast: RequirementAST, plan: ArchitecturePlan) -> UISchema:
        ui = UISchema()
        
        # Navigation
        nav_items = []
        
        # Generate Home page
        ui.pages.append(PageDefinition(
            route="/",
            title="Home",
            layout="default",
            auth_required=False
        ))
        nav_items.append(NavigationItem(label="Home", route="/"))
        
        # If auth, add login page
        if plan.auth_strategy != "none":
            ui.pages.append(PageDefinition(
                route="/login",
                title="Login",
                layout="auth",
                auth_required=False
            ))
        
        # Feature pages
        for feature in ast.features:
            route = f"/{feature.name}"
            ui.pages.append(PageDefinition(
                route=route,
                title=feature.name.capitalize(),
                layout="dashboard",
                auth_required=True,
                required_roles=feature.required_roles,
                required_plan=feature.required_plan,
                data_sources=[f"/api/v1/{e}s" for e in feature.entities]
            ))
            nav_items.append(NavigationItem(
                label=feature.name.capitalize(),
                route=route,
                required_roles=feature.required_roles,
                required_plan=feature.required_plan
            ))
            
            # Components for feature
            ui.components.append(ComponentDefinition(
                name=f"{feature.name}Dashboard",
                component_type="dashboard",
                actions=[a.verb for a in feature.actions]
            ))
            
        # CRUD Pages for Entities
        for entity in ast.entities:
            # List page
            route = f"/{entity.name}s"
            ui.pages.append(PageDefinition(
                route=route,
                title=f"{entity.name.capitalize()}s",
                layout="dashboard",
                auth_required=True,
                data_sources=[f"/api/v1/{entity.name}s"]
            ))
            nav_items.append(NavigationItem(label=f"{entity.name.capitalize()}s", route=route))
            
            ui.components.append(ComponentDefinition(
                name=f"{entity.name}List",
                component_type="table",
                entity=entity.name,
                fields=[f.name for f in entity.fields]
            ))
            ui.components.append(ComponentDefinition(
                name=f"{entity.name}Form",
                component_type="form",
                entity=entity.name,
                fields=[f.name for f in entity.fields]
            ))
            
        ui.navigation = nav_items
        return ui

    def generate_api_schema(self, ast: RequirementAST, plan: ArchitecturePlan) -> APISchema:
        api = APISchema()
        
        if plan.auth_strategy == "jwt":
            api.middleware.append(MiddlewareDefinition(name="jwt_auth", middleware_type="auth"))
            api.endpoints.extend([
                EndpointDefinition(method="POST", path="/api/v1/auth/login",    auth_required=False, response_body={"token": "string"}),
                EndpointDefinition(method="POST", path="/api/v1/auth/register", auth_required=False, response_body={"token": "string"}),
                EndpointDefinition(method="POST", path="/api/v1/auth/logout",   auth_required=True,  response_body={"message": "string"}),
                EndpointDefinition(method="POST", path="/api/v1/auth/refresh",  auth_required=False, response_body={"token": "string"}),
                EndpointDefinition(method="POST", path="/api/v1/auth/google",   auth_required=False, response_body={"token": "string"}),
            ])
            
        for entity in ast.entities:
            base_path = f"/api/v1/{entity.name}s"
            api.endpoints.extend([
                EndpointDefinition(
                    method="GET",
                    path=base_path,
                    summary=f"List {entity.name}s",
                    auth_required=True,
                    entity=entity.name
                ),
                EndpointDefinition(
                    method="POST",
                    path=base_path,
                    summary=f"Create {entity.name}",
                    auth_required=True,
                    entity=entity.name,
                    request_body={f.name: f.field_type for f in entity.fields}
                ),
                EndpointDefinition(
                    method="GET",
                    path=f"{base_path}/{{id}}",
                    summary=f"Get {entity.name}",
                    auth_required=True,
                    entity=entity.name,
                    parameters=[EndpointParam(name="id", param_type="path", data_type="uuid")]
                ),
                EndpointDefinition(
                    method="PUT",
                    path=f"{base_path}/{{id}}",
                    summary=f"Update {entity.name}",
                    auth_required=True,
                    entity=entity.name,
                    parameters=[EndpointParam(name="id", param_type="path", data_type="uuid")],
                    request_body={f.name: f.field_type for f in entity.fields}
                ),
                EndpointDefinition(
                    method="DELETE",
                    path=f"{base_path}/{{id}}",
                    summary=f"Delete {entity.name}",
                    auth_required=True,
                    entity=entity.name,
                    parameters=[EndpointParam(name="id", param_type="path", data_type="uuid")]
                )
            ])
            
        return api

    def _map_type(self, field_type: FieldType) -> str:
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

    def generate_db_schema(self, ast: RequirementAST, plan: ArchitecturePlan) -> DBSchema:
        db = DBSchema()
        
        for entity in ast.entities:
            table = TableDefinition(name=f"{entity.name}s")
            for field in entity.fields:
                col = ColumnDefinition(
                    name=field.name,
                    data_type=self._map_type(field.field_type),
                    nullable=not field.required,
                    primary_key=(field.name == "id"),
                    unique=field.unique
                )
                table.columns.append(col)
                if field.indexed:
                    table.indexes.append(field.name)
            
            for rel in entity.relations:
                # Add foreign key column if many-to-one or one-to-one
                fk_col_name = f"{rel.target_entity}_id"
                if not any(c.name == fk_col_name for c in table.columns):
                    table.columns.append(ColumnDefinition(
                        name=fk_col_name,
                        data_type="UUID",
                        foreign_key=f"{rel.target_entity}s.id"
                    ))
                    
            db.tables.append(table)
            
        return db

    def generate_auth_schema(self, ast: RequirementAST, plan: ArchitecturePlan) -> AuthSchema:
        auth = AuthSchema()
        
        if plan.auth_strategy == "jwt":
            auth.provider = "jwt"
            
        for role in ast.roles:
            auth.roles.append(RoleDefinition(
                name=role.name,
                is_default=role.is_default,
                parent=role.parent_role
            ))
            
            for perm in role.permissions:
                auth.permissions.append(PermissionDefinition(
                    role=role.name,
                    resource=perm.resource,
                    actions=[a.value for a in perm.actions],
                    conditions=perm.conditions or {}
                ))
                
        return auth

    def generate_business_logic_schema(self, ast: RequirementAST, plan: ArchitecturePlan) -> BusinessLogicSchema:
        bl = BusinessLogicSchema()
        
        for entity in ast.entities:
            # Create a simple create workflow
            bl.workflows.append(WorkflowDefinition(
                name=f"create_{entity.name}",
                trigger="on_create",
                entity=entity.name,
                steps=[
                    WorkflowStep(step=1, action="validate"),
                    WorkflowStep(step=2, action="save_to_db")
                ]
            ))
            
        return bl

    def generate_all(self, ast: RequirementAST, plan: ArchitecturePlan) -> CompiledSpecification:
        spec = CompiledSpecification()
        spec.ast = ast
        spec.ui_schema = self.generate_ui_schema(ast, plan)
        spec.api_schema = self.generate_api_schema(ast, plan)
        spec.db_schema = self.generate_db_schema(ast, plan)
        spec.auth_schema = self.generate_auth_schema(ast, plan)
        spec.business_logic = self.generate_business_logic_schema(ast, plan)
        return spec
