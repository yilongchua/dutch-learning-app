import uuid
from backend.base.llm_base import LLMBase
from typing import Optional, List, Dict
from backend.app.dutch.schema.response_format import NewThemeExtracted, NewExerciseExtracted, NewListeningExtracted, EvaluatedExtracted
from backend.app.dutch.schema.schemas import ExerciseContent
from datetime import datetime
from backend.config.config import settings


class LocalLLMService(LLMBase):
    def __init__(self):
        import os
        prompt_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        super().__init__(model=settings.MODEL, template_dir=prompt_dir)
        self.system_prompt = "You are a DUTCH LANGUAGE TEACHER & TRANSLATOR (B1 LEVEL)."

    async def get_new_theme(self, current_themes: list[str]) -> str:
        """Generates a new theme using the LLM."""
        user_prompt = self.render_prompt("generate_theme", current_themes=current_themes)
        result = await self.generate_output(self.system_prompt, user_prompt, response_model=NewThemeExtracted)
        return result
        
    async def generate_exercise(self, exercise: ExerciseContent) -> ExerciseContent:
        """High-level method to generate a specific exercise."""
        user_prompt = self.render_prompt("generate_exercise", theme=exercise.theme)
        result = await self.generate_output(self.system_prompt, user_prompt, response_model=NewExerciseExtracted)
        exercise.question = result.question
        exercise.keywords = result.keywords
        return exercise
    
    async def generate_answer(self, exercise: ExerciseContent) -> ExerciseContent:
        """High-level method to generate a answer."""
        user_prompt = self.render_prompt("generate_exercise", theme=exercise.theme)
        result = await self.generate_output(self.system_prompt, user_prompt)
        exercise.correct_answer = result
        return exercise
        
    async def generate_listening(self, exercise: ExerciseContent) -> ExerciseContent:
        """High-level method to generate a answer."""
        user_prompt = self.render_prompt("generate_listening", theme=exercise.theme)
        result = await self.generate_output(self.system_prompt, user_prompt, response_model=NewListeningExtracted)
        exercise.audio_text = result.text
        exercise.question = result.question
        exercise.options = result.options
        exercise.correct_answer = result.correct_answer
        exercise.audio_translation = result.english_translation
        return exercise

    async def evaluate(self, exercise: ExerciseContent) -> ExerciseContent:
        kwargs = {"question": exercise.question, "answer": exercise.user_answer}
        user_prompt = self.render_prompt("evaluate_answer", **kwargs)
        result = await self.generate_output(self.system_prompt, user_prompt, response_model=EvaluatedExtracted)
        print(result)
        exercise.score = result.score
        exercise.score_breakdown = result.score_breakdown
        exercise.improved_text = result.improved_text
        exercise.feedback = result.feedback
        return exercise
