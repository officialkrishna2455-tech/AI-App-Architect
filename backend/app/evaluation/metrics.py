from typing import Sequence
from app.models.metric import EvaluationResult
from app.schemas.responses import MetricsResponse

class EvaluationMetrics:
    @staticmethod
    def compute(results: Sequence[EvaluationResult]) -> MetricsResponse:
        total = len(results)
        if total == 0:
            return MetricsResponse()
            
        success_count = sum(1 for r in results if r.success)
        avg_latency = sum(r.latency_ms for r in results) / total
        avg_val = sum(r.validation_pass_rate for r in results) / total
        avg_sim = sum(r.simulation_pass_rate for r in results) / total
        avg_repair = sum(r.repair_count for r in results) / total
        
        latencies = sorted([r.latency_ms for r in results])
        
        return MetricsResponse(
            total_runs=total,
            success_rate=success_count / total,
            average_latency_ms=avg_latency,
            average_validation_pass_rate=avg_val,
            average_simulation_pass_rate=avg_sim,
            average_repair_rate=avg_repair,
            p50_latency_ms=latencies[int(total * 0.5)] if total > 0 else 0,
            p95_latency_ms=latencies[int(total * 0.95)] if total > 0 else 0,
            p99_latency_ms=latencies[int(total * 0.99)] if total > 0 else 0
        )
