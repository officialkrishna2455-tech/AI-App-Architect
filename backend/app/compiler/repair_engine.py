import time
import copy
from app.schemas.ast_models import (
    CompiledSpecification,
    ValidationReport,
    RepairReport,
    RepairAction,
    Severity,
    EndpointDefinition,
    PageDefinition,
    FieldNode,
    FieldType,
    RelationNode,
    RelationType,
    EntityNode
)

class RepairEngine:
    """
    Targeted repair of validation issues without regenerating everything.
    """

    def repair(self, 
               spec: CompiledSpecification, 
               validation_report: ValidationReport, 
               max_iterations: int = 3) -> tuple[CompiledSpecification, RepairReport]:
        
        start_time = time.time()
        repair_report = RepairReport()
        
        # Deep copy to avoid mutating the original until we decide to
        repaired_spec = spec.model_copy(deep=True)
        
        for issue in validation_report.issues:
            if issue.severity == Severity.INFO:
                continue
                
            action = None
            
            # Simple heuristic repairs based on Rule IDs
            if issue.rule_id == "V008":
                # Missing PK
                entity_name = issue.message.split()[1] # "Entity [name] is missing..."
                entity = repaired_spec.ast.get_entity(entity_name)
                if entity:
                    entity.fields.insert(0, FieldNode(name="id", field_type=FieldType.UUID, required=True, unique=True, indexed=True))
                    
                    # Fix DB schema too
                    for table in repaired_spec.db_schema.tables:
                        if table.name == f"{entity_name}s":
                            from app.schemas.ast_models import ColumnDefinition
                            table.columns.insert(0, ColumnDefinition(name="id", data_type="UUID", primary_key=True))
                            break
                            
                    action = RepairAction(
                        issue_rule_id=issue.rule_id,
                        action_type="add",
                        target_schema="db",
                        target_path=f"tables.[name='{entity_name}s'].columns",
                        description=f"Added primary key 'id' to entity {entity_name}"
                    )
                    
            elif issue.rule_id == "V009":
                # Missing timestamps
                entity_name = issue.message.split()[1]
                entity = repaired_spec.ast.get_entity(entity_name)
                if entity:
                    entity.fields.append(FieldNode(name="created_at", field_type=FieldType.DATETIME, required=True))
                    entity.fields.append(FieldNode(name="updated_at", field_type=FieldType.DATETIME, required=True))
                    action = RepairAction(
                        issue_rule_id=issue.rule_id,
                        action_type="add",
                        target_schema="ast",
                        target_path=f"entities.[name='{entity_name}'].fields",
                        description=f"Added timestamp fields to entity {entity_name}"
                    )
                    
            elif issue.rule_id == "V011":
                # Missing login page
                repaired_spec.ui_schema.pages.append(PageDefinition(
                    route="/login",
                    title="Login",
                    layout="auth",
                    auth_required=False
                ))
                action = RepairAction(
                    issue_rule_id=issue.rule_id,
                    action_type="add",
                    target_schema="ui",
                    target_path="pages",
                    description="Added login page due to auth middleware requirement"
                )
                
            if action:
                repair_report.repairs.append(action)
            else:
                repair_report.unresolvable.append(issue)
                
        repair_report.repair_time_ms = int((time.time() - start_time) * 1000)
        return repaired_spec, repair_report
