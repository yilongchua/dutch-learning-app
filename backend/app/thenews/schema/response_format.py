from pydantic import BaseModel, Field
from typing import Optional, List

class QuestionsExtracted(BaseModel):
    questions : List[str] = Field(default_factory=list, description="list of questions")

class ArticleExtracted(BaseModel):
    article: str = Field(default="", description="aritcle")

class CaptionsExtracted(BaseModel):
    captions: List[tuple[str, str]] = Field(default_factory=list, description="captions")

class ImagePromptsExtracted(BaseModel):
    image_prompts: List[str] = Field(default_factory=list, description="image prompts")