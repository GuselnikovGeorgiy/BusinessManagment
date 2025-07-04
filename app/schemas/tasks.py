from typing import List, Optional
from pydantic import BaseModel, field_validator, ConfigDict

from app.models.tasks import TaskStatus


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    responsible_id: int
    observer_ids: List[int]
    executor_ids: List[int]
    deadline: Optional[str] = None
    estimated_time: Optional[float] = None


class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    responsible_id: int
    observer_ids: List[int]
    executor_ids: List[int]
    deadline: Optional[str]
    estimated_time: Optional[float]
    status: Optional[TaskStatus] = TaskStatus.NEW

    @field_validator("status", mode="before")
    def normalize_status(cls, value):
        if isinstance(value, str):
            value = value.title()
        return TaskStatus(value)


class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[TaskStatus]
    deadline: Optional[str]
    estimated_time: Optional[float]


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    responsible_id: int
    observer_ids: List[int]
    executor_ids: List[int]
    deadline: Optional[str] = None
    estimated_time: Optional[float] = None
    status: TaskStatus

    model_config = ConfigDict(from_attributes=True)
