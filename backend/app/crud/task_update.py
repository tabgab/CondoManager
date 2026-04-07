"""CRUD operations for task updates."""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.models.task_update import TaskUpdate
from app.schemas.task_update import TaskUpdateCreate


async def get_task_updates(
    db: AsyncSession,
    task_id: str,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[TaskUpdate], int]:
    """Get updates for a specific task."""
    # Get total count
    count_query = select(func.count(TaskUpdate.id)).where(TaskUpdate.task_id == task_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results with author loaded
    query = (
        select(TaskUpdate)
        .where(TaskUpdate.task_id == task_id)
        .options(selectinload(TaskUpdate.author))
        .order_by(desc(TaskUpdate.created_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    return list(items), total


async def create_task_update(
    db: AsyncSession,
    task_id: str,
    update_data: TaskUpdateCreate,
    author_id: str
) -> TaskUpdate:
    """Create a new task update."""
    db_update = TaskUpdate(
        task_id=task_id,
        author_id=author_id,
        content=update_data.content,
        update_type=update_data.update_type,
    )
    db.add(db_update)
    await db.commit()
    await db.refresh(db_update)
    return db_update
