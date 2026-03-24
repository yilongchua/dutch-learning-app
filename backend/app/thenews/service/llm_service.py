import uuid
from backend.base.llm_base import LLMBase
from typing import Optional, List, Dict
from backend.app.thenews.schema.response_format import (
    QuestionsExtracted, 
    ArticleExtracted, 
    ImagePromptsExtracted, 
    StructuredDutchExtracted, 
    TranslatedEnglishExtracted
)
from backend.app.thenews.schema.news_item import NewsItemBase, NewsItem, ImageInfo
from datetime import datetime
from backend.config.config import settings
class LocalLLMService(LLMBase):
    def __init__(self):
        import os
        prompt_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        super().__init__(model=settings.MODEL, template_dir=prompt_dir)
    async def generate_questions(self, theme:str, **kwargs) -> QuestionsExtracted:
        """Generates unique sub-questions based on a theme and avoiding historical question."""
        result = QuestionsExtracted()
        system_prompt = f"You are curious young asian female mid 30s interested in {theme}, asking questions about the latest news"
        user_prompt = self.render_prompt("generate_questions", year = datetime.year, **kwargs)    
        result = await self.generate_output(system_prompt=system_prompt, user_prompt=user_prompt, response_model=QuestionsExtracted)
        return result
    
    async def generate_article(self, news_item: NewsItem, **kwargs) -> NewsItem:
        """Generates a structured article dict based on search context."""
        result = ArticleExtracted()
        system_prompt = "You are a helpful news assistant. Write objective news articles based on the given sources. Output strictly structured text matching the template."
        user_prompt = self.render_prompt("generate_article", news_item=news_item,  **kwargs)
        result = await self.generate_output(system_prompt, user_prompt, response_model=ArticleExtracted)
        news_item.article = result.article
        return news_item
    
    async def translate_dutch_b1(self, news_item: NewsItem) -> NewsItem:
        """Translates a single text block to Dutch B1."""
        system_prompt = "You are a professional Dutch translator (CEFR B1). Preparing Specific Content for CVanT B1 Learner translation, Output the information in JSON format"
        user_prompt = self.render_prompt("translate_b1", news_item=news_item)
        result = await self.generate_output(system_prompt, user_prompt, response_model=StructuredDutchExtracted)
        translated_english = await self.translate_article(result.structured_dutch)
        news_item.output_captions = result.structured_dutch + "\n" + translated_english
        return news_item
    
    async def translate_article(self, dutch_text: str) -> str:
        """Translates a single text block to English."""
        system_prompt = "You are a professional English translator. Preparing Specific Content for CVanT B1 Learner translation, Output the information in JSON format"
        user_prompt = self.render_prompt("translate_article", text_to_translate=dutch_text)
        result = await self.generate_output(system_prompt, user_prompt, response_model=TranslatedEnglishExtracted)
        return result.translated_english

    async def generate_image_prompts(self, news_item:NewsItem) -> NewsItem:
        """Generates image prompts."""
        system_prompt = "You are a visual narrative designer. Create a chronological series of image prompts that illustrate the key events/details/situations"
        user_prompt = self.render_prompt("generate_image_prompts", news_item=news_item)
        result = await self.generate_output(system_prompt, user_prompt, response_model=ImagePromptsExtracted)
        for info in result.image_prompts:
            id_name = f"thenews/{news_item.theme}_{str(uuid.uuid4())}"
            news_item.images_info.append(ImageInfo(image_id=id_name, img_path=str(settings.COMFYUI_DIR)+f"/{id_name}.png", image_prompt=info ))
        return news_item