import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Get the absolute path to the backend directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR.parent / "data"

# ---------------------------------------------------------------------------
# Per-app data directories  (auto-created on import)
# ---------------------------------------------------------------------------
DUTCH_DATA_DIR             = DATA_DIR / "app" / "dutch"
THENEWS_DATA_DIR           = DATA_DIR / "app" / "thenews"
GRAPHICS_GENERATION_DATA_DIR = DATA_DIR / "app" / "graphics_generation"
SCHEDULER_DATA_DIR         = DATA_DIR / "app" / "scheduler"

for _dir in [DUTCH_DATA_DIR, THENEWS_DATA_DIR, GRAPHICS_GENERATION_DATA_DIR, SCHEDULER_DATA_DIR]:
    os.makedirs(_dir, exist_ok=True)

# ---------------------------------------------------------------------------
# Master Settings (single source of truth for ALL sub-apps)
# ---------------------------------------------------------------------------
class Settings(BaseSettings):
    APP_NAME: str = "YL Unified App"
    
    # Connection Ports
    BACKEND_PORT: int = Field(default=8010, env="BACKEND_PORT")
    FRONTEND_PORT: int = Field(default=5173, env="FRONTEND_PORT")
    
    # Database Settings

    # ── Ports ──────────────────────────────────────────────────────────────
    BACKEND_PORT: int  = Field(default=8010, env="BACKEND_PORT")
    FRONTEND_PORT: int = Field(default=5173, env="FRONTEND_PORT")

    # ── Database URLs ───────────────────────────────────────────────────────
    DUTCH_DB_URL: str = Field(
        default=f"sqlite:///{DUTCH_DATA_DIR.resolve()}/dutch.db",
        env="DUTCH_DB_URL",
    )
    THENEWS_DB_URL: str = Field(
        default=f"sqlite:///{THENEWS_DATA_DIR.resolve()}/the_news.db",
        env="THENEWS_DB_URL",
    )
    GRAPHICS_GENERATION_DB_URL: str = Field(
        default=f"sqlite:///{GRAPHICS_GENERATION_DATA_DIR.resolve()}/graphics_generation.db",
        env="GRAPHICS_GENERATION_DB_URL",
    )
    # Scheduler uses a JSON file — no DB URL needed.

    # ── External Services ───────────────────────────────────────────────────
    COMFYUI_API_URL: str = Field(default="http://localhost:8188", env="COMFYUI_API_URL")
    SEARXNG_URL: str     = Field(default="http://localhost:8888/search", env="SEARXNG_URL")
    SEARXNG_SECRET: Optional[str] = Field(default=None, env="SEARXNG_SERECT")

    # ── LLM ────────────────────────────────────────────────────────────────
    LOCAL_LLM_URL: str = Field(default="http://localhost:1234/v1", env="LOCAL_LLM_URL")
    MODEL: str         = Field(default="openai/gpt-oss-120b", env="MODEL")

    # ── File Directories ────────────────────────────────────────────────────
    COMFYUI_DIR: str = Field(default="/Volumes/comfyUI/output", env="COMFYUI_DIR")
    IMAGE_DIR: str   = Field(default=str(DATA_DIR / "images"), env="IMAGE_DIR")
    AUDIO_DIR: str   = Field(default=str(DATA_DIR / "audio"),  env="AUDIO_DIR")
    XTTS_SPEAKER_WAV: str = Field(default=str(DATA_DIR/ "max_verstappen_dutch.wav"), env="XTTS_SPEAKER_WAV")

    # Load from the project root .env
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / ".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()

# Ensure media directories exist
os.makedirs(settings.IMAGE_DIR, exist_ok=True)
os.makedirs(settings.AUDIO_DIR, exist_ok=True)
