"""Task API endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database import get_db
from app.models.task import Task as TaskModel
from app.models.task import TaskAssignment as TaskAssignmentModel
from app.models.task import TaskStatus
from app.models.user import User as UserModel
from app.schemas.task import (
    Task,
    TaskAssignment,
    TaskAssignmentCreate,
    TaskCreate,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=Task, status_code=201)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = TaskModel(
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        creator_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=List[Task])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    status: Optional[TaskStatus] = Query(None),
    assigned: Optional[bool] = Query(None),
):
    query = db.query(TaskModel)
    if status:
        query = query.filter(TaskModel.status == status)
    if assigned is not None:
        if assigned:
            query = query.join(TaskAssignmentModel).filter(
                TaskAssignmentModel.assigned_user_id == current_user.id
            )
        else:
            query = query.filter(TaskModel.creator_id == current_user.id)
    return query.all()


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    for field, value in task_in.dict(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db.delete(task)
    db.commit()
    return None


@router.post("/{task_id}/assign", response_model=TaskAssignment)
def assign_task(
    task_id: int,
    assignment_in: TaskAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    # Prevent duplicate assignment
    existing = (
        db.query(TaskAssignmentModel)
        .filter(
            TaskAssignmentModel.task_id == task_id,
            TaskAssignmentModel.assigned_user_id == assignment_in.assigned_user_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="User already assigned to this task"
        )
    assignment = TaskAssignmentModel(
        task_id=task_id,
        assigned_user_id=assignment_in.assigned_user_id,
        assigned_by_id=current_user.id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/{task_id}/assignments", response_model=List[TaskAssignment])
def list_assignments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Only creator or assigned users can view assignments
    is_assigned = (
        db.query(TaskAssignmentModel)
        .filter(
            TaskAssignmentModel.task_id == task_id,
            TaskAssignmentModel.assigned_user_id == current_user.id,
        )
        .first()
    )
    if task.creator_id != current_user.id and not is_assigned:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    assignments = (
        db.query(TaskAssignmentModel)
        .filter(TaskAssignmentModel.task_id == task_id)
        .all()
    )
    return assignments


@router.post("/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Only creator or assigned user can complete
    is_assigned = (
        db.query(TaskAssignmentModel)
        .filter(
            TaskAssignmentModel.task_id == task_id,
            TaskAssignmentModel.assigned_user_id == current_user.id,
        )
        .first()
    )
    if task.creator_id != current_user.id and not is_assigned:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if task.status == TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Task is already completed")
    task.status = TaskStatus.COMPLETED  # type: ignore[assignment]
    task.completed_at = datetime.now()  # type: ignore[assignment]
    db.commit()
    db.refresh(task)
    return task
