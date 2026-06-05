import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import async_session_factory, init_db
from app.evaluation.runner import EvaluationRunner
from app.evaluation.prompts import EvaluationPrompts

async def generate_markdown_report(metrics, results):
    report = f"""# Validation & Reliability Evaluation Report

## 1. Summary Metrics
- **Total Runs**: {metrics.total_runs}
- **Overall Success Rate**: {metrics.success_rate * 100:.2f}%
- **Validation Pass Rate**: {metrics.average_validation_pass_rate * 100:.2f}%
- **Simulation Pass Rate**: {metrics.average_simulation_pass_rate * 100:.2f}%
- **Average Repair Count**: {metrics.average_repair_rate:.2f} per run
- **Average Latency**: {metrics.average_latency_ms:.2f} ms

## 2. P-Level Latencies
- **P50 Latency**: {metrics.p50_latency_ms} ms
- **P95 Latency**: {metrics.p95_latency_ms} ms
- **P99 Latency**: {metrics.p99_latency_ms} ms

## 3. Failure Categories
"""
    if not metrics.failure_categories:
        report += "- No failures recorded.\n"
    for cat, count in metrics.failure_categories.items():
        report += f"- **{cat}**: {count}\n"
        
    report += "\n## 4. Run Details\n\n"
    
    for r in results:
        status = "✅ Pass" if r.success else "❌ Fail"
        report += f"### Prompt {r.prompt_id} ({r.prompt_type})\n"
        report += f"- **Status**: {status}\n"
        report += f"- **Validation Pass Rate**: {r.validation_pass_rate * 100:.2f}%\n"
        report += f"- **Simulation Pass Rate**: {r.simulation_pass_rate * 100:.2f}%\n"
        report += f"- **Repairs**: {r.repair_count}\n"
        report += f"- **Latency**: {r.latency_ms} ms\n"
        if r.error_message:
            report += f"- **Error**: {r.error_message}\n"
        report += "\n"
        
    report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ReliabilityReport.md"))
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report written to {report_path}")

async def main():
    await init_db()
    runner = EvaluationRunner()
    
    all_prompts = EvaluationPrompts.get_all()
    prompt_ids = [p[0] for p in all_prompts]
    
    print(f"Running evaluations for {len(prompt_ids)} prompts...")
    
    async with async_session_factory() as db:
        response = await runner.run(prompt_ids, db)
        
    await generate_markdown_report(response.aggregate_metrics, response.results)
    
if __name__ == "__main__":
    asyncio.run(main())
