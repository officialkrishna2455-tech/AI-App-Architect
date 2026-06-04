from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.requests import RepairRequest
from app.schemas.responses import RepairReport
from app.models.run import CompilationRun
from app.compiler.repair_engine import RepairEngine
from app.schemas.ast_models import (
    RequirementAST,
    UISchema,
    APISchema,
    DBSchema,
    AuthSchema,
    BusinessLogicSchema,
    ValidationReport,
    CompiledSpecification
)

router = APIRouter(tags=["compiler"])

@router.post("/repair", response_model=RepairReport)
async def repair_run(request: RepairRequest, db: AsyncSession = Depends(get_db)):
    run = await db.get(CompilationRun, request.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    if not run.validation_report_json:
        raise HTTPException(status_code=400, detail="Run has no validation report to repair")
        
    ast = RequirementAST.model_validate_json(run.ast_json)
    ui_schema = UISchema.model_validate_json(run.ui_schema_json)
    api_schema = APISchema.model_validate_json(run.api_schema_json)
    db_schema = DBSchema.model_validate_json(run.db_schema_json)
    auth_schema = AuthSchema.model_validate_json(run.auth_schema_json)
    business_logic = BusinessLogicSchema.model_validate_json(run.business_logic_json)
    validation_report = ValidationReport.model_validate_json(run.validation_report_json)
    
    spec = CompiledSpecification(
        ast=ast,
        ui_schema=ui_schema,
        api_schema=api_schema,
        db_schema=db_schema,
        auth_schema=auth_schema,
        business_logic=business_logic
    )
    
    repair_engine = RepairEngine()
    repaired_spec, report = repair_engine.repair(spec, validation_report, request.max_iterations)
    
    # Update DB
    run.ast_json = repaired_spec.ast.model_dump_json()
    run.ui_schema_json = repaired_spec.ui_schema.model_dump_json()
    run.api_schema_json = repaired_spec.api_schema.model_dump_json()
    run.db_schema_json = repaired_spec.db_schema.model_dump_json()
    run.auth_schema_json = repaired_spec.auth_schema.model_dump_json()
    run.business_logic_json = repaired_spec.business_logic.model_dump_json()
    
    run.repair_report_json = report.model_dump_json()
    run.repair_count = report.total_repairs
    await db.commit()
    
    return report
