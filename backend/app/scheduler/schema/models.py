from sqlmodel import SQLModel, Field
from typing import Optional

class CronJobBase(SQLModel):
    task_type: str = Field(index=True, description="Task Type, e.g. dutch, thenews, image, video")
    schedule_time: str = Field(description="12-hour format time, e.g., '02:00 PM'")
    input_number: int = Field(default=1, description="Input associated with this task")

class CronJob(CronJobBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class CronJobRead(CronJobBase):
    id: int
