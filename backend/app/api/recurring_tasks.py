"""API endpoints for recurring tasks."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.dependencies.auth import require_manager, get_current_user
from app.models.user import User
from app.schemas.recurring_task import (
    RecurringTaskCreate,
    RecurringTaskUpdate,
    RecurringTaskResponse,
    RecurringTaskListResponse,
    RecurringTaskToggle,
)
from app.crud.recurring_task import (
    get_recurring_tasks,
    get_recurring_task,
    get_recurring_task_with_relationships,
    create_recurring_task,
    update_recurring_task,
    delete_recurring_task,
    toggle_active,
)

router = APIRouter(prefix="/recurring-tasks", tags=["recurring-tasks"])


@router.get("", response_model=RecurringTaskListResponse)
async def list_recurring_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """List all recurring task templates (manager only)."""
    items, total = await get_recurring_tasks(db, skip=skip, limit=limit, is_active=is_active)
    
    # Build response with assignee and building names
    response_items = []
    for item in items:
        item_dict = RecurringTaskResponse.model_validate(item).model_dump()
        if item.assignee:
            item_dict["assignee_name"] = f"{item.assignee.first_name} {item.assignee.last_name}"
        if item.building:
            item_dict["building_name"] = item.building.name
        response_items.append(RecurringTaskResponse(**item_dict))
    
    return RecurringTaskListResponse(
        items=response_items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=RecurringTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring_task_endpoint(
    task_data: RecurringTaskCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """Create a new recurring task template (manager only)."""
    task = await create_recurring_task(db, task_data, current_user.id)
    
    # Load relationships for response
    task_with_relations = await get_recurring_task_with_relations(db, task.id)
    
    item_dict = RecurringTaskResponse.model_validate(task_with_relations).model_dump()
    if task_with_relations.assignee:
        item_dict["assignee_name"] = f"{task_with_relations.assignee.first_name} {task_with_relations.assignee.last_name}"
    if task_with_relations.building:
        item_dict["building_name"] = task_with_relations.building.name
    
    return RecurringTaskResponse(**item_dict)


@router.get("/{task_id}", response_model=RecurringTaskResponse)
async def get_recurring_task_endpoint(
    task_id: UUID,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """Get a recurring task template by ID (manager only)."""
    task = await get_recurring_task_with_relations(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring task not found",
        )
    
    item_dict = RecurringTaskResponse.model_validate(task).model_dump()
    if task.assignee:
        item_dict["assignee_name"] = f"{task.assignee.first_name} {task.assignee.last_name}"
    if task.building:
        item_dict["building_name"] = task.building.name
    
    return RecurringTaskResponse(**item_dict)


@router.patch("/{task_id}", response_model=RecurringTaskResponse)
async def update_recurring_task_endpoint(
    task_id: UUID,
    task_update: RecurringTaskUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """Update a recurring task template (manager only)."""
    task = await get_recurring_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring task not found",
        )
    
    updated_task = await update_recurring_task(db, task, task_update)
    
    # Load relationships for response
    task_with_relations = await get_recurring_task_with_relations(db, updated_task.id)
    
    item_dict = RecurringTaskResponse.model_validate(task_with_relations).model_dump()
    if task_with_relations.assignee:
        item_dict["assignee_name"] = f"{task_with_relations.assignee.first_name} {task_with_relations.assignee.last_name}"
    if task_with_relations.building:
        item_dict["building_name"] = task_with_relations.building.name
    
    return RecurringTaskResponse(**item_dict)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_task_endpoint(
    task_id: UUID,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """Delete a recurring task template (manager only)."""
    task = await get_recurring_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring task not found",
        )
    
    await delete_recurring_task(db, task)
    return None


@router.patch("/{task_id}/toggle", response_model=RecurringTaskResponse)
async def toggle_recurring_task_endpoint(
    task_id: UUID,
    toggle_data: RecurringTaskToggle,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """Toggle active status of a recurring task (manager only)."""
    task = await get_recurring_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring task not found",
        )
    
    updated_task = await toggle_active(db, task, toggle_data.is_active)
    
    # Load relationships for response
    task_with_relations = await get_recurring_task_with_relations(db, updated_task.id)
    
    item_dict = RecurringTaskResponse.model_validate(task_with_relations).model_dump()
    if task_with_relations.assignee:
        item_dict["assignee_name"] = f"{task_with_relations.assignee.first_name} {task_with_relations.assignee.last_name}"
    if task_with_relations.building:
        item_dict["building_name"] = task_with_relations.building.name
    
    return RecurringTaskResponse(**item_dict)


async def get_recurring_task_with_relations(db: AsyncSession, task_id: UUID):
    """Helper to load recurring task with relationships."""
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    from app.models.recurring_task import RecurringTask
    from app.models.user import User
    from app.models.building import Building
    
    result = await db.execute(
        select(RecurringTask)
        .where(RecurringTask.id == task_id)
        .options(
            selectinload(RecurringTask.assignee),
            selectinload(RecurringTask.building),
            selectinload(RecurringTask.created_by),
        )
    )
    return result.scalar_one_or_none()
