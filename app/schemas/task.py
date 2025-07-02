"""Task-related Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    """Base task schema."""

    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskCreate(TaskBase):
    """Schema for creating a task."""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


class TaskInDB(TaskBase):
    """Schema for task in database."""

    id: int
    status: TaskStatus
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Task(TaskInDB):
    """Schema for task response."""


class TaskAssignmentBase(BaseModel):
    """Base task assignment schema."""

    assigned_user_id: int


class TaskAssignmentCreate(TaskAssignmentBase):
    """Schema for creating a task assignment."""

    pass


class TaskAssignmentInDB(TaskAssignmentBase):
    """Schema for task assignment in database."""

    id: int
    task_id: int
    assigned_by_id: int
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskAssignment(TaskAssignmentInDB):
    """Schema for task assignment response."""
