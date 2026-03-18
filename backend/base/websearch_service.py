import asyncio
from backend.base.searxng_service import SearxngService
from backend.base.page_extraction import PageExtractionService
from backend.schema.search import SearchItem, SearchResult
from backend.schema.response_format import ArticleExtracted
from backend.base.llm_base import LLMBase

class WebSearchService:
    """Higher-level pipeline to perform searches and extract clean content from results"""
    def __init__(self, max_results: int = 3):
        self.max_results = max_results
        self.searcher = SearxngService()
        self.extractor = PageExtractionService()
        self.llm = LLMBase()

    async def search_and_extract(self, query: str) -> SearchResult:
        """Run the full Search -> Fetch -> Clean pipeline in parallel."""
        # 1. Get search results
        search_results: SearchResult = await self.searcher.search(query, num_results=self.max_results)
        # 2. Extract content for each result in parallel
        async def _fill_content(item: SearchItem):
            if item.url:
                item.content = await self.extractor.extract_url(item.url) or ""
        if search_results.search_items:
            await asyncio.gather(*[_fill_content(res) for res in search_results.search_items])
        return search_results
    
    async def summarise(self, news_item) -> str:
        system_prompt = "You are a professional editor, specializing in condensing heavy news reports into punch."
        user_prompt = self.llm.render_prompt("summarize_article", news_item=news_item)
        result = await self.llm.generate_output(system_prompt, user_prompt, response_model=ArticleExtracted)
        return result.article


    async def search_updates(self, input_text:str) -> str:
        result = SearchResult()
        for query in ['latest news', 'future updates']:
            search_results: SearchResult = await self.search_and_extract(f"{input_text} {query}")
            output = await self.summarise(news_item=search_results)
            result.search_items.append(SearchItem(title=",".join([item.title for item in search_results.search_items]),
                                                  snippet=",".join([item.snippet for item in search_results.search_items]),
                                                  content=output))
        output = await self.summarise(news_item=result)
        return output
