from pydantic import BaseModel, Field
from typing import List, Optional

class SearchItem(BaseModel):
    title: str = Field(default="", description="Title of the search result")
    snippet: str = Field(default="", description="Snippet of the search result")
    content: str = Field(default="", description="Content of the search result")
    url: str = Field(default="", description="URL of the search result")
    score: float = Field(default=0.0, description="Score of the search result")
    image_src: str = Field(default="", description="Image source of the search result")
    image_download: bool = Field(default=False, description="downloaded image")
    image_path: str = Field(default="", description="image downlaod path")

class SearchResult(BaseModel):
    search_items: List[SearchItem] = Field(default_factory=list, description="List of search items")
    