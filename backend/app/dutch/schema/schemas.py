from sqlalchemy.types import TypeDecorator
from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

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

class ExerciseContentBase(SQLModel):
    exercise_type: str = Field(default="", description="writing|speaking|listening")
    theme: str = Field(default="")
    question: str = Field(default="")
    keywords: List[str] = Field(default_factory=list, description="list of words", sa_column=Column(PydanticJSONList))
    audio_text: str = Field(default="", description="audio_text")
    audio_translation: str = Field(default="", description="audio translation text")
    audio_url: str = Field(default="", description="audio url for speaking exercise")
    
    user_answer: str = Field(default="", description="User Answer")
    
    score: int = Field(default=0, description="score of user answer")
    score_breakdown: str = Field(default="", description="score_breakdown of user answer")
    improved_text: str = Field(default="", description="improved text for user answer")
    feedback: str = Field(default="", description="feedback for user answer")
    
    options: List[str] = Field(default_factory=list, description="multiple choices options", sa_column=Column(PydanticJSONList))
    correct_answer: str = Field(default="", description="correct answer")
    correct_answer_translation: str = Field(default="", description="correct answer translation")
    status: str = Field(default="pending", description="pending|served|completed|deleted")
    date_completed: Optional[str] = Field(default=None, description="Format: YYYY-MM-DD")


class ExerciseContent(ExerciseContentBase, table=True):
    """Unified single-table model for both Dutch exercise content and completion progress."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ExerciseContentReceive(ExerciseContentBase):
    """Handle incoming frontend data with aliases"""
    id: Optional[int] = None
    text: Optional[str] = None
    prompt: Optional[str] = None
    date: Optional[str] = None

class ExerciseContentRead(ExerciseContentBase):
    id: int
    created_at: datetime
    updated_at: datetime
