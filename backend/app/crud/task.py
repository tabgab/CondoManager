"""CRUD operations for tasks."""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


async def get_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[str] = None,
    created_by_id: Optional[str] = None,
    building_id: Optional[str] = None,
    apartment_id: Optional[str] = None,
    report_id: Optional[str] = None,
) -> Tuple[List[Task], int]:
    """Get tasks with optional filtering."""
    query = select(Task)
    
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    if assignee_id:
        query = query.where(Task.assignee_id == assignee_id)
    if created_by_id:
        query = query.where(Task.created_by_id == created_by_id)
    if building_id:
        query = query.where(Task.building_id == building_id)
    if apartment_id:
        query = query.where(Task.apartment_id == apartment_id)
    if report_id:
        query = query.where(Task.report_id == report_id)
    
    # Get total count
    count_query = select(func.count(Task.id)).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results with relationships loaded
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return list(items), total


async def get_task(db: AsyncSession, task_id: str) -> Optional[Task]:
    """Get a single task by ID."""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    return result.scalar_one_or_none()


async def get_task_with_relationships(db: AsyncSession, task_id: str) -> Optional[Task]:
    """Get task with assignee and other relationships loaded."""
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id)
        .options(selectinload(Task.assignee), selectinload(Task.created_by))
    )
    return result.scalar_one_or_none()


async def create_task(
    db: AsyncSession,
    task_data: TaskCreate,
    created_by_id: str
) -> Task:
    """Create a new task."""
    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        created_by_id=created_by_id,
        assignee_id=task_data.assignee_id,
        building_id=task_data.building_id,
        apartment_id=task_data.apartment_id,
        report_id=task_data.report_id,
        estimated_hours=task_data.estimated_hours,
        due_date=task_data.due_date,
        status=TaskStatus.PENDING,
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def update_task(
    db: AsyncSession,
    task: Task,
    update_data: TaskUpdate
) -> Task:
    """Update a task."""
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    return task


async def assign_task(
    db: AsyncSession,
    task: Task,
    assignee_id: Optional[str]
) -> Task:
    """Assign or reassign a task."""
    task.assignee_id = assignee_id
    await db.commit()
    await db.refresh(task)
    return task


async def update_task_status(
    db: AsyncSession,
    task: Task,
    status: TaskStatus
) -> Task:
    """Update task status."""
    task.status = status
    
    # Auto-set completed_at if status is COMPLETED
    if status == TaskStatus.COMPLETED:
        from datetime import datetime
        task.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(task)
    return task


async def verify_completion(
    db: AsyncSession,
    task: Task,
    verified_by_id: str,
    approved: bool = True,
    rejection_reason: Optional[str] = None
) -> Task:
    """Manager verifies task completion."""
    task.verified_by_id = verified_by_id
    
    if not approved:
        task.rejection_reason = rejection_reason
        task.status = TaskStatus.ON_HOLD
    
    await db.commit()
    await db.refresh(task)
    return task
