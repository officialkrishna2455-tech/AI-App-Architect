from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db, shutdown_db

from app.api.compile import router as compile_router
from app.api.validate import router as validate_router
from app.api.repair import router as repair_router
from app.api.simulate import router as simulate_router
from app.api.runs import router as runs_router
from app.api.metrics import router as metrics_router
from app.api.auth import router as auth_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await shutdown_db()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Requirement Compiler API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(compile_router, prefix="/api/v1")
app.include_router(validate_router, prefix="/api/v1")
app.include_router(repair_router, prefix="/api/v1")
app.include_router(simulate_router, prefix="/api/v1")
app.include_router(runs_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "ok", "version": settings.app_version}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
