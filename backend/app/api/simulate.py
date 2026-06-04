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
    
    # Self-Healing Loop for standalone simulation endpoint
    repair_cycles = 0
    all_repair_actions = []
    
    while (
        report.pass_rate < 1.0 and 
        repair_cycles < request.max_repair_iterations
    ):
        repair_cycles += 1
        
        sim_issues = simulator.failures_to_issues(report)
        if not sim_issues:
            break
            
        from app.schemas.ast_models import ValidationReport
        from app.compiler.repair_engine import RepairEngine
        from app.compiler.validation_engine import ValidationEngine
        
        sim_validation_report = ValidationReport(issues=sim_issues)
        repair_engine = RepairEngine()
        validation_engine = ValidationEngine()
        
        spec, sim_repair_report = repair_engine.repair(
            spec, sim_validation_report, max_iterations=1
        )
        
        if sim_repair_report.repairs:
            all_repair_actions.extend([
                {"rule_id": r.issue_rule_id, "action": r.action_type, "target": r.target_path}
                for r in sim_repair_report.repairs
            ])
        
        _ = validation_engine.validate(
            spec.ast, spec.ui_schema, spec.api_schema,
            spec.db_schema, spec.auth_schema, spec.business_logic
        )
        
        report = simulator.simulate(spec.ast, spec, request.categories)

    report.repair_cycles = repair_cycles
    report.auto_repaired = repair_cycles > 0
    report.repairs_triggered = all_repair_actions
    
    # Update DB
    run.simulation_report_json = report.model_dump_json()
    run.simulation_pass_rate = report.pass_rate
    
    # If we repaired, we also need to save the new schemas
    if repair_cycles > 0:
        run.ui_schema_json = spec.ui_schema.model_dump_json()
        run.api_schema_json = spec.api_schema.model_dump_json()
        run.db_schema_json = spec.db_schema.model_dump_json()
        run.auth_schema_json = spec.auth_schema.model_dump_json()
        run.business_logic_json = spec.business_logic.model_dump_json()

    await db.commit()
    
    return report
