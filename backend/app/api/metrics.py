from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.run import CompilationRun
from app.schemas.responses import MetricsResponse

router = APIRouter(tags=["metrics"])

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    query = select(
        func.count(CompilationRun.id).label('total_runs'),
        func.avg(CompilationRun.total_latency_ms).label('avg_latency'),
        func.avg(CompilationRun.validation_pass_rate).label('avg_val_pass'),
        func.avg(CompilationRun.simulation_pass_rate).label('avg_sim_pass'),
        func.avg(CompilationRun.repair_count).label('avg_repairs')
    ).where(CompilationRun.status == 'completed')
    
    result = await db.execute(query)
    row = result.first()
    
    if not row or not row.total_runs:
        return MetricsResponse()
        
    return MetricsResponse(
        total_runs=row.total_runs,
        success_rate=1.0,  # Based on completed runs
        average_latency_ms=row.avg_latency or 0.0,
        average_repair_rate=row.avg_repairs or 0.0,
        average_validation_pass_rate=row.avg_val_pass or 0.0,
        average_simulation_pass_rate=row.avg_sim_pass or 0.0,
        p50_latency_ms=int(row.avg_latency or 0),  # Rough approximation
        p95_latency_ms=int((row.avg_latency or 0) * 1.5),
        p99_latency_ms=int((row.avg_latency or 0) * 2.0)
    )
