import asyncio
import os
import sys
import json

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import async_session_factory, init_db
from app.compiler.pipeline import CompilationPipeline
from app.schemas.requests import CompileOptions

async def main():
    await init_db()
    
    requirements = "Build a CRM with login, contacts, dashboard, role-based access, premium plans, and admin analytics."
    options = CompileOptions(target_stack="nextjs-fastapi", include_simulation=True)
    
    pipeline = CompilationPipeline()
    response = pipeline.compile_sync(requirements, options, run_id="demo_run")
    
    output = {
        "status": response.status,
        "metrics": response.metrics.model_dump(),
        "ast_entities": [e.name for e in response.ast.entities],
        "ast_features": [f.name for f in response.ast.features],
        "ast_roles": [r.name for r in response.ast.roles],
        "validation_passed": response.validation_report.passed if response.validation_report else False,
        "simulation_pass_rate": response.simulation_report.pass_rate if response.simulation_report else 0.0
    }
    
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../CRM_Compilation_Result.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
        
    print(f"Compilation finished. Result written to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
