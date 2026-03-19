from fastapi import APIRouter, Depends, HTTPException
import os, sys
# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from sqlmodel import Session, select, func
from typing import List

from backend.app.thenews.core.database import get_session
from backend.app.thenews.schema.news_item import NewsItem, NewsItemRead
from backend.app.thenews.content_generation import ContentGenerator
from fastapi import BackgroundTasks

router = APIRouter(tags=["news"])
@router.get("/")
async def news_root():
    return {"status": "online", "app": "thenews"}

# ---------- NEWS ITEMS (Unified) ----------
@router.get("/news-items", response_model=List[NewsItemRead])
def list_news_items(session: Session = Depends(get_session)):
    """Returns all news items, randomized for the feed."""
    return session.exec(select(NewsItem).order_by(func.random())).all()

@router.get("/news-items/{item_id}", response_model=NewsItemRead)
def get_news_item(item_id: int, session: Session = Depends(get_session)):
    """Returns a single news item by ID."""
    item = session.get(NewsItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="NewsItem not found")
    return item
@router.post("/generate")
async def trigger_generation(background_tasks: BackgroundTasks):
    """Triggers the content generation pipeline in the background."""
    generator = ContentGenerator()
    background_tasks.add_task(generator.run_pipeline)
    return {"status": "started", "message": "Content generation pipeline is running in the background."}

# ---------- END OF ROUTER ----------

