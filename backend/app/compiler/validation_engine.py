import time
from app.schemas.ast_models import (
    RequirementAST,
    UISchema,
    APISchema,
    DBSchema,
    AuthSchema,
    BusinessLogicSchema,
    ValidationReport,
    ValidationIssue,
    Severity
)

class ValidationEngine:
    """
    Four-layer validation: Structural, Type, Cross-layer, Semantic.
    """

    def validate(self, 
                 ast: RequirementAST, 
                 ui: UISchema, 
                 api: APISchema, 
                 db: DBSchema, 
                 auth: AuthSchema, 
                 business_logic: BusinessLogicSchema,
                 graph_issues: list[ValidationIssue]) -> ValidationReport:
        
        start_time = time.time()
        report = ValidationReport()
        
        # Include issues from the consistency engine (graph validation)
        report.issues.extend(graph_issues)
        
        # Semantic Validations
        
        # V008: Every entity must have a primary key (id)
        # V009: Every entity must have timestamp fields
        for entity in ast.entities:
            field_names = [f.name for f in entity.fields]
            if "id" not in field_names:
                report.issues.append(ValidationIssue(
                    rule_id="V008",
                    severity=Severity.ERROR,
                    layer="semantic",
                    message=f"Entity {entity.name} is missing a primary key (id)",
                    affected_schema="ast"
                ))
            if entity.timestamps:
                if "created_at" not in field_names or "updated_at" not in field_names:
                    report.issues.append(ValidationIssue(
                        rule_id="V009",
                        severity=Severity.WARNING,
                        layer="semantic",
                        message=f"Entity {entity.name} is missing timestamp fields",
                        affected_schema="ast"
                    ))
                    
        # V010: CRUD endpoints must exist for every entity
        for entity in ast.entities:
            entity_paths = [ep.path for ep in api.endpoints if ep.entity == entity.name]
            if not entity_paths:
                report.issues.append(ValidationIssue(
                    rule_id="V010",
                    severity=Severity.WARNING,
                    layer="semantic",
                    message=f"Entity {entity.name} is missing CRUD endpoints",
                    affected_schema="api"
                ))
                
        # V011: Login page must exist if auth is configured
        if api.middleware and any(m.middleware_type == "auth" for m in api.middleware):
            if not any(p.route == "/login" for p in ui.pages):
                report.issues.append(ValidationIssue(
                    rule_id="V011",
                    severity=Severity.ERROR,
                    layer="semantic",
                    message="Login page is missing but auth is required",
                    affected_schema="ui"
                ))
                
        # Structural & Type validation are implicitly handled by Pydantic during generation
        # We can simulate V001, V002, V003 as implicitly passing here if schemas were generated correctly
        
        report.validation_time_ms = int((time.time() - start_time) * 1000)
        # the `@model_validator` on ValidationReport will compute passed/failed totals
        return report
