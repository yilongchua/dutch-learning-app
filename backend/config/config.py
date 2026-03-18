import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Get the absolute path to the backend directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR.parent / "data"

# Ensure sub-application data directories exist
DUTCH_DATA_DIR = DATA_DIR / "app" / "dutch"
THENEWS_DATA_DIR = DATA_DIR / "app" / "thenews"
GRAPHICS_GENERATION_DATA_DIR = DATA_DIR / "app" / "graphics_generation"

for new_dir in [DUTCH_DATA_DIR, THENEWS_DATA_DIR, GRAPHICS_GENERATION_DATA_DIR]:
    os.makedirs(new_dir, exist_ok=True)

class Settings(BaseSettings):
    # App Names for prefixes
    APP_NAME: str = "YL Unified App"
    
    # Database Settings
    DUTCH_DB_URL: str = Field(
        default=f"sqlite:///{DUTCH_DATA_DIR}/dutch.db",
        env="DUTCH_DB_URL"
    )
    THENEWS_DB_URL: str = Field(
        default=f"sqlite:///{THENEWS_DATA_DIR}/the_news.db",
        env="THENEWS_DB_URL"
    )
    GRAPHICS_GENERATION_DB_URL: str = Field(
        default=f"sqlite:///{GRAPHICS_GENERATION_DATA_DIR}/graphics_generation.db",
        env="GRAPHICS_GENERATION_DB_URL"
    )

    # API Keys / External Services
    COMFYUI_API_URL: str = Field(
        default="http://192.168.1.21:8188",
        env="COMFYUI_API_URL"
    )
    SEARXNG_URL: str = Field(
        default="http://localhost:8888/search",
        env="SEARXNG_URL"
    )
    SEARXNG_SECRET: Optional[str] = Field(
        default=None,
        env="SEARXNG_SERECT"
    )
    
    # LLM Settings
    LOCAL_LLM_URL: str = Field(
        default="http://192.168.1.21:1234/v1",
        env="LOCAL_LLM_URL"
    )
    MODEL: str = Field(
        default="openai/gpt-oss-120b",
        env="MODEL"
    )

    # Directories
    COMFYUI_DIR: str = Field(
        default="/Volumes/comfyUI/output",
        env="COMFYUI_DIR"
    )
    IMAGE_DIR: str = Field(
        default=str(DATA_DIR / "images"),
        env="IMAGE_DIR"
    )
    AUDIO_DIR: str = Field(
        default=str(DATA_DIR / "audio"),
        env="AUDIO_DIR"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Ensure sub-directories exist
os.makedirs(settings.IMAGE_DIR, exist_ok=True)
os.makedirs(settings.AUDIO_DIR, exist_ok=True)