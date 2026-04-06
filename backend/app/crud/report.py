"""CRUD operations for reports."""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.report import Report, ReportStatus
from app.schemas.report import ReportCreate, ReportUpdate


async def get_reports(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    reporter_id: Optional[str] = None,
    assigned_manager_id: Optional[str] = None,
    apartment_id: Optional[str] = None,
) -> Tuple[List[Report], int]:
    """Get reports with optional filtering."""
    query = select(Report)
    
    if status:
        query = query.where(Report.status == status)
    if priority:
        query = query.where(Report.priority == priority)
    if category:
        query = query.where(Report.category == category)
    if reporter_id:
        query = query.where(Report.reporter_id == reporter_id)
    if assigned_manager_id:
        query = query.where(Report.assigned_manager_id == assigned_manager_id)
    if apartment_id:
        query = query.where(Report.apartment_id == apartment_id)
    
    # Get total count
    count_query = select(func.count(Report.id)).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return list(items), total


async def get_report(db: AsyncSession, report_id: str) -> Optional[Report]:
    """Get a single report by ID."""
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    return result.scalar_one_or_none()


async def get_report_with_messages(db: AsyncSession, report_id: str) -> Optional[Report]:
    """Get report with messages loaded."""
    result = await db.execute(
        select(Report)
        .where(Report.id == report_id)
        .options(selectinload(Report.messages))
    )
    return result.scalar_one_or_none()


async def create_report(
    db: AsyncSession,
    report_data: ReportCreate,
    reporter_id: str
) -> Report:
    """Create a new report."""
    db_report = Report(
        reporter_id=reporter_id,
        apartment_id=report_data.apartment_id,
        building_id=report_data.building_id,
        title=report_data.title,
        description=report_data.description,
        category=report_data.category,
        priority=report_data.priority,
        photo_urls=report_data.photo_urls or [],
        status=ReportStatus.PENDING,
    )
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)
    return db_report


async def update_report(
    db: AsyncSession,
    report: Report,
    update_data: ReportUpdate
) -> Report:
    """Update a report."""
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(report, field, value)
    
    await db.commit()
    await db.refresh(report)
    return report


async def acknowledge_report(
    db: AsyncSession,
    report: Report,
    manager_id: str
) -> Report:
    """Acknowledge a report."""
    report.status = ReportStatus.ACKNOWLEDGED
    report.assigned_manager_id = manager_id
    await db.commit()
    await db.refresh(report)
    return report


async def reject_report(
    db: AsyncSession,
    report: Report,
    manager_id: str,
    reason: str
) -> Report:
    """Reject a report with reason."""
    report.status = ReportStatus.REJECTED
    report.assigned_manager_id = manager_id
    report.rejection_reason = reason
    await db.commit()
    await db.refresh(report)
    return report


async def resolve_report(db: AsyncSession, report: Report) -> Report:
    """Mark report as resolved."""
    report.status = ReportStatus.RESOLVED
    await db.commit()
    await db.refresh(report)
    return report


async def delete_report(db: AsyncSession, report: Report) -> Report:
    """Soft delete a report."""
    report.status = ReportStatus.DELETED
    await db.commit()
    await db.refresh(report)
    return report
