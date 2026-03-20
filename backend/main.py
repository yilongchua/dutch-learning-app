import sys
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# Ensure the project root is in sys.path
# We add the parent directory so that 'backend.' imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config.config import settings
from backend.app.dutch.router import router as dutch_router
from backend.app.thenews.router import router as news_router
from backend.app.thenews.schema.news_item import NewsItem
from backend.app.dutch.schema.schemas import ExerciseContent
from backend.app.dutch.core.database import init_db as init_dutch_db
from backend.app.thenews.core.database import init_db as init_news_db
from backend.app.dutch.service.exercise_queue import exercise_queue_service
from backend.app.graphics_generation.router import router as graphics_generation_router
from backend.app.graphics_generation.core.database import init_db as init_graphics_db
from backend.app.thenews.service.image_sync_service import background_image_sync
from backend.app.scheduler.router import router as scheduler_router
from backend.app.scheduler.service.scheduler_service import scheduler_service

# Ensure all models are registered in SQLModel's metadata
# We import them above to trigger the registration

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Databases
    print(f"Initializing Dutch DB at {settings.DUTCH_DB_URL}")
    try:
        init_dutch_db()
    except Exception as e:
        print(f"DB Init Warning (Dutch): {e}")

    print(f"Initializing News DB at {settings.THENEWS_DB_URL}")
    try:
        init_news_db()
    except Exception as e:
        print(f"DB Init Warning (News): {e}")
    
    print(f"Initializing Graphics Generation DB at {settings.GRAPHICS_GENERATION_DB_URL}")
    try:
        init_graphics_db()
    except Exception as e:
        print(f"DB Init Warning (Graphics): {e}")
    
    # Start Scheduler (JSON-based, no DB init needed)
    scheduler_service.start()
    
    # Create necessary folders
    os.makedirs(settings.IMAGE_DIR, exist_ok=True)
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
    
    # Start background sync
    image_sync_task = asyncio.create_task(background_image_sync())
    exercise_queue_service.start_background_refill()

    try:
        yield
    finally:
        image_sync_task.cancel()
        await exercise_queue_service.stop_background_refill()

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(dutch_router, prefix="/api/dutch")
app.include_router(news_router, prefix="/api/news")
app.include_router(graphics_generation_router, prefix="/api/graphics_generation", tags=["Graphics Generation"])
app.include_router(scheduler_router, prefix="/api/scheduler", tags=["Scheduler"])

# Media Library alias (for gallery)
from backend.app.graphics_generation.router import get_gallery
@app.get("/api/media_library")
async def media_library_root():
    return get_gallery()

# Mount static files
app.mount("/images", StaticFiles(directory=settings.IMAGE_DIR), name="images")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Unified YL Learning App API",
        "apps": ["dutch", "news", "graphics_generation"],
        "status": "online"
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.BACKEND_PORT, reload=True)
