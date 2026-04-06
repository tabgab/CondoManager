"""Task API endpoints with RBAC."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, TaskVerification
from app.crud import task as task_crud
from app.dependencies.auth import get_current_user, require_manager

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assignee_id: Optional[str] = Query(None),
    building_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tasks. Manager sees all, employee sees assigned only."""
    if current_user.role not in ["manager", "super_admin"]:
        # Employee only sees their assigned tasks
        assignee_id = current_user.id
    
    items, total = await task_crud.get_tasks(
        db, skip=skip, limit=limit, status=status, priority=priority,
        assignee_id=assignee_id, building_id=building_id
    )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """Create a new task (manager only)."""
    task = await task_crud.create_task(db, task_data, current_user.id)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a task by ID (manager or assigned employee)."""
    task = await task_crud.get_task_with_relationships(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Check permissions
    if current_user.role not in ["manager", "super_admin"]:
        if task.assignee_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this task")
    
    return task


@router.patch("/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: str,
    assign_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """Assign or reassign a task (manager only)."""
    task = await task_crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    assignee_id = assign_data.get("assignee_id")
    task = await task_crud.assign_task(db, task, assignee_id)
    return task


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: str,
    status_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update task status. Employee can progress workflow, manager can do anything."""
    task = await task_crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    new_status = status_data.get("status")
    if not new_status:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Status required")
    
    # Check permissions
    if current_user.role not in ["manager", "super_admin"]:
        # Employee can only update their assigned tasks
        if task.assignee_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
        # Employee can only progress forward: pending -> in_progress -> completed
        allowed_transitions = {
            TaskStatus.PENDING: [TaskStatus.IN_PROGRESS],
            TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED],
        }
        current_status = TaskStatus(task.status)
        target_status = TaskStatus(new_status)
        
        if target_status not in allowed_transitions.get(current_status, []):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot change to this status")
    
    task = await task_crud.update_task_status(db, task, TaskStatus(new_status))
    return task


@router.patch("/{task_id}/verify", response_model=TaskResponse)
async def verify_task(
    task_id: str,
    verify_data: TaskVerification,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """Verify task completion or reject (manager only)."""
    task = await task_crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task must be completed before verification")
    
    task = await task_crud.verify_completion(
        db, task, current_user.id, 
        approved=verify_data.approved, 
        rejection_reason=verify_data.rejection_reason
    )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """Delete a task (manager only)."""
    task = await task_crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    await db.delete(task)
    await db.commit()
    return None
