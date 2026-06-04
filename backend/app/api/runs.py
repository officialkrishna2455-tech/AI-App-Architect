from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models.run import CompilationRun
from app.schemas.responses import RunListResponse, RunSummary, CompileResponse

router = APIRouter(tags=["runs"])

@router.get("/runs", response_model=RunListResponse)
async def list_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(CompilationRun)
    if status:
        query = query.where(CompilationRun.status == status)
        
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Fetch paginated
    query = query.order_by(desc(CompilationRun.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    runs = result.scalars().all()
    
    summaries = []
    for r in runs:
        summaries.append(RunSummary(
            run_id=r.id,
            status=r.status,
            requirements_preview=r.requirements[:200] + ("..." if len(r.requirements) > 200 else ""),
            total_latency_ms=r.total_latency_ms,
            validation_pass_rate=r.validation_pass_rate,
            simulation_pass_rate=r.simulation_pass_rate,
            entity_count=r.entity_count,
            feature_count=r.feature_count,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat()
        ))
        
    return RunListResponse(
        runs=summaries,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )

@router.get("/runs/{run_id}", response_model=CompileResponse)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    import json
    from app.schemas.ast_models import RequirementAST, ValidationReport, RepairReport, SimulationReport
    from app.schemas.responses import SchemaOutput, CompileMetrics, KnowledgeGraphOutput
    from app.schemas.ast_models import UISchema, APISchema, DBSchema, AuthSchema, BusinessLogicSchema
    
    run = await db.get(CompilationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    schema_out = SchemaOutput()
    if run.ui_schema_json: schema_out.ui_schema = UISchema.model_validate_json(run.ui_schema_json)
    if run.api_schema_json: schema_out.api_schema = APISchema.model_validate_json(run.api_schema_json)
    if run.db_schema_json: schema_out.db_schema = DBSchema.model_validate_json(run.db_schema_json)
    if run.auth_schema_json: schema_out.auth_schema = AuthSchema.model_validate_json(run.auth_schema_json)
    if run.business_logic_json: schema_out.business_logic_schema = BusinessLogicSchema.model_validate_json(run.business_logic_json)
    
    kg_out = KnowledgeGraphOutput()
    if run.knowledge_graph_json:
        kg_dict = json.loads(run.knowledge_graph_json)
        kg_out = KnowledgeGraphOutput(**kg_dict)
        
    return CompileResponse(
        run_id=run.id,
        status=run.status,
        ast=RequirementAST.model_validate_json(run.ast_json) if run.ast_json else RequirementAST(),
        schemas=schema_out,
        validation_report=ValidationReport.model_validate_json(run.validation_report_json) if run.validation_report_json else ValidationReport(),
        repair_report=RepairReport.model_validate_json(run.repair_report_json) if run.repair_report_json else RepairReport(),
        simulation_report=SimulationReport.model_validate_json(run.simulation_report_json) if run.simulation_report_json else SimulationReport(),
        knowledge_graph=kg_out,
        metrics=CompileMetrics.model_validate_json(run.metrics_json) if run.metrics_json else CompileMetrics()
    )

@router.delete("/runs/{run_id}")
async def delete_run(run_id: str, db: AsyncSession = Depends(get_db)):
    run = await db.get(CompilationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    await db.delete(run)
    await db.commit()
    return {"status": "success"}
