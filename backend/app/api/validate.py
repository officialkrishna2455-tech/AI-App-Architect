import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.requests import ValidateRequest
from app.schemas.responses import ValidationReport
from app.models.run import CompilationRun
from app.compiler.validation_engine import ValidationEngine
from app.compiler.consistency_engine import ConsistencyEngine
from app.schemas.ast_models import (
    RequirementAST,
    UISchema,
    APISchema,
    DBSchema,
    AuthSchema,
    BusinessLogicSchema
)

router = APIRouter(tags=["compiler"])

@router.post("/validate", response_model=ValidationReport)
async def validate_run(request: ValidateRequest, db: AsyncSession = Depends(get_db)):
    run = await db.get(CompilationRun, request.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    if not run.ast_json:
        raise HTTPException(status_code=400, detail="Run has no generated schemas")
        
    ast = RequirementAST.model_validate_json(run.ast_json)
    ui_schema = UISchema.model_validate_json(run.ui_schema_json)
    api_schema = APISchema.model_validate_json(run.api_schema_json)
    db_schema = DBSchema.model_validate_json(run.db_schema_json)
    auth_schema = AuthSchema.model_validate_json(run.auth_schema_json)
    business_logic = BusinessLogicSchema.model_validate_json(run.business_logic_json)
    
    # Re-run consistency and validation
    consistency_engine = ConsistencyEngine()
    graph, graph_issues = consistency_engine.check(ast, ui_schema, api_schema, db_schema, auth_schema, business_logic)
    
    validation_engine = ValidationEngine()
    report = validation_engine.validate(ast, ui_schema, api_schema, db_schema, auth_schema, business_logic, graph_issues)
    
    # Update DB
    run.validation_report_json = report.model_dump_json()
    run.validation_pass_rate = 1.0 if report.passed else 0.0
    await db.commit()
    
    return report
