import asyncio, httpx
from pathlib import Path
from typing import Union
from typing import Type, TypeVar
from jinja2 import Environment, FileSystemLoader
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel
from backend.config.config import settings

T = TypeVar("T", bound=BaseModel)


class LLMBase:
    def __init__(self, 
                 model: str = settings.MODEL, # model: str = "unsloth/nvidia-nemotron-3-super-120b-a12b"
                 template_dir: str = Path(__file__).parent.parent / "prompts"):
        # template_dir = Path(__file__).parent.parent / "prompts"
        urls = [settings.LOCAL_LLM_URL]
        base_url: str = self._pick_first_responsive(urls)
        api_key: str = "lm-studio"
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.temperature: float = 0.7
        self.max_retries: int = 3

    @staticmethod
    def _pick_first_responsive(urls: list[str]) -> str:
        """Pick the first responsive LLM URL. Skips ping if only one URL exists."""
        if len(urls) == 1:
            return urls[0]

        for url in urls:
            try:
                import httpx
                # Use a valid OpenAI-compatible endpoint to check status
                test_url = f"{url.rstrip('/')}/models"
                httpx.get(test_url, timeout=2.0)
                return url
            except Exception as e:
                print(f"Warning: URL {url} did not respond: {e}")
                continue
        
        print("Warning: None of the configured LLM URLs responded. Using the first one as default.")
        return urls[0]
    def render_prompt(self, template_name: str, **kwargs) -> str:
        """Render Jinja prompt."""
        template = self.env.get_template(f"{template_name}.j2")
        return template.render(**kwargs)

    async def generate_output(self, system_prompt: str, user_prompt: str, response_model: Type[T] = None) -> Union[T, str, None]:
        for attempt in range(self.max_retries):
            try:
                # Prepare arguments
                kwargs = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                }
                if response_model:
                    # Use the parse helper for structured data
                    response = await self.client.beta.chat.completions.parse(**kwargs, response_format=response_model)
                    return response.choices[0].message.parsed
                else:
                    # Use standard create for plain text
                    response:ChatCompletion  = await self.client.chat.completions.create(**kwargs)
                    return response.choices[0].message.content

            except Exception as e:
                if attempt == self.max_retries - 1:
                    model_name = response_model.__name__ if response_model else "String"
                    raise RuntimeError(f"LLM failed to produce valid {model_name}") from e                
                await asyncio.sleep(1.5 * (attempt + 1))
        return None
    