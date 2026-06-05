import uuid
import json
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.requests import CompileRequest
from app.schemas.responses import CompileResponse
from app.models.run import CompilationRun
from app.compiler.pipeline import CompilationPipeline

router = APIRouter(tags=["compiler"])
pipeline = CompilationPipeline()

from app.database import async_session_factory

async def background_compile(run_id: str, requirements: str, options, resume_ast=None):
    async with async_session_factory() as db:
        # Simplified here to just run the pipeline and update at the end
        try:
            response = pipeline.compile_sync(requirements, options, run_id=run_id, resume_ast=resume_ast)
            
            # Save to DB
            run = await db.get(CompilationRun, run_id)
            if run:
                run.status = "completed"
                run.ast_json = response.ast.model_dump_json()
                run.ui_schema_json = response.schemas.ui_schema.model_dump_json()
                run.api_schema_json = response.schemas.api_schema.model_dump_json()
                run.db_schema_json = response.schemas.db_schema.model_dump_json()
                run.auth_schema_json = response.schemas.auth_schema.model_dump_json()
                run.business_logic_json = response.schemas.business_logic_schema.model_dump_json()
                run.knowledge_graph_json = json.dumps(response.knowledge_graph.model_dump())
                run.validation_report_json = response.validation_report.model_dump_json()
                run.repair_report_json = response.repair_report.model_dump_json()
                run.simulation_report_json = response.simulation_report.model_dump_json() if response.simulation_report else None
                run.metrics_json = response.metrics.model_dump_json()
                
                run.total_latency_ms = response.metrics.total_latency_ms
                run.validation_pass_rate = response.metrics.validation_pass_rate
                run.simulation_pass_rate = response.metrics.simulation_pass_rate
                run.entity_count = len(response.ast.entities)
                run.feature_count = len(response.ast.features)
                run.repair_count = response.metrics.repair_count
                
                await db.commit()
        except Exception as e:
            run = await db.get(CompilationRun, run_id)
            if run:
                run.status = "failed"
                run.error_message = str(e)
                await db.commit()


@router.post("/compile", response_model=CompileResponse)
async def compile_requirements(
    request: CompileRequest, 
    background_tasks: BackgroundTasks,
    sync: bool = False,
    db: AsyncSession = Depends(get_db)
):
    run_id = str(uuid.uuid4())
    
    # Check if resuming
    resume_ast = None
    if request.resume_from_run_id:
        old_run = await db.get(CompilationRun, request.resume_from_run_id)
        if old_run and old_run.ast_json:
            from app.schemas.ast_models import RequirementAST
            resume_ast = RequirementAST.model_validate_json(old_run.ast_json)
    
    # Create run record
    run = CompilationRun(
        id=run_id,
        requirements=request.requirements,
        status="queued",
        options_json=request.options.model_dump_json()
    )
    db.add(run)
    await db.commit()
    
    if sync:
        # Run synchronously
        response = pipeline.compile_sync(request.requirements, request.options, run_id=run_id, resume_ast=resume_ast)
        
        # Save results
        run.status = "completed"
        run.ast_json = response.ast.model_dump_json()
        run.ui_schema_json = response.schemas.ui_schema.model_dump_json()
        run.api_schema_json = response.schemas.api_schema.model_dump_json()
        run.db_schema_json = response.schemas.db_schema.model_dump_json()
        run.auth_schema_json = response.schemas.auth_schema.model_dump_json()
        run.business_logic_json = response.schemas.business_logic_schema.model_dump_json()
        run.knowledge_graph_json = json.dumps(response.knowledge_graph.model_dump())
        run.validation_report_json = response.validation_report.model_dump_json()
        run.repair_report_json = response.repair_report.model_dump_json()
        run.simulation_report_json = response.simulation_report.model_dump_json() if response.simulation_report else None
        run.metrics_json = response.metrics.model_dump_json()
        
        run.total_latency_ms = response.metrics.total_latency_ms
        run.validation_pass_rate = response.metrics.validation_pass_rate
        run.simulation_pass_rate = response.metrics.simulation_pass_rate
        run.entity_count = len(response.ast.entities)
        run.feature_count = len(response.ast.features)
        run.repair_count = response.metrics.repair_count
        
        await db.commit()
        return response
    else:
        # Run in background
        background_tasks.add_task(background_compile, run_id, request.requirements, request.options, resume_ast)
        
        # Return pending response
        from app.schemas.responses import CompileMetrics, SchemaOutput, KnowledgeGraphOutput
        from app.schemas.ast_models import RequirementAST, ValidationReport, RepairReport, SimulationReport
        
        return CompileResponse(
            run_id=run_id,
            status="queued",
            ast=RequirementAST(),
            schemas=SchemaOutput(),
            validation_report=ValidationReport(),
            repair_report=RepairReport(),
            simulation_report=SimulationReport(),
            knowledge_graph=KnowledgeGraphOutput(),
            metrics=CompileMetrics()
        )
