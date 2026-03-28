import uuid
from backend.base.llm_base import LLMBase
from typing import Optional, List, Dict
from backend.app.dutch.schema.response_format import (NewThemeExtracted, NewExerciseExtracted, TranslatedEnglishExtracted,
                                                        NewListeningExtracted, EvaluatedExtracted, AnswerExtracted)
from backend.app.dutch.schema.schemas import ExerciseContent
from datetime import datetime
from backend.config.config import settings


class LocalLLMService(LLMBase):
    def __init__(self):
        import os
        prompt_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        super().__init__(model=settings.MODEL, template_dir=prompt_dir)
        self.system_prompt = "You are a DUTCH LANGUAGE TEACHER & TRANSLATOR (B1 LEVEL)."

    async def get_new_theme(self, current_themes: list[str]) -> NewThemeExtracted:
        """Generates a new theme using the LLM."""
        user_prompt = self.render_prompt("generate_theme", current_themes=current_themes)
        result = await self.generate_output(self.system_prompt, user_prompt, response_model=NewThemeExtracted)
        return result
        
    async def generate_exercise(self, theme:str) -> NewExerciseExtracted:
        """High-level method to generate a specific exercise."""
        user_prompt = self.render_prompt("generate_exercise", theme=theme)
        result = await self.generate_output(self.system_prompt, user_prompt, response_model=NewExerciseExtracted)
        return result
    
    async def translate_answer(self, text_to_translate:str) -> TranslatedEnglishExtracted:
        """High-level method to generate a answer."""
        kwargs = {"text_to_translate": text_to_translate}
        user_prompt = self.render_prompt("translate_answer", **kwargs)
        result = await self.generate_output(self.system_prompt, user_prompt, response_model=TranslatedEnglishExtracted)
        return result
        
    async def generate_answer(self, question: str, keywords: list[str]) -> AnswerExtracted:
        """High-level method to generate a answer."""
        kwargs = {"question": question, "keywords": keywords}
        user_prompt = self.render_prompt("generate_answer", **kwargs)
        result = await self.generate_output(self.system_prompt, user_prompt, response_model=AnswerExtracted)
        return result
        
    async def generate_listening(self, theme: str) -> NewListeningExtracted:
        """High-level method to generate a answer."""
        user_prompt = self.render_prompt("generate_listening", theme=theme)
        result = await self.generate_output(self.system_prompt, user_prompt, response_model=NewListeningExtracted)
        return result
        
    async def evaluate(self, question: str, user_answer: str) -> EvaluatedExtracted:
        kwargs = {"question": question, "answer": user_answer}
        user_prompt = self.render_prompt("evaluate_answer", **kwargs)
        result = await self.generate_output(self.system_prompt, user_prompt, response_model=EvaluatedExtracted)
        return result