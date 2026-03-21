import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path
import os
from sqlmodel import Session, select
from backend.app.thenews.core.database import engine
from backend.app.thenews.schema.news_item import NewsItem, ImageInfo
from backend.base.comfy_base import ComfyUIService
from datetime import datetime
from backend.config.config import settings

SYNC_INTERVAL_SECONDS = 30


def _extract_generated_image_path(outputs: Dict[str, Any]) -> Optional[str]:
    """Extract absolute file path from ComfyUI /history outputs."""
    if not isinstance(outputs, dict):
        return None

    for node_output in outputs.values():
        if not isinstance(node_output, dict):
            continue
        images = node_output.get("images", [])
        if not images:
            continue
        first = images[0]
        filename = first.get("filename")
        if not filename:
            continue
        subfolder = first.get("subfolder", "")
        if subfolder:
            return str(Path(settings.COMFYUI_DIR) / subfolder / filename)
        return str(Path(settings.COMFYUI_DIR) / filename)
    return None


def _normalize_to_desired_path(generated_path: str, desired_path: str) -> str:
    """
    Try to rename ComfyUI's suffixed output file to the desired fixed path.
    Returns the path that should be persisted.
    """
    if not generated_path:
        return desired_path

    if generated_path == desired_path:
        return generated_path

    try:
        src = Path(generated_path)
        dst = Path(desired_path)
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                os.replace(src, dst)
                return str(dst)
            return str(dst)
    except Exception as e:
        print(f"  [!] Path normalize failed ({generated_path} -> {desired_path}): {e}")

    return generated_path


async def background_image_sync():
    """
    Background task that periodically checks ComfyUI for finished images in NewsItems.
    """
    print("[Background Sync] Starting ComfyUI unified image sync loop...")
    image_gen = ComfyUIService()
    while True:
        try:
            with Session(engine) as session:
                # Include both pending and processing rows to recover from older records
                # where item.status was not updated, but image rows are still processing.
                statement = select(NewsItem).where(NewsItem.status.in_(["pending", "processing"]))
                items: List[NewsItem] = session.exec(statement).all()
                
                if items:
                    print(f"[Background Sync] Checking {len(items)} NewsItems for image updates...")
                    
                    for item in items:
                        any_updated = False
                        item_status_changed = False
                        all_images_done = True
                        
                        for idx, img_dict in enumerate(item.images_info):
                            # Validation: Use model to parse dictionary
                            # This performs the 'items = items(**items)' type logic
                            img = ImageInfo(**img_dict)
                            
                            if img.status == "processing" and img.prompt_id:
                                res = await image_gen.check_prompt_status(img.prompt_id)
                                if isinstance(res, dict) and res.get("status") in {"pending", "error"}:
                                    all_images_done = False 
                                else:
                                    generated_path = _extract_generated_image_path(res if isinstance(res, dict) else {})
                                    if generated_path:
                                        # Keep DB path exact and deterministic when possible.
                                        img.img_path = _normalize_to_desired_path(generated_path, img.img_path)
                                        img.status = "done"
                                        print(f"  [+] NewsItem {item.id} Image DONE: {img.img_path}")
                                        any_updated = True
                                    else:
                                        all_images_done = False
                                item.images_info[idx] = img.model_dump()
                            elif not img.prompt_id: # due to certain reasons it failed
                                img.status = 'failed'
                                item.images_info[idx] = img.model_dump()
                        
                        if all_images_done:
                            if item.status != "done":
                                item.status = "done"
                                item_status_changed = True
                                print(f"  [#] NewsItem {item.id} overall status set to DONE")
                        else:
                            if item.status != "processing":
                                item.status = "processing"
                                item_status_changed = True

                        if any_updated or item_status_changed:
                            session.add(item)
                    
                    session.commit()
                
        except Exception as e:
            print(f"[Background Sync] Error in sync loop: {e}")
            
        await asyncio.sleep(SYNC_INTERVAL_SECONDS)
