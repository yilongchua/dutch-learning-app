import asyncio
from typing import List
from sqlmodel import Session, select
from backend.app.thenews.core.database import engine
from backend.app.thenews.schema.news_item import NewsItem, ImageInfo
from backend.base.comfy_base import ComfyUIService
from datetime import datetime


async def background_image_sync():
    """
    Background task that periodically checks ComfyUI for finished images in NewsItems.
    """
    print("[Background Sync] Starting ComfyUI unified image sync loop...")
    image_gen = ComfyUIService()
    while True:
        try:
            with Session(engine) as session:
                # Find all NewsItems that are still 'processing' (meaning images might be pending)
                statement = select(NewsItem).where(NewsItem.status == "processing")
                items: List[NewsItem] = session.exec(statement).all()
                
                if items:
                    print(f"[Background Sync] Checking {len(items)} NewsItems for image updates...")
                    
                    for item in items:
                        any_updated = False
                        all_images_done = True
                        
                        for img_dict in item.images_info:
                            # Validation: Use model to parse dictionary
                            # This performs the 'items = items(**items)' type logic
                            img = ImageInfo(**img_dict)
                            
                            if img.status == "processing" and img.prompt_id:
                                res = await image_gen.check_prompt_status(img.prompt_id)
                                if res:
                                    if res == 'failed':
                                        img.status = 'failed'
                                        print(f"  [!] NewsItem {item.id}, Image FAILED: {img.image_id}")
                                    else:
                                        img.status = "passed"
                                        print(f"  [+] NewsItem {item.id} Image DONE: {img.img_path}")
                                    any_updated = True
                                else:
                                    all_images_done = False 
                            elif not img.prompt_id: # due to certain reasons it failed
                                img.status = 'failed'
                            
                        if all_images_done:
                            item.status = "done"
                            print(f"  [#] NewsItem {item.id} overall status set to DONE")
                        if any_updated:
                            session.add(item)
                    
                    session.commit()
                
        except Exception as e:
            print(f"[Background Sync] Error in sync loop: {e}")
            
        await asyncio.sleep(300)

