import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.ast_models import (
    RequirementAST, EntityNode, FieldNode, FieldType,
    UISchema, PageDefinition, NavigationItem,
    APISchema, DBSchema, AuthSchema, PermissionDefinition,
    BusinessLogicSchema, CompiledSpecification
)
from app.compiler.validation_engine import ValidationEngine
from app.compiler.repair_engine import RepairEngine

def run_demo():
    # 1. Construct intentionally broken schema
    ast = RequirementAST(
        entities=[
            EntityNode(
                name="user",
                # Missing 'id' field (V008)
                fields=[FieldNode(name="email", field_type=FieldType.EMAIL, required=True)]
            )
        ]
    )
    
    ui = UISchema(
        pages=[PageDefinition(route="/", title="Home")],
        # Broken UI -> API mapping (V016): Nav points to missing route
        navigation=[NavigationItem(label="Dashboard", route="/dashboard")]
    )
    
    api = APISchema(
        # Missing API CRUD endpoints for 'user' (V010)
        endpoints=[]
    )
    
    db = DBSchema(
        tables=[] # Missing DB table for 'user' (V006)
    )
    
    auth = AuthSchema(
        roles=[],
        permissions=[
            # Invalid role reference (V023: role 'admin' doesn't exist)
            PermissionDefinition(role="admin", actions=["read"], resource="user"),
            # Invalid permission reference (V007: resource 'invalid_entity' doesn't exist)
            PermissionDefinition(role="admin", actions=["write"], resource="invalid_entity")
        ]
    )
    
    bl = BusinessLogicSchema()
    
    spec = CompiledSpecification(
        ast=ast,
        ui_schema=ui,
        api_schema=api,
        db_schema=db,
        auth_schema=auth,
        business_logic=bl
    )

    validator = ValidationEngine()
    repairer = RepairEngine()
    
    # 2. Initial Validation
    initial_report = validator.validate(
        spec.ast, spec.ui_schema, spec.api_schema, spec.db_schema, spec.auth_schema, spec.business_logic
    )
    
    # 3. Run Repair
    repaired_spec, repair_report = repairer.repair(spec, initial_report, max_iterations=3)
    
    # 4. Generate Markdown
    md = [
        "# Repair Engine Demonstration\n",
        "This document demonstrates the cyclic auto-healing capabilities of the Repair Engine.\n",
        "## 1. Initial Validation Errors\n",
        "The following intentional errors were injected:\n"
    ]
    
    for issue in initial_report.issues:
        md.append(f"- **{issue.rule_id} ({issue.severity.value})**: {issue.message}")
        if issue.suggestion:
            md.append(f"  - *Suggestion*: {issue.suggestion}")
            
    md.append("\n## 2. Repair Actions Taken\n")
    for action in repair_report.repairs:
        md.append(f"- **Fixed {action.issue_rule_id}** ({action.action_type} in {action.target_schema}): {action.description}")
        md.append(f"  - *Changes*: `{action.changes}`")
        
    md.append("\n## 3. Revalidation Result\n")
    md.append(f"- **Validation Passed**: {repair_report.revalidation_passed}")
    md.append(f"- **Iterations Used**: {repair_report.iterations_used}")
    md.append(f"- **Repair Time**: {repair_report.repair_time_ms}ms\n")
    
    md.append("## 4. Final Corrected Schemas Snippets\n")
    md.append("### AST (User Entity Fixed)")
    md.append("```json")
    md.append(repaired_spec.ast.model_dump_json(indent=2))
    md.append("```\n")
    
    md.append("### DB Schema (Table & PK Fixed)")
    md.append("```json")
    md.append(repaired_spec.db_schema.model_dump_json(indent=2))
    md.append("```\n")
    
    md.append("### API Schema (Missing Endpoints Fixed)")
    md.append("```json")
    md.append(repaired_spec.api_schema.model_dump_json(indent=2))
    md.append("```\n")

    md.append("### Auth Schema (Roles & Permissions Fixed)")
    md.append("```json")
    md.append(repaired_spec.auth_schema.model_dump_json(indent=2))
    md.append("```\n")
    
    md.append("### UI Schema (Broken Nav Fixed)")
    md.append("```json")
    md.append(repaired_spec.ui_schema.model_dump_json(indent=2))
    md.append("```\n")

    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../RepairEngineDemo.md"))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    print(f"Demo generated at {output_path}")

if __name__ == "__main__":
    run_demo()
