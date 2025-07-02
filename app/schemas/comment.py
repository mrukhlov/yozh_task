"""Comment-related Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CommentBase(BaseModel):
    """Base comment schema."""

    content: str


class CommentCreate(CommentBase):
    """Schema for creating a comment."""

    pass


class CommentUpdate(BaseModel):
    """Schema for updating a comment."""

    content: str


class CommentInDB(CommentBase):
    """Schema for comment in database."""

    id: int
    task_id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Comment(CommentInDB):
    """Schema for comment response."""
