from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.metric import EvaluationResult
from app.evaluation.runner import EvaluationRunner
from app.evaluation.prompts import EvaluationPrompts
from app.evaluation.metrics import EvaluationMetrics
from app.schemas.responses import EvalRunResponse, EvalPromptResult, MetricsResponse

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.post("/run", response_model=EvalRunResponse)
async def run_evaluation(db: AsyncSession = Depends(get_db)):
    """Run the evaluation suite over all prompts."""
    runner = EvaluationRunner()
    
    # Run for all prompts
    all_prompts = EvaluationPrompts.get_all()
    prompt_ids = [p[0] for p in all_prompts]
    
    return await runner.run(prompt_ids, db)


@router.get("/report", response_model=EvalRunResponse)
async def get_evaluation_report(db: AsyncSession = Depends(get_db)):
    """Get the latest evaluation results and aggregate metrics."""
    # Fetch all evaluation results (or latest N, but let's just get all for the dashboard)
    # Actually, we should probably fetch the latest set or all. Let's fetch all for simplicity.
    result = await db.execute(select(EvaluationResult).order_by(EvaluationResult.created_at.desc()))
    all_db_results = result.scalars().all()
    
    if not all_db_results:
        return EvalRunResponse()
        
    # Keep only the latest result for each prompt_id
    latest_results_map = {}
    for r in all_db_results:
        if r.prompt_id not in latest_results_map:
            latest_results_map[r.prompt_id] = r
            
    db_results = list(latest_results_map.values())
        
    agg_metrics = EvaluationMetrics.compute(db_results)
    
    api_results = []
    for r in db_results:
        api_results.append(EvalPromptResult(
            prompt_id=r.prompt_id,
            prompt_type=r.prompt_type,
            prompt_text=r.prompt_text,
            success=r.success,
            validation_pass_rate=r.validation_pass_rate,
            simulation_pass_rate=r.simulation_pass_rate,
            repair_count=r.repair_count,
            latency_ms=r.latency_ms,
            json_valid_rate=r.json_valid_rate,
            assumptions_made=r.assumptions_made,
            failure_category=r.failure_category or "",
            error_message=r.error_message or ""
        ))
        
    return EvalRunResponse(
        total_prompts=len(api_results),
        success_count=sum(1 for r in api_results if r.success),
        success_rate=agg_metrics.success_rate,
        results=api_results,
        aggregate_metrics=agg_metrics
    )
