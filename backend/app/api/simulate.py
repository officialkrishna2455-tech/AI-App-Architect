from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.requests import SimulateRequest
from app.schemas.responses import SimulationReport
from app.models.run import CompilationRun
from app.compiler.runtime_simulator import RuntimeSimulator
from app.schemas.ast_models import (
    RequirementAST,
    UISchema,
    APISchema,
    DBSchema,
    AuthSchema,
    BusinessLogicSchema,
    CompiledSpecification
)

router = APIRouter(tags=["compiler"])

@router.post("/simulate", response_model=SimulationReport)
async def simulate_run(request: SimulateRequest, db: AsyncSession = Depends(get_db)):
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
    
    spec = CompiledSpecification(
        ast=ast,
        ui_schema=ui_schema,
        api_schema=api_schema,
        db_schema=db_schema,
        auth_schema=auth_schema,
        business_logic=business_logic
    )
    
    simulator = RuntimeSimulator()
    report = simulator.simulate(ast, spec, request.categories)
    
    # Update DB
    run.simulation_report_json = report.model_dump_json()
    run.simulation_pass_rate = report.pass_rate
    await db.commit()
    
    return report
