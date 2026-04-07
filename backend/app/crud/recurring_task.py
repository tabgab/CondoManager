"""CRUD operations for RecurringTask model."""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recurring_task import RecurringTask
from app.schemas.recurring_task import RecurringTaskCreate, RecurringTaskUpdate


async def get_recurring_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
) -> tuple[List[RecurringTask], int]:
    """Get list of recurring tasks with optional filtering."""
    from sqlalchemy.orm import selectinload

    query = select(RecurringTask).options(
        selectinload(RecurringTask.assignee),
        selectinload(RecurringTask.building),
    )

    if is_active is not None:
        query = query.where(RecurringTask.is_active == is_active)

    # Execute count query
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Execute main query with pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return list(items), total


async def get_recurring_task(
    db: AsyncSession,
    recurring_task_id: str,
) -> Optional[RecurringTask]:
    """Get a recurring task by ID."""
    result = await db.execute(
        select(RecurringTask).where(RecurringTask.id == str(recurring_task_id))
    )
    return result.scalar_one_or_none()


async def get_recurring_task_with_relationships(
    db: AsyncSession,
    recurring_task_id: str,
) -> Optional[RecurringTask]:
    """Get recurring task with assignee and building loaded."""
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(RecurringTask)
        .where(RecurringTask.id == str(recurring_task_id))
        .options(
            selectinload(RecurringTask.assignee),
            selectinload(RecurringTask.building),
            selectinload(RecurringTask.created_by),
        )
    )
    return result.scalar_one_or_none()


async def create_recurring_task(
    db: AsyncSession,
    task_data: RecurringTaskCreate,
    created_by_id: str,
) -> RecurringTask:
    """Create a new recurring task template."""
    db_task = RecurringTask(
        title=task_data.title,
        description=task_data.description,
        category=task_data.category,
        priority=task_data.priority,
        frequency=task_data.frequency,
        day_of_week=task_data.day_of_week,
        day_of_month=task_data.day_of_month,
        is_active=task_data.is_active if task_data.is_active is not None else True,
        assignee_id=task_data.assignee_id,
        building_id=task_data.building_id,
        created_by_id=str(created_by_id),
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def update_recurring_task(
    db: AsyncSession,
    recurring_task: RecurringTask,
    task_update: RecurringTaskUpdate,
) -> RecurringTask:
    """Update a recurring task template."""
    update_data = task_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(recurring_task, field, value)

    await db.commit()
    await db.refresh(recurring_task)
    return recurring_task


async def delete_recurring_task(
    db: AsyncSession,
    recurring_task: RecurringTask,
) -> None:
    """Delete a recurring task template."""
    await db.delete(recurring_task)
    await db.commit()


async def toggle_active(
    db: AsyncSession,
    recurring_task: RecurringTask,
    is_active: bool,
) -> RecurringTask:
    """Toggle the active status of a recurring task."""
    recurring_task.is_active = is_active
    await db.commit()
    await db.refresh(recurring_task)
    return recurring_task
