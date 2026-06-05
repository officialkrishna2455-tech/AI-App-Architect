import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import FastAPI
import json

from app.main import app
from app.database import Base, get_db

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.anyio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.anyio
async def test_compile_endpoint():
    # The pipeline uses ClaudeModel, but if we don't mock it, it'll make real API calls.
    # We will patch the CompilationPipeline.compile_sync to return a dummy response,
    # or patch the LLM layer. To keep it simple, we'll patch compile_sync.
    from app.compiler.pipeline import CompilationPipeline
    from app.schemas.responses import CompileResponse, CompileMetrics, SchemaOutput, KnowledgeGraphOutput
    from app.schemas.ast_models import RequirementAST, EntityNode, ValidationReport, RepairReport, SimulationReport
    
    def mock_compile_sync(self, text, options, run_id):
        ast = RequirementAST(entities=[EntityNode(name="TestEntity")])
        return CompileResponse(
            run_id=run_id,
            status="completed",
            ast=ast,
            schemas=SchemaOutput(),
            validation_report=ValidationReport(),
            repair_report=RepairReport(),
            simulation_report=SimulationReport(),
            knowledge_graph=KnowledgeGraphOutput(),
            metrics=CompileMetrics(total_latency_ms=100)
        )
        
    original_compile_sync = CompilationPipeline.compile_sync
    CompilationPipeline.compile_sync = mock_compile_sync

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            req_data = {
                "requirements": "Create a test app",
                "options": {
                    "include_simulation": False
                }
            }
            # Test async compile (background task)
            response = await ac.post("/api/v1/compile?sync=false", json=req_data)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "queued"
            run_id = data["run_id"]
            
            # Wait up to 2 seconds for background task to run
            for _ in range(20):
                res_run = await ac.get(f"/api/v1/runs/{run_id}")
                if res_run.json()["status"] == "completed":
                    break
                await asyncio.sleep(0.1)
            
            # Fetch the run one last time to assert
            res_run = await ac.get(f"/api/v1/runs/{run_id}")
            assert res_run.status_code == 200
            assert res_run.json()["status"] == "completed"
            
            # Test sync compile
            response = await ac.post("/api/v1/compile?sync=true", json=req_data)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert len(data["ast"]["entities"]) == 1
            
            # Test getting all runs
            res_runs = await ac.get("/api/v1/runs")
            assert res_runs.status_code == 200
            assert len(res_runs.json()["runs"]) == 2
            
            # Test metrics
            res_metrics = await ac.get("/api/v1/metrics")
            assert res_metrics.status_code == 200
            assert res_metrics.json()["total_runs"] == 2
    finally:
        CompilationPipeline.compile_sync = original_compile_sync

@pytest.mark.anyio
async def test_validate_and_repair_endpoints():
    # Insert a dummy run to test validate and repair
    async with TestingSessionLocal() as db:
        from app.models.run import CompilationRun
        from app.schemas.ast_models import RequirementAST, EntityNode
        import uuid
        
        run_id = str(uuid.uuid4())
        ast = RequirementAST(entities=[EntityNode(name="TestEntity")])
        from app.schemas.ast_models import UISchema, APISchema, DBSchema, AuthSchema, BusinessLogicSchema
        
        run = CompilationRun(
            id=run_id,
            requirements="test",
            status="completed",
            ast_json=ast.model_dump_json(),
            ui_schema_json=UISchema().model_dump_json(),
            api_schema_json=APISchema().model_dump_json(),
            db_schema_json=DBSchema().model_dump_json(),
            auth_schema_json=AuthSchema().model_dump_json(),
            business_logic_json=BusinessLogicSchema().model_dump_json()
        )
        db.add(run)
        await db.commit()
        
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Validate
        val_res = await ac.post("/api/v1/validate", json={"run_id": run_id})
        assert val_res.status_code == 200
        val_data = val_res.json()
        assert "passed" in val_data
        
        # Repair (will fail due to lack of mock LLM unless we mock the engine)
        # We'll mock the repair engine
        from app.compiler.repair_engine import RepairEngine
        from app.schemas.ast_models import RepairReport
        from app.schemas.ast_models import CompiledSpecification
        
        def mock_repair(self, spec, val_report, max_iterations):
            return CompiledSpecification(), RepairReport()
            
        original_repair = RepairEngine.repair
        RepairEngine.repair = mock_repair
        
        try:
            rep_res = await ac.post("/api/v1/repair", json={"run_id": run_id, "max_iterations": 1})
            assert rep_res.status_code == 200
            rep_data = rep_res.json()
            assert "total_repairs" in rep_data
        finally:
            RepairEngine.repair = original_repair

@pytest.mark.anyio
async def test_simulate_endpoint():
    async with TestingSessionLocal() as db:
        from app.models.run import CompilationRun
        from app.schemas.ast_models import RequirementAST, EntityNode
        import uuid
        
        run_id = str(uuid.uuid4())
        ast = RequirementAST(entities=[EntityNode(name="TestEntity")])
        from app.schemas.ast_models import UISchema, APISchema, DBSchema, AuthSchema, BusinessLogicSchema
        
        run = CompilationRun(
            id=run_id,
            requirements="test",
            status="completed",
            ast_json=ast.model_dump_json(),
            ui_schema_json=UISchema().model_dump_json(),
            api_schema_json=APISchema().model_dump_json(),
            db_schema_json=DBSchema().model_dump_json(),
            auth_schema_json=AuthSchema().model_dump_json(),
            business_logic_json=BusinessLogicSchema().model_dump_json()
        )
        db.add(run)
        await db.commit()
        
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Simulate
        sim_res = await ac.post("/api/v1/simulate", json={"run_id": run_id})
        assert sim_res.status_code == 200
        sim_data = sim_res.json()
        assert "simulation_status" in sim_data
