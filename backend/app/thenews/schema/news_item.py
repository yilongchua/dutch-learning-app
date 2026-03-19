from sqlmodel import SQLModel, Field, Column, JSON
from sqlalchemy.types import TypeDecorator
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from backend.schema.search import SearchResult, SearchItem


class PydanticJSONList(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return [v.model_dump() if hasattr(v, 'model_dump') else (v.dict() if hasattr(v, 'dict') else v) for v in value]

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value

class ImageInfo(SQLModel):
    """Schema for tracking image generation within a NewsItem."""
    image_id: str = Field(default="", description="image id")
    image_prompt: str = Field(default="", description=" image prompts")
    img_path: str = Field(default="", description="image path")
    status: str = Field(default="", description="status")
    prompt_id: str = Field(default="", description="prompt id to trace back progress")

class NewsItemBase(SQLModel):
    theme: str = Field(default="",description="The overarching theme")
    question: str = Field(default="", description="The specific prompt/question")
    
    # Store lists of our sub-models in JSON columns
    search_items: List[SearchItem] = Field(default_factory=list, sa_column=Column(PydanticJSONList))
    article: str = Field(default="", description="english articke")    
    images_info: List[ImageInfo] = Field(default_factory=list, sa_column=Column(PydanticJSONList))
    # Prompt refinement: intertwined NL/EN and grammar
    output_captions: str = Field(default="", sa_column=Column(JSON))
    
    # Button content
    heart_button: str = Field(default="", description="Dutch with translated English for practice")
    comment_button: str = Field(default="", description="User input or placeholder")
    recommended_output: str = Field(default="")
    
    status: str = Field(default="pending", description="overall status: pending|processing|done|failed")

class NewsItem(NewsItemBase, table=True):
    """Unified single-table model for all news content and generation metadata."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )



class NewsItemCreate(NewsItemBase):
    pass

class NewsItemRead(NewsItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
