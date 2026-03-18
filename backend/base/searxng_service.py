from pathlib import Path
import httpx, os, re, requests
from datetime import datetime
from typing import List, Dict, Any
from backend.schema.search import SearchItem, SearchResult
from backend.config.config import settings
class SearxngService:
    def __init__(self):
        self.base_url = settings.SEARXNG_URL
        self.output_folder = Path(settings.IMAGE_DIR) / "images"
        os.makedirs(self.output_folder, exist_ok=True)
    
    async def searchApi(self, payload: dict, num_results: int = 5) -> SearchResult:
        if settings.SEARXNG_SECRET:
            payload["secret_key"] = settings.SEARXNG_SECRET
        search_result = SearchResult()
        try:
            async with httpx.AsyncClient() as client:
                headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
                # Use POST as configured in settings.yml
                response = await client.post(self.base_url, data=payload, timeout=30.0, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    for res in results[:num_results]:
                        search_result.search_items.append(SearchItem(title=res.get("title", ""),
                                                                     snippet=res.get("content", ""),
                                                                     url=res.get("url", ""),
                                                                     image_src =res.get("img_src", ""),
                                                                     score = res.get("score", 0.0)))
                    return search_result
                else:
                    print(f"[SearxngService] Exception:{response.status_code}, {response.content}")
                    return search_result
        except Exception as e:
            print(f"[SearxngService] Exception: {e}")
        return search_result

    async def search(self, query: str, payload:dict ,num_results: int = 5) -> SearchResult:
        """
        Searches SearXNG and returns a list of dictionaries with title, body, sources.
        """
        payload = {"q": query, "format": "json"}
        output = await self.searchApi(payload=payload, num_results=num_results)
        return output

    async def image_search(self, query:str, num_results: int = 10, safe_search: int = 1) -> SearchItem:
        payload = {"q": query, "categories": "images", "format": "json", "safesearch": safe_search}
        output = await self.searchApi(payload=payload, num_results=num_results)
        return output
    
    def download_image(self, news_item:SearchItem, folder:str = "images") -> SearchItem:
        ""
        img_url = news_item.image_src
        
        if news_item.title:
            clean_title = re.sub(r'[^\w\-_\. ]', '_',  news_item.title)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_title = f"image_{timestamp}"
        extension = img_url.split('.')[-1].split('?')[0].lower()
        if extension not in ['jpg', 'jpeg', 'png', 'webp']:
                    extension = "jpg"        
        filename = f"{clean_title[:30]}.{extension}"
        filepath = os.path.join(folder, filename)
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(img_url, headers=headers, timeout=10)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                f.write(response.content)
            news_item.image_download = True
            news_item.image_path = filepath
            print(f"Successfully saved: {filename}")
            
        except Exception as e:
            print(f"Error Downlaoding {e}")
        return SearchItem