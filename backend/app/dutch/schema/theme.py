from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class ThemeBase(SQLModel):
    name: str = Field(index=True, unique=True, description="Canonical name of the theme/person.")

class Theme(ThemeBase, table=True):
    """Represents a learning theme or person used to generate cards."""
    __tablename__ = "dutch_theme"
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
