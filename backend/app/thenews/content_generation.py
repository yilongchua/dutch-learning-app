import asyncio, os, sys, json
from sqlmodel import Session, select, distinct
# Add project root to sys.path
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from backend.app.thenews.core.database import engine, init_db
from backend.app.thenews.schema.news_item import NewsItem
from backend.app.thenews.schema.theme import Theme
from backend.app.thenews.schema.response_format import QuestionsExtracted
from backend.app.thenews.service.llm_service import LocalLLMService
from backend.base.websearch_service  import WebSearchService
from backend.base.comfy_base  import ComfyUIService
from backend.schema.search import SearchResult
from backend.config.config import DATA_DIR

class ContentGenerator:
    """
    Complete Content Generation Pipeline Orchestrator.
    Handles: Question Gen -> News Gen (Per Question) -> Image Gen -> Translation/Restructure -> Unified NewsItem.
    """
    def __init__(self, theme_file: str = Path(DATA_DIR) / "app"/ "thenews" /"theme.json"):
        self.theme_file = theme_file
        print(self.theme_file)
        init_db()
        self.web_search = WebSearchService()
        self.llm = LocalLLMService()
        self.image_gen = ComfyUIService()
        print(f"[*] Initialized ContentGenerator.")

    def _load_themes(self):
        with Session(engine) as session:
            theme = session.exec(select(distinct(Theme.name))).all()
            print(f'{theme=}')
        if theme:
            return theme
        else:
            if os.path.exists(self.theme_file):
                with open(self.theme_file, "r") as f:
                    data = json.load(f)
                    return data.get("theme", [])
        return []
    async def run_pipeline(self):
        themes = self._load_themes()
        print(f"[*] Loaded {len(themes)} themes for end-to-end testing.")
        for idx, theme_name in enumerate(themes):
            print(f"\n[!] Theme: {theme_name} ({idx+1}/{len(themes)})")
            success = await self.run_process(theme_name)
            if not success:
                print(f"[ERROR] Failed to process theme: {theme_name}")

    async def run_process(self, theme_name: str) -> bool:
        """Returns True if at least one NewsItem was generated."""
        with Session(engine) as session:
            # Find past questions from Unified NewsItem table
            past_questions = session.exec(select(NewsItem.question).where(NewsItem.theme == theme_name)).all()
            latest_news = await self.web_search.search_updates(input_text=theme_name)
            print(f"    [*] Generating questions (Local LLM)...")
            new_questions: QuestionsExtracted = await self.llm.generate_questions(theme_name, past_questions=past_questions, news=latest_news)
            processed_count = 0
            for q_idx, question in enumerate(new_questions.questions[:5]): 
                news_item = NewsItem(theme=theme_name, question=question)
                print(f"\n    [>] Question {q_idx+1}/{len(new_questions.questions)}: {question}")                
                try:
                    # Search
                    print(f"        [*] Searching SearXNG...")
                    search_result: SearchResult = await self.web_search.search_and_extract(query=question)
                    news_item.search_items = search_result.search_items
                    # Generate Article 
                    print(f"        [*] Generating article via Local LLM ...")
                    news_item = await self.llm.generate_article(news_item)
                    # Generate Caption 
                    print(f"        [*] Generating Caption via Local LLM ...")
                    news_item = await self.llm.translate_dutch_b1(news_item)
                    # Image Generation (ComfyUI)
                    print(f"        [*] Generating image Prompts via Local LLM ...")
                    news_item = await self.llm.generate_image_prompts(news_item)
                    # Image Generation (ComfyUI)
                    print(f"        [*] Submitting image prompts to ComfyUI...")
                    for image in news_item.images_info:
                        image.prompt_id = await self.image_gen.generate_image(image_prompt=image.image_prompt, file_prefix=image.image_id)
                        image.status = "processing"
                    # Mark item as actively processing so background sync picks it up.
                    news_item.status = "processing"
                    print(f"        [*] Prepare model for DB...")
                    session.add(news_item)
                    session.commit()
                    processed_count += 1
                except Exception as e:
                    print(f"        [!] Error processing question: {e}")
                    session.rollback()

            print(f"\n[+] Successfully completed session for theme: {theme_name}")
            return processed_count > 0

if __name__ == "__main__":
    generator = ContentGenerator()
    asyncio.run(generator.run_pipeline())
