from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
import httpx
import os
from backend.config.config import settings
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel

from .core.database import get_session
from .schema.models import GraphicsGenerationItem, GraphicsGenerationItemRead
from .service.logic import GraphicsGenerationService

router = APIRouter()
service = GraphicsGenerationService()

class EnhancePromptRequest(BaseModel):
    prompt: str

class GenerateRequest(BaseModel):
    original_prompt: str
    improved_prompt: str
    media_type: str

@router.post("/enhance-prompt")
async def enhance_prompt(request: EnhancePromptRequest):
    improved = await service.enhance_prompt(request.prompt)
    return {"improved_prompt": improved}

@router.post("/generate", response_model=GraphicsGenerationItemRead)
async def generate_media(request: GenerateRequest, session: Session = Depends(get_session)):
    prompt_to_use = request.improved_prompt if request.improved_prompt else request.original_prompt
    prompt_id = await service.generate_media(prompt_to_use, request.media_type)
    
    item = GraphicsGenerationItem(
        original_prompt=request.original_prompt,
        improved_prompt=request.improved_prompt,
        media_type=request.media_type,
        media_url=prompt_id # Store prompt_id as media_url until generation finishes
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.get("/history", response_model=List[GraphicsGenerationItemRead])
def get_history(skip: int = Query(0), limit: int = Query(20), session: Session = Depends(get_session)):
    items = session.exec(select(GraphicsGenerationItem).order_by(GraphicsGenerationItem.created_at.desc()).offset(skip).limit(limit)).all()
    return items

@router.delete("/history/{item_id}")
def delete_history_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(GraphicsGenerationItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {"status": "deleted"}

@router.get("/status/{prompt_id}")
async def check_status(prompt_id: str):
    status = await service.check_status(prompt_id)
    return status

@router.get("/view")
async def proxy_comfy_view(
    filename: str = Query(...),
    type: str = Query("output"),
    subfolder: str = Query(""),
):
    """
    Proxy ComfyUI /view via backend so remote clients (e.g. phones over zrok)
    do not need direct access to localhost:8188.
    """
    comfy_view_url = f"{settings.COMFYUI_API_URL}/view"
    params = {"filename": filename, "type": type, "subfolder": subfolder}
    try:
        async with httpx.AsyncClient() as client:
            upstream = await client.get(comfy_view_url, params=params, timeout=30.0)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to reach ComfyUI: {e}")

    if upstream.status_code >= 400:
        raise HTTPException(status_code=upstream.status_code, detail="ComfyUI view request failed")

    media_type = upstream.headers.get("content-type", "application/octet-stream")
    return Response(content=upstream.content, media_type=media_type)

@router.get("/gallery")
def get_gallery():
    # List all generated files in IMAGE_DIR
    files = []
    if os.path.exists(settings.IMAGE_DIR):
        for f in os.listdir(settings.IMAGE_DIR):
            if f.endswith((".png", ".jpg", ".jpeg", ".mp4", ".webp")):
                files.append(f)
    # Sort files by creation time or just alphabetically
    files.sort(reverse=True)
    return {"images": [f"/images/{file}" for file in files]}
