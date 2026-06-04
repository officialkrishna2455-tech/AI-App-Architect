"""
Application configuration — Pydantic Settings with environment variable binding.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # ── Application ──────────────────────────────────────────────
    app_name: str = "Requirement Compiler"
    app_version: str = "1.0.0"
    debug: bool = False

    # ── Database ─────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./requirement_compiler.db"

    # ── Authentication (single-user mode) ────────────────────────
    secret_key: str = "requirement-compiler-secret-change-in-production"
    access_token_expire_minutes: int = 1440  # 24 hours
    admin_username: str = "admin"
    admin_password: str = "compiler2024"

    # ── CORS ─────────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # ── Compiler ─────────────────────────────────────────────────
    max_parallel_runs: int = 4
    compilation_timeout_seconds: int = 120
    spacy_model: str = "en_core_web_sm"

    # ── Paths ────────────────────────────────────────────────────
    base_dir: Path = Path(__file__).parent.parent

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — call this instead of constructing Settings()."""
    return Settings()
