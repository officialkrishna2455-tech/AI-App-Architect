import uuid
import time
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.metric import EvaluationResult
from app.models.run import CompilationRun
from app.evaluation.prompts import EvaluationPrompts
from app.evaluation.metrics import EvaluationMetrics
from app.compiler.pipeline import CompilationPipeline
from app.schemas.requests import CompileOptions
from app.schemas.responses import EvalRunResponse, EvalPromptResult
from app.database import async_session_factory

class EvaluationRunner:
    def __init__(self):
        self.pipeline = CompilationPipeline()

    async def run(self, prompt_ids: list[int], db: AsyncSession) -> EvalRunResponse:
        results = []
        
        options = CompileOptions(target_stack="nextjs-fastapi", include_simulation=True)
        
        for pid in prompt_ids:
            p_type, p_text = EvaluationPrompts.get_prompt(pid)
            if not p_text and p_type != "adversarial": # Empty string case
                continue
                
            run_id = str(uuid.uuid4())
            start_time = time.time()
            
            try:
                response = self.pipeline.compile_sync(p_text if p_text else "", options, run_id=run_id)
                
                # Save run
                run = CompilationRun(
                    id=run_id,
                    requirements=p_text if p_text else "",
                    status="completed",
                    total_latency_ms=response.metrics.total_latency_ms,
                    validation_pass_rate=response.metrics.validation_pass_rate,
                    simulation_pass_rate=response.metrics.simulation_pass_rate,
                    entity_count=len(response.ast.entities),
                    feature_count=len(response.ast.features),
                    repair_count=response.metrics.repair_count
                )
                db.add(run)
                
                eval_res = EvaluationResult(
                    id=str(uuid.uuid4()),
                    run_id=run_id,
                    prompt_id=pid,
                    prompt_type=p_type,
                    prompt_text=p_text if p_text else "",
                    success=True,
                    validation_pass_rate=response.metrics.validation_pass_rate,
                    simulation_pass_rate=response.metrics.simulation_pass_rate,
                    repair_count=response.metrics.repair_count,
                    latency_ms=response.metrics.total_latency_ms
                )
                db.add(eval_res)
                results.append(eval_res)
                
            except Exception as e:
                # Handle gracefully
                eval_res = EvaluationResult(
                    id=str(uuid.uuid4()),
                    run_id=None,
                    prompt_id=pid,
                    prompt_type=p_type,
                    prompt_text=p_text if p_text else "",
                    success=False,
                    latency_ms=int((time.time() - start_time) * 1000),
                    error_message=str(e)
                )
                db.add(eval_res)
                results.append(eval_res)
                
        await db.commit()
        
        agg_metrics = EvaluationMetrics.compute(results)
        
        api_results = []
        for r in results:
            api_results.append(EvalPromptResult(
                prompt_id=r.prompt_id,
                prompt_type=r.prompt_type,
                prompt_text=r.prompt_text,
                success=r.success,
                validation_pass_rate=r.validation_pass_rate,
                simulation_pass_rate=r.simulation_pass_rate,
                repair_count=r.repair_count,
                latency_ms=r.latency_ms,
                error_message=r.error_message or ""
            ))
            
        return EvalRunResponse(
            total_prompts=len(api_results),
            success_count=sum(1 for r in api_results if r.success),
            success_rate=agg_metrics.success_rate,
            results=api_results,
            aggregate_metrics=agg_metrics
        )
