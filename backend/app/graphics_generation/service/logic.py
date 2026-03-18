import os
from pathlib import Path
from pydantic import BaseModel
from backend.base.llm_base import LLMBase
from backend.base.comfy_base import ComfyUIService

class ImprovedPromptResponse(BaseModel):
    improved_prompt: str

class GraphicsLLMService(LLMBase):
    def __init__(self):
        super().__init__(template_dir=Path(__file__).parent.parent / "prompts")

    async def enhance_prompt(self, user_prompt: str) -> str:
        system_prompt = "You are an expert prompt engineer for AI image and video generators. Enhance the user's short prompt into a highly detailed, descriptive visual prompt suitable for Stable Diffusion / ComfyUI. Provide ONLY the enhanced prompt string without any conversational text."
        result = await self.generate_output(system_prompt, user_prompt, response_model=ImprovedPromptResponse)
        if result:
            return result.improved_prompt
        return user_prompt # Fallback

class GraphicsGenerationService:
    def __init__(self):
        self.comfy = ComfyUIService()
        self.llm = GraphicsLLMService()

    async def enhance_prompt(self, user_prompt: str) -> str:
        return await self.llm.enhance_prompt(user_prompt)

    async def generate_media(self, prompt: str, media_type: str) -> str:
        file_prefix = "graphics_gen_"
        if media_type == "image":
            prompt_id = await self.comfy.generate_image(image_prompt=prompt, file_prefix=file_prefix)
        else:
            prompt_id = await self.comfy.generate_video(pos_image_prompt=prompt, neg_image_prompt="", file_prefix=file_prefix)
        return prompt_id or ""

    async def check_status(self, prompt_id: str) -> dict:
        return await self.comfy.check_prompt_status(prompt_id)
