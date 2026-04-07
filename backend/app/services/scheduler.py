"""Scheduler service for processing recurring tasks."""
from datetime import datetime, timedelta
from typing import List, Tuple

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recurring_task import RecurringTask
from app.models.task import Task
from app.crud.task import create_task
from app.schemas.task import TaskCreate


async def process_recurring_tasks(db: AsyncSession) -> int:
    """
    Process all active recurring tasks and create tasks as needed.

    Returns:
        Number of tasks created
    """
    from sqlalchemy.orm import selectinload

    # Get all active recurring tasks
    result = await db.execute(
        select(RecurringTask)
        .where(RecurringTask.is_active == True)
        .options(
            selectinload(RecurringTask.assignee),
            selectinload(RecurringTask.building),
        )
    )
    recurring_tasks = result.scalars().all()

    now = datetime.utcnow()
    tasks_created = 0

    for recurring_task in recurring_tasks:
        if await should_create_task(db, recurring_task, now):
            await create_task_from_recurring(db, recurring_task)
            tasks_created += 1

    return tasks_created


async def should_create_task(
    db: AsyncSession,
    recurring_task: RecurringTask,
    now: datetime,
) -> bool:
    """
    Determine if a new task should be created from this recurring task.

    Checks:
    1. Is it the right day (based on frequency)?
    2. Has a task already been created for this period?
    """
    # Check if it's the right day based on frequency
    if recurring_task.frequency == "daily":
        # Daily tasks run every day
        pass
    elif recurring_task.frequency == "weekly":
        # Weekly tasks run on the specified day of week (0=Monday, 6=Sunday)
        if now.weekday() != recurring_task.day_of_week:
            return False
    elif recurring_task.frequency == "monthly":
        # Monthly tasks run on the specified day of month (1-31)
        day = recurring_task.day_of_month or 1
        if now.day != day:
            return False

    # Check if a task already exists for this period
    if await task_exists_for_period(db, recurring_task, now):
        return False

    return True


async def task_exists_for_period(
    db: AsyncSession,
    recurring_task: RecurringTask,
    now: datetime,
) -> bool:
    """
    Check if a task has already been created from this recurring task
    for the current period (day/week/month).
    """
    # Calculate the start of the current period
    if recurring_task.frequency == "daily":
        period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + timedelta(days=1)
    elif recurring_task.frequency == "weekly":
        # Start of the week (Monday)
        days_since_monday = now.weekday()
        period_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
        period_end = period_start + timedelta(days=7)
    elif recurring_task.frequency == "monthly":
        # Start of the month
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Next month
        if now.month == 12:
            period_end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            period_end = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        return False

    # Check if a task exists that was created from this recurring task in this period
    result = await db.execute(
        select(Task)
        .where(
            and_(
                Task.recurring_task_id == recurring_task.id,
                Task.created_at >= period_start,
                Task.created_at < period_end,
            )
        )
    )

    existing_task = result.scalar_one_or_none()
    return existing_task is not None


async def create_task_from_recurring(
    db: AsyncSession,
    recurring_task: RecurringTask,
) -> Task:
    """
    Create a new task from a recurring task template.
    """
    # Create task data
    task_data = TaskCreate(
        title=recurring_task.title,
        description=recurring_task.description,
        priority=recurring_task.priority,
        category=recurring_task.category,
        assignee_id=recurring_task.assignee_id,
        building_id=recurring_task.building_id,
    )

    # Create the task
    task = await create_task(db, task_data, recurring_task.created_by_id)

    # Update last_generated_at
    recurring_task.last_generated_at = datetime.utcnow()
    await db.commit()

    return task
