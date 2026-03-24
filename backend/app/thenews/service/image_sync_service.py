import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path
import os
from sqlmodel import Session, select
from backend.app.thenews.core.database import engine
from backend.app.thenews.schema.news_item import NewsItem, ImageInfo
from backend.base.comfy_base import ComfyUIService
from backend.config.config import settings

SYNC_INTERVAL_SECONDS = 30
COUNTER = 0

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

    desired = Path(desired_path) if desired_path else None
    if desired and desired.exists():
        return str(desired)

    if generated_path == desired_path:
        return generated_path

    try:
        src = Path(generated_path)
        dst = desired if desired else Path(desired_path)
        if src.exists() and desired_path:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                os.replace(src, dst)
                return str(dst)
            return str(dst)
    except Exception as e:
        print(f"  [!] Path normalize failed ({generated_path} -> {desired_path}): {e}")

    return desired_path or generated_path


async def background_image_sync():
    """
    Background task that periodically checks ComfyUI for finished images in NewsItems.
    """
    print("[Background Sync] Starting ComfyUI unified image sync loop...")
    image_gen = ComfyUIService()
    while True:
        try:
            with Session(engine) as session:
                # Include all item statuses to self-heal nested images_info states.
                items: List[NewsItem] = session.exec(select(NewsItem).where(NewsItem.status != "done")).all()
                print(f"[Background Sync] {len(items)} NewsItems not done...")
                # if news_item == 0, then sleep
                # statement = select(NewsItem)
                # items: List[NewsItem] = session.exec(statement).all()
                if items:
                    SYNC_INTERVAL_SECONDS = 30 # reset sync interval
                    print(f"[Background Sync] Checking {len(items)} NewsItems for image updates...")
                    
                    for item in items:
                        any_updated = False
                        item_status_changed = False
                        image_statuses: List[str] = []
                        original_images = item.images_info or []
                        updated_images: List[Dict[str, Any]] = []
                        
                        for img_dict in original_images:
                            # Validation: Use model to parse dictionary
                            # This performs the 'items = items(**items)' type logic
                            img = ImageInfo(**img_dict)

                            # Fast self-heal: if target file already exists, image is done.
                            if img.img_path and Path(img.img_path).exists():
                                if img.status != "done":
                                    img.status = "done"
                                    any_updated = True
                                updated_images.append(img.model_dump())
                                image_statuses.append("done")
                                continue

                            # Preserve explicit done/failed statuses.
                            if img.status in {"done", "passed"}:
                                updated_images.append(img.model_dump())
                                image_statuses.append("done")
                                continue
                            if img.status == "failed":
                                updated_images.append(img.model_dump())
                                image_statuses.append("failed")
                                continue
                            
                            if img.prompt_id and img.status not in {"done", "passed", "failed"}:
                                res = await image_gen.check_prompt_status(img.prompt_id)
                                if isinstance(res, dict) and res.get("status") in {"pending", "error"}:
                                    image_statuses.append("processing")
                                else:
                                    generated_path = _extract_generated_image_path(res if isinstance(res, dict) else {})
                                    if generated_path:
                                        # Keep DB path exact and deterministic when possible.
                                        normalized_path = _normalize_to_desired_path(generated_path, img.img_path)
                                        if img.img_path != normalized_path:
                                            img.img_path = normalized_path
                                            any_updated = True
                                        if img.status != "done":
                                            img.status = "done"
                                            any_updated = True
                                        print(f"  [+] NewsItem {item.id} Image DONE: {img.img_path}")
                                        image_statuses.append("done")
                                    else:
                                        image_statuses.append("processing")
                                updated_images.append(img.model_dump())
                            elif not img.prompt_id: # due to certain reasons it failed
                                if img.status != "failed":
                                    img.status = "failed"
                                    any_updated = True
                                updated_images.append(img.model_dump())
                                image_statuses.append("failed")
                            else:
                                updated_images.append(img.model_dump())
                                image_statuses.append("processing")

                        if updated_images != original_images:
                            item.images_info = updated_images
                            any_updated = True
                        
                        # Recompute item status from nested image statuses each cycle.
                        if image_statuses and all(s == "done" for s in image_statuses):
                            if item.status != "done":
                                item.status = "done"
                                item_status_changed = True
                                print(f"  [#] NewsItem {item.id} overall status set to DONE")
                        elif image_statuses and all(s == "failed" for s in image_statuses):
                            if item.status != "failed":
                                item.status = "failed"
                                item_status_changed = True
                        else:
                            if item.status != "processing":
                                item.status = "processing"
                                item_status_changed = True

                        if any_updated or item_status_changed:
                            session.add(item)
                    
                    session.commit()
                
                else:
                    if COUNTER > 3:
                        SYNC_INTERVAL_SECONDS = 1800 # 30 minutes
                    else:
                        COUNTER += 1
                
        except Exception as e:
            print(f"[Background Sync] Error in sync loop: {e}")
            
        await asyncio.sleep(SYNC_INTERVAL_SECONDS)
