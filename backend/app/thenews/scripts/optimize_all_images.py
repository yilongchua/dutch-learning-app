"""
Optimise all existing images in the DB.
1. Read all NewsItems.
2. For each image in images_info:
   - If it exists on disk and is a PNG or on the Volume
   - Convert to WebP, resize, and save to local IMAGE_DIR
   - Update DB path.
"""
import sys, os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from sqlmodel import Session, select
from backend.app.thenews.core.database import engine
from backend.app.thenews.schema.news_item import NewsItem
from backend.app.thenews.service.image_sync_service import _optimize_image

def main():
    with Session(engine) as session:
        items = session.exec(select(NewsItem)).all()
        print(f"Found {len(items)} NewsItems to check.")
        
        updates = 0
        for item in items:
            changed = False
            updated_images = []
            for img in item.images_info:
                path = img.get("img_path")
                if path and Path(path).exists():
                    # Only optimize if it's not already a webp in the local IMAGE_DIR
                    if not (path.endswith(".webp") and "data/images" in path):
                        print(f"Optimizing item {item.id} image: {path}")
                        optimized = _optimize_image(path)
                        if optimized and optimized != path:
                            img["img_path"] = optimized
                            img["status"] = "done"
                            changed = True
                updated_images.append(img)
            
            if changed:
                item.images_info = updated_images
                session.add(item)
                updates += 1
        
        session.commit()
        print(f"Done. Optimized images for {updates} items.")

if __name__ == "__main__":
    main()
