"""CRUD operations for report messages."""
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.report_message import ReportMessage
from app.schemas.report_message import ReportMessageCreate


async def get_messages_by_report(
    db: AsyncSession,
    report_id: str,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[ReportMessage], int]:
    """Get messages for a report with pagination."""
    query = (
        select(ReportMessage)
        .where(ReportMessage.report_id == report_id)
        .order_by(ReportMessage.created_at.desc())
    )

    # Get total count
    count_query = select(func.count(ReportMessage.id)).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return list(items), total


async def create_message(
    db: AsyncSession,
    report_id: str,
    message_data: ReportMessageCreate,
    sender_id: str
) -> ReportMessage:
    """Create a new message in a report thread."""
    db_message = ReportMessage(
        report_id=report_id,
        sender_id=sender_id,
        content=message_data.content,
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message
