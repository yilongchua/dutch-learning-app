from backend.base.llm_base import LLMBase
from backend.schema.response_format import ImagePromptsExtracted

class LLMService(LLMBase):
    def __init__(self):
        super().__init__(model="openai/gpt-oss-120b")

    async def generate_image_prompts(self, article: str, num_image: int = 1) -> list[str]:
        """Generates image prompts."""
        system_prompt = "You are a visual narrative designer. Create a chronological series of image prompts that illustrate the key events/details/situations"
        user_prompt = self.render_prompt("generate_image_prompts", article=article, num_image=num_image)
        result = await self.generate_output(system_prompt, user_prompt, response_model=ImagePromptsExtracted)
        return result.image_prompts
