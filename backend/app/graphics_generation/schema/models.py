from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

class GraphicsGenerationItemBase(SQLModel):
    original_prompt: str = Field(default="", description="User initial prompt")
    improved_prompt: str = Field(default="", description="LLM improved prompt used for generation")
    media_type: str = Field(default="image", description="image|video")
    media_url: str = Field(default="", description="Local path or URL of the generated media")

class GraphicsGenerationItem(GraphicsGenerationItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GraphicsGenerationItemRead(GraphicsGenerationItemBase):
    id: int
    created_at: datetime
