from pydantic import BaseModel, Field
from typing import Optional, List
class ArticleExtracted(BaseModel):
    article: str = Field(default="", description="aritcle")

class ImagePromptsExtracted(BaseModel):
    image_prompts: List[str] = Field(default_factory=list, description="image prompts")