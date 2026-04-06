"""Task update API endpoints with RBAC."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.user import User
from app.models.task import Task
from app.models.task_update import TaskUpdate
from app.schemas.task_update import TaskUpdateCreate, TaskUpdateResponse, TaskUpdateListResponse
from app.crud import task as task_crud
from app.crud import task_update as task_update_crud
from app.dependencies.auth import get_current_user

router = APIRouter(tags=["task_updates"])


@router.get("/tasks/{task_id}/updates", response_model=TaskUpdateListResponse)
async def list_task_updates(
    task_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List updates for a specific task (manager or assigned employee)."""
    # Check task exists and user has permission
    task = await task_crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Check permissions
    if current_user.role not in ["manager", "super_admin"]:
        if task.assignee_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this task's updates")
    
    items, total = await task_update_crud.get_task_updates(db, task_id, skip=skip, limit=limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/tasks/{task_id}/updates", response_model=TaskUpdateResponse, status_code=status.HTTP_201_CREATED)
async def create_task_update(
    task_id: str,
    update_data: TaskUpdateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add an update to a task (manager or assigned employee)."""
    # Check task exists and user has permission
    task = await task_crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Check permissions - only manager or assigned employee can add updates
    if current_user.role not in ["manager", "super_admin"]:
        if task.assignee_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add updates to this task")
    
    # Create the update
    update = await task_update_crud.create_task_update(db, task_id, update_data, current_user.id)
    return update
