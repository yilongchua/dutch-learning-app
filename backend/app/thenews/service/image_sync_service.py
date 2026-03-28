import asyncio, re
from typing import List, Optional, Dict, Any
from pathlib import Path
import os
from PIL import Image
from sqlmodel import Session, select
from backend.app.thenews.core.database import engine
from backend.app.thenews.schema.news_item import NewsItem, ImageInfo
from backend.base.comfy_base import ComfyUIService
from backend.config.config import settings

SYNC_INTERVAL_SECONDS = 30
COUNTER = 0

def _optimize_image(src_path: str) -> Optional[str]:
    """
    Takes an image from ComfyUI output (often large PNG), converts to WebP,
    resizes to max 1024px width, and saves to local fast storage.
    """
    try:
        src = Path(src_path)
        if not src.exists():
            return None

        # 1. Define destination in local IMAGE_DIR
        dest_dir = Path(settings.IMAGE_DIR) / "thenews"
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Use same stem but switch extension to .webp
        dest_path = dest_dir / (src.stem + ".webp")
        
        # 3. If already optimized, just return path
        if dest_path.exists():
            return str(dest_path)

        # 4. Open and process
        with Image.open(src) as img:
            # Resize if too large (keep aspect ratio)
            max_width = 1024
            if img.width > max_width:
                w_percent = (max_width / float(img.width))
                h_size = int((float(img.height) * float(w_percent)))
                img = img.resize((max_width, h_size), Image.Resampling.LANCZOS)
            
            # Save as WebP with quality 80 (good balanced trade-off)
            img.save(dest_path, "WEBP", quality=80)
            
        print(f"  [Optimizer] Converted & optimized: {src.name} -> {dest_path.name}")
        return str(dest_path)
    except Exception as e:
        print(f"  [!] Optimization failed for {src_path}: {e}")
        return src_path # Return original if optimization fails

def _find_comfy_suffixed_file(base_path: str) -> Optional[str]:
    """
    ComfyUI's SaveImage node appends _NNNNN_ to the filename_prefix, e.g.:
      F1_uuid -> F1_uuid_00001_.png
    If `base_path` doesn't exist, scan its parent directory for a file whose
    stem matches `{stem}_NNNNN_` pattern and return the first match.
    """
    p = Path(base_path)
    if p.exists():
        return str(p)
    parent = p.parent
    if not parent.exists():
        print("failed to find parent")
        return None
    pattern = re.compile(re.escape(p.stem) + r"_\d+_$")
    for candidate in sorted(parent.glob(f"{p.stem}_*{p.suffix}")):
        if pattern.match(candidate.stem):
            return str(candidate)
    print("No Match")
    return None


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
    COUNTER = 0
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
                    COUNTER = 0
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

                            # Fast self-heal: if target file exists (or a ComfyUI
                            # suffixed variant like _00001_ is found), mark done.
                            resolved = _find_comfy_suffixed_file(img.img_path) if img.img_path else None
                            if resolved:
                                # Always try to optimize if it's currently on the Volume or a PNG
                                if str(settings.COMFYUI_DIR) in resolved or resolved.endswith(".png"):
                                    optimized = _optimize_image(resolved)
                                    if optimized:
                                        resolved = optimized

                                if img.img_path != resolved:
                                    img.img_path = resolved
                                    any_updated = True
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
                                        # Optimization step
                                        optimized = _optimize_image(generated_path)
                                        final_path = optimized if optimized else generated_path

                                        # Keep DB path exact and deterministic when possible.
                                        normalized_path = _normalize_to_desired_path(final_path, img.img_path)
                                        if img.img_path != normalized_path:
                                            img.img_path = normalized_path
                                            any_updated = True
                                        if img.status != "done":
                                            img.status = "done"
                                            any_updated = True
                                        print(f"  [+] NewsItem {item.id} Image DONE (Optimized): {img.img_path}")
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
                        print(" set sync to 30 mins")
                    else:
                        COUNTER += 1
                        print(f"{COUNTER =}")
                
        except Exception as e:
            print(f"[Background Sync] Error in sync loop: {e}")
            
        await asyncio.sleep(SYNC_INTERVAL_SECONDS)
